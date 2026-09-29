/* Forever Warlock leveling model: expected-value solo fight simulator.
 * Line-for-line port of models/leveling_sim.py and models/character.py.
 * tests/leveling_parity_test.js checks it against the Python on a grid of builds, levels and pets.
 * Deterministic expected values: hit and crit are folded into every tick, buffs apply live (no snapshotting).
 */
(function (root) {
  // ---------------------------------------------------------------- spell ranks (level, values...)
  const CORR = [[4, 11, 4, 35], [14, 14, 5, 55], [24, 23, 6, 100], [34, 29, 6, 160], [44, 41, 6, 225], [54, 58, 6, 290], [60, 74, 6, 340]];
  const CORR_SP = 0.2;
  const BOA = [[8, 7, 25], [18, 11, 50], [28, 15, 90], [38, 22, 130], [48, 34, 170], [58, 47, 215]];
  const BOA_SP = 0.133;
  const SB = [[1, 14, 1.7, 25, .486], [6, 26, 2.2, 40, .629], [12, 42, 2.8, 70, .8], [20, 57, 3, 110, .857],
    [28, 79, 3, 160, .857], [36, 102, 3, 210, .857], [44, 142, 3, 265, .857], [52, 192, 3, 315, .857], [60, 269, 3, 380, .857]];
  const DL = [[14, 11, 55], [22, 15, 85], [30, 23, 135], [38, 29, 185], [46, 40, 240], [54, 52, 300]];
  const DL_SP = 0.1;
  const SL = [[30, 12, 150], [38, 20, 205], [48, 30, 285], [58, 42, 365]];
  const SL_SP = 0.05;
  const DS = [[10, 18, 55], [24, 35, 125], [38, 55, 210], [52, 85, 290]];
  const DS_SP = 0.1;
  const LT = [[6, 30], [16, 75], [26, 140], [36, 220], [46, 310], [56, 430]];
  const WRACK = [40, 37, 200];
  const WRACK_SP = 0.143;
  const IMPDRAINS = { 0: 0, 1: .07, 2: .14, 3: .20 };
  const DT = 0.02;

  function rank(table, lvl) {
    let best = null;
    for (const row of table) if (row[0] <= lvl) best = row;
    return best;
  }

  // ---------------------------------------------------------------- character (models/character.py)
  const AFF = { ImprovedLifeTap: [0, 2], Suppression: [0, 5], ImprovedCorruption: [0, 5],
    Malediction: [1, 5], SoulHarvesting: [1, 2], ImprovedDrains: [1, 3],
    ImprovedBoA: [2, 2], FelConcentration: [2, 3], AmplifyCurse: [2, 1], Pandemic: [2, 3],
    Malevolence: [3, 5], Nightfall: [3, 2], CurseOfExhaustion: [3, 1],
    SiphonLife: [4, 1], SoulSiphon: [4, 3], ShadowMastery: [5, 5], Wrack: [6, 1] };
  const DEMO = { ImprovedHealthFunnel: [0, 2], ImprovedImp: [0, 3], DemonicEmbrace: [0, 5], UnholyPower: [0, 5],
    DemonicAegis: [1, 2], ImprovedVoidwalker: [1, 3], FelVitality: [1, 3], DemonicEnergies: [1, 2],
    ImprovedSayaad: [2, 3], DemonicSacrifice: [2, 1], MasterSummoner: [2, 2],
    Decimation: [3, 2], FelDomination: [3, 1], DemonicBrand: [3, 3],
    ImprovedFelhunter: [4, 3], SoulLink: [4, 1], DemonicKnowledge: [4, 3],
    MasterDemonologist: [5, 5], DemonicPact: [6, 1] };
  const PREREQ = { Wrack: ['SiphonLife', 1], SoulLink: ['DemonicSacrifice', 1], DemonicPact: ['SoulLink', 1], FelDomination: ['MasterSummoner', 2] };

  function valid(tal) {
    for (const tree of [AFF, DEMO]) {
      const rows = [0, 0, 0, 0, 0, 0, 0];
      for (const k in tree) {
        const [r, mx] = tree[k], p = tal[k] || 0;
        if (p < 0 || p > mx) return false;
        rows[r] += p;
      }
      for (let r = 0; r < 7; r++) {
        let below = 0; for (let i = 0; i < r; i++) below += rows[i];
        if (rows[r] && below < 5 * r) return false;
      }
    }
    for (const k in PREREQ) { const [req, n] = PREREQ[k]; if ((tal[k] || 0) && (tal[req] || 0) < n) return false; }
    return true;
  }

  const PET_BASE = { voidwalker: 0.5, succubus: 1.1, imp: 0.8, felhunter: 0.8, none: 0.0 };
  const PET_TAKEN = { voidwalker: 0.10, succubus: 1.0, imp: 1.0, felhunter: 1.0, none: 1.0 };

  function makeChar(L, tal, spPerLevel, pet) {
    spPerLevel = spPerLevel === undefined ? 1.0 : spPerLevel;
    pet = pet || 'voidwalker';
    const t = k => tal[k] || 0;
    let hp = 20 + 28 * L + 0.4 * L * L;
    let mana = 20 + 25 * L + 0.45 * L * L;
    hp *= 1 + 0.02 * t('DemonicEmbrace') * 0.65;
    mana *= 1 + 0.05 * t('FelVitality') * 0.7;
    let petDps = PET_BASE[pet] * L * (1 + .02 * t('UnholyPower'));
    let shadow = 1.0, felSac = false, vwSac = false;
    const pact = t('DemonicPact'), sac = tal._sac;
    if (sac && (pact || pet === 'none')) {
      if (sac === 'imp') shadow *= 1.15;
      if (sac === 'felhunter') felSac = true;
      if (sac === 'voidwalker') vwSac = true;
    }
    if (pet === 'succubus') shadow *= 1 + .02 * t('MasterDemonologist');
    if (t('SoulLink') && pet !== 'none') { shadow *= 1.03; petDps *= 1.03; }
    let taken = PET_TAKEN[pet];
    if (t('SoulLink') && pet !== 'none') taken *= 0.70;
    return { level: L, sp: spPerLevel * L, crit: 0.05, spirit: 15 + 1.2 * L, maxHp: hp, maxMana: mana,
      wandDps: 0.9 * L + 3, petDps, talents: tal, shadowMult: shadow, mobLevelDiff: 0,
      mobDps: 0.035 * L * L, takenFrac: taken, felhunterSac: felSac, voidwalkerSac: vwSac };
  }
  const mobHp = L => 18 * L + 0.62 * L * L;

  const POLICIES = [
    ['DoTs+DrainLife', ['Corruption', 'BoA', 'SiphonLife', 'DrainLife']],
    ['DoTs+Wrack+DL', ['Corruption', 'BoA', 'SiphonLife', 'Wrack', 'DrainLife']],
    ['DoTs+ShadowBolt', ['Corruption', 'BoA', 'SiphonLife', 'ShadowBolt']],
    ['DoTs+Wand', ['Corruption', 'BoA', 'SiphonLife', 'Wand']],
    ['Corr+SL+DrainLife', ['Corruption', 'SiphonLife', 'DrainLife']],
    ['Corr+SL+Wand', ['Corruption', 'SiphonLife', 'Wand']],
    ['Corr+SL+SB', ['Corruption', 'SiphonLife', 'ShadowBolt']],
    ['Corr+BoA+DrainLife', ['Corruption', 'BoA', 'DrainLife']],
    ['Corr+BoA+Wand', ['Corruption', 'BoA', 'Wand']],
    ['Corr+DrainLife', ['Corruption', 'DrainLife']],
    ['Corr+Wand', ['Corruption', 'Wand']],
  ];

  // ---------------------------------------------------------------- simulator (models/leveling_sim.py)
  function simulate(ch, mobHpV, policy, maxTime) {
    maxTime = maxTime === undefined ? 240.0 : maxTime;
    const T = k => ch.talents[k] || 0;
    const lvl = ch.level;
    const sp = ch.sp + ch.level * T('DemonicKnowledge') / 3.0;
    const hit = Math.min(.99, { 0: .96, 1: .95, 2: .94, 3: .83 }[ch.mobLevelDiff] + .01 * T('Suppression'));
    const sm = 1 + .01 * T('ShadowMastery');
    const mal = 1 + .01 * T('Malediction');
    const crit = ch.crit + .01 * T('Malevolence');
    const pand = 1.5 + 0.5 * T('Pandemic') / 3.0;
    const evcDot = 1 + crit * (pand - 1);
    const evcSb = 1 + crit * 0.5;
    const corr = rank(CORR, lvl), boa = rank(BOA, lvl), sb = rank(SB, lvl), dl = rank(DL, lvl), ds = rank(DS, lvl);
    const sl = T('SiphonLife') ? rank(SL, lvl) : null;
    const wrackOk = !!T('Wrack') && lvl >= 40;
    const lt = rank(LT, lvl);
    const nf = .02 * T('Nightfall');
    const sbHit = (sb[1] + sb[4] * sp) * sm * ch.shadowMult * evcSb * hit;

    const S = { mana_spent: 0.0, lt_mana: 0.0, hp_spent: 0.0, healed: 0.0, casts: {}, dmg: {}, hp_taken: 0 };
    const st = { hp: mobHpV, t: 0.0, mana: ch.maxMana, php: ch.maxHp, wrack_until: -1.0,
      amp: !!policy.amp && !!T('AmplifyCurse'), nfc: 0, gcd: 0, wand: false };
    const dots = new Map();
    let chan = null, cast = null;

    const dmg = (name, x) => { st.hp -= x; S.dmg[name] = (S.dmg[name] || 0) + x; };
    const heal = x => { st.php = Math.min(ch.maxHp, st.php + x); S.healed += x; };
    const nAffl = () => Math.min(3, ['Corruption', 'BoA', 'SiphonLife'].filter(k => dots.has(k)).length);
    const dotMult = name => {
      let m = sm * mal * ch.shadowMult * evcDot * hit;
      if (name === 'Corruption') m *= 1 + .02 * T('ImprovedCorruption');
      if (name === 'BoA') m *= 1 + .05 * T('ImprovedBoA');
      if (st.t < st.wrack_until) m *= 1.10;
      return m;
    };
    const drainMult = () => sm * mal * ch.shadowMult * evcDot * hit * (1 + IMPDRAINS[T('ImprovedDrains')]) * (1 + .04 * T('SoulSiphon') * nAffl());
    const spend = (name, cost) => { st.mana -= cost; S.mana_spent += cost; S.casts[name] = (S.casts[name] || 0) + 1; };
    const lifeTap = () => {
      const amt = lt[1] + ch.spirit;
      st.php -= amt; S.hp_spent += amt;
      const gain = amt * (1 + .10 * T('ImprovedLifeTap'));
      st.mana += gain; S.lt_mana += gain;
      S.casts.LifeTap = (S.casts.LifeTap || 0) + 1;
    };
    const applyDot = name => {
      if (name === 'Corruption') dots.set(name, { next: st.t + 3, left: corr[2], per: corr[1] + CORR_SP * sp, period: 3 });
      else if (name === 'BoA') {
        let amp = 1.0;
        if (st.amp) { amp = 1.5; st.amp = false; }
        dots.set(name, { next: st.t + 2, left: 12, per: (boa[1] + BOA_SP * sp) * amp, period: 2, n: 0 });
      } else if (name === 'SiphonLife') dots.set(name, { next: st.t + 3, left: 10, per: sl[1] + SL_SP * sp, period: 3 });
    };

    while (st.hp > 0 && st.t < maxTime) {
      const t = st.t;
      for (const name of [...dots.keys()]) {
        const d = dots.get(name);
        if (t >= d.next - 1e-9) {
          let per = d.per;
          if ('n' in d) { d.n += 1; per *= d.n <= 4 ? 0.5 : (d.n <= 8 ? 1.0 : 1.5); }
          const x = per * dotMult(name);
          dmg(name, x);
          if (name === 'SiphonLife') heal(x);
          if (name === 'Corruption' && nf) st.nfc += nf;
          d.left -= 1; d.next += d.period;
          if (d.left <= 0) dots.delete(name);
        }
      }
      if (chan && t >= chan.next - 1e-9) {
        const x = chan.per * drainMult();
        dmg(chan.name, x);
        if (chan.name === 'DrainLife') heal(x);
        if (nf) st.nfc += nf;
        chan.left -= 1; chan.next += chan.period;
        if (chan.left <= 0) chan = null;
      }
      if (cast && t >= cast.end - 1e-9) { cast.fn(); cast = null; }
      dmg('Pet', ch.petDps * DT);
      st.php -= ch.mobDps * ch.takenFrac * DT;
      S.hp_taken += ch.mobDps * ch.takenFrac * DT;
      if (ch.felhunterSac) heal(0.03 * ch.maxHp / 4 * DT);
      if (ch.voidwalkerSac) st.mana = Math.min(ch.maxMana * 2, st.mana + 0.02 * ch.maxMana / 4 * DT);
      const busy = chan !== null || cast !== null;
      if (st.wand && !busy) dmg('Wand', ch.wandDps * DT * hit);
      if (!busy && t >= st.gcd - 1e-9 && st.hp > 0) {
        let a = choose(policy, ch, dots, st, mobHpV, corr, boa, sl, dl, ds, sb, wrackOk);
        if (st.nfc >= 1 && st.mana >= sb[3] && !['Corruption', 'BoA', 'SiphonLife'].includes(a)) a = 'NightfallSB';
        if (a !== 'Wand') { st.wand = false; st.gcd = t + 1.5; }
        if (a === 'LifeTap') lifeTap();
        else if (a === 'Corruption') {
          spend(a, corr[3]);
          const ct = Math.max(0.0, 2.0 - 0.4 * T('ImprovedCorruption'));
          if (ct > 0) cast = { end: t + ct, fn: () => applyDot('Corruption') }; else applyDot('Corruption');
        } else if (a === 'BoA') { spend(a, boa[2]); applyDot('BoA'); }
        else if (a === 'SiphonLife') { spend(a, sl[2]); applyDot('SiphonLife'); }
        else if (a === 'DrainLife') { spend(a, dl[2]); chan = { name: 'DrainLife', next: t + 1, left: 5, period: 1, per: dl[1] + DL_SP * sp }; }
        else if (a === 'DrainSoul') { spend(a, ds[2]); chan = { name: 'DrainSoul', next: t + 3, left: 5, period: 3, per: ds[1] + DS_SP * sp }; }
        else if (a === 'Wrack') { spend(a, WRACK[2]); chan = { name: 'Wrack', next: t + 1, left: 6, period: 1, per: WRACK[1] + WRACK_SP * sp }; st.wrack_until = t + 6; }
        else if (a === 'ShadowBolt') {
          spend(a, sb[3]);
          const ct = Math.max(1.5, sb[2] - 0.1 * T('Bane'));
          cast = { end: t + ct, fn: () => dmg('ShadowBolt', sbHit) };
        } else if (a === 'NightfallSB') { st.nfc -= 1; spend('ShadowBolt', sb[3]); dmg('Nightfall', sbHit); }
        else if (a === 'Wand') st.wand = true;
      }
      st.t += DT;
    }
    S.ttk = st.t; S.end_mana = st.mana; S.end_hp = st.php;
    S.net_mana = st.mana - ch.maxMana; S.net_hp = st.php - ch.maxHp;
    return S;
  }

  function choose(policy, ch, dots, st, mobHpV, corr, boa, sl, dl, ds, sb, wrackOk) {
    const T = k => ch.talents[k] || 0;
    const frac = st.hp / mobHpV;
    const ltRow = rank(LT, ch.level);
    const ltGain = (ltRow[1] + ch.spirit) * (1 + .10 * T('ImprovedLifeTap'));
    if (st.php - (ltRow[1] + ch.spirit) > (policy.tap_above === undefined ? 0.75 : policy.tap_above) * ch.maxHp && st.mana + ltGain <= ch.maxMana) return 'LifeTap';
    const ltOk = st.php > (policy.lt_hp_floor === undefined ? 0.35 : policy.lt_hp_floor) * ch.maxHp;
    const mana = st.mana;
    for (const step of policy.prio) {
      let cost = null;
      if (step === 'Corruption') {
        if (!corr || dots.has('Corruption') || frac <= (policy.corr_min === undefined ? 0.15 : policy.corr_min)) continue;
        cost = corr[3];
      } else if (step === 'BoA') {
        if (!boa || dots.has('BoA') || frac <= (policy.boa_min === undefined ? 0.5 : policy.boa_min)) continue;
        cost = boa[2];
      } else if (step === 'SiphonLife') {
        if (!sl || dots.has('SiphonLife') || frac <= (policy.sl_min === undefined ? 0.4 : policy.sl_min)) continue;
        cost = sl[2];
      } else if (step === 'Wrack') {
        if (!wrackOk || frac <= 0.25 || dots.size < 2) continue;
        cost = WRACK[2];
      } else if (step === 'DrainLife') {
        if (!dl) continue;
        cost = dl[2];
      } else if (step === 'DrainSoul') {
        if (frac > (policy.ds_below === undefined ? 0.25 : policy.ds_below)) continue;
        cost = ds[2];
      } else if (step === 'ShadowBolt') cost = sb[3];
      else if (step === 'Wand') return 'Wand';
      if (mana >= cost) return step;
      if (ltOk) return 'LifeTap';
      return 'Wand';
    }
    return 'Wand';
  }

  function secondsPerKill(ch, mobHpV, policy, travel) {
    travel = travel === undefined ? 8.0 : travel;
    const L = ch.level;
    const k = 1 + .10 * (ch.talents.ImprovedLifeTap || 0);
    const restRate = 2.2 * L + 1.2 * L * k;
    const regenRate = (8 + ch.spirit / 4) / 2 + ch.spirit / 5 * k * 0.5;
    const s = simulate(ch, mobHpV, policy);
    const net = s.net_mana + k * s.net_hp + regenRate * travel;
    s.rest = Math.max(0.0, -net) / restRate;
    s.spk = s.ttk + travel + s.rest;
    return s;
  }

  // Best rotation for a build: the policy with the lowest seconds per kill (first wins ties, as in Python).
  // opts.aggro: the pet holds the mob like a Voidwalker (a Demonic Brand scenario, not the default).
  function evaluate(L, tal, pet, spPerLevel, opts) {
    opts = opts || {};
    let best = null;
    for (const [name, prio] of POLICIES) {
      const ch = makeChar(L, tal, spPerLevel, pet);
      if (opts.aggro && pet !== 'voidwalker' && pet !== 'none') ch.takenFrac = 0.10 * ((tal.SoulLink && pet !== 'none') ? 0.70 : 1.0);
      const s = secondsPerKill(ch, mobHp(L), { prio, amp: false });
      if (best === null || s.spk < best.spk) { best = s; best.policy = name; }
    }
    return best;
  }

  const api = { rank, valid, makeChar, mobHp, simulate, secondsPerKill, evaluate, POLICIES, AFF, DEMO, PREREQ };
  if (typeof module !== 'undefined') module.exports = api; else root.LevelingModel = api;
})(this);
