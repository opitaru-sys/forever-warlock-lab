/* Forever Warlock leveling model: expected-value solo fight simulator.
 * Line-for-line port of models/leveling_sim.py and models/character.py.
 * tests/leveling_parity_test.js checks it against the Python on a grid of builds, levels and pets.
 * Deterministic expected values: hit and crit are folded into every tick, buffs apply live (no snapshotting),
 * short procs (Improved Shadow Bolt, Shadow and Flame) enter as the chance they are up.
 */
(function (root) {
  // ---------------------------------------------------------------- spell ranks (level, values...), client base points
  // v8.4: level 60 uses the trainer's ranks. Shadow Bolt 10, Corruption 7 and Immolate 8 were taught only by books
  // from Ruins of Ahn'Qiraj in Classic, with no Forever source yet, so Corruption rank 6 carries at 60.
  const CORR = [[4, 10, 4, 35], [14, 13, 5, 55], [24, 22, 6, 100], [34, 28, 6, 160], [44, 40, 6, 225], [54, 57, 6, 290]];
  const CORR_SP = 0.2;
  const BOA = [[8, 6, 25], [18, 10, 50], [28, 14, 90], [38, 21, 130], [48, 33, 170], [58, 46, 215]];
  const BOA_SP = 0.133;
  const DL = [[14, 10, 55], [22, 14, 85], [30, 22, 135], [38, 28, 185], [46, 39, 240], [54, 51, 300]];
  const DL_SP = 0.1;
  const SL = [[30, 11, 150], [38, 19, 205], [48, 29, 285], [58, 41, 365]];
  const SL_SP = 0.05;
  const DS = [[10, 17, 55], [24, 34, 125], [38, 54, 210], [52, 84, 290]];
  const DS_SP = 0.1;
  const WRACK = [40, 36, 200];
  const WRACK_SP = 0.143;
  const IMPDRAINS = { 0: 0, 1: .07, 2: .14, 3: .20 };
  const LT = [[6, 30, 16], [16, 75, 26], [26, 140, 36], [36, 220, 46], [46, 310, 56], [56, 430, 66]];
  // direct damage: the last two fields are EffectRealPointsPerLevel and the rank's MaxLevel (ddAvg)
  const SB = [[1, 13, 1.7, 25, .486, .3, 5], [6, 25, 2.2, 40, .629, .6, 11], [12, 41, 2.8, 70, .8, .7, 17],
    [20, 56, 3, 110, .857, .9, 25], [28, 78, 3, 160, .857, 1.2, 33], [36, 101, 3, 210, .857, 1.2, 41],
    [44, 141, 3, 265, .857, 1.4, 49], [52, 191, 3, 315, .857, 1.6, 57], [60, 251, 3, 370, .857, 1.8, 65]];
  const IMM = [[1, 8, 25, 3, .7, 5], [10, 17, 45, 6, .8, 15], [20, 32, 90, 12, 1.2, 25], [30, 56, 155, 19, 1.5, 35],
    [40, 72, 220, 25, 1.6, 45], [50, 106, 295, 38, 1.9, 55], [60, 146, 370, 52, 2.3, 65]];
  const IMM_SP = 0.2, IMM_TICK_SP = 0.13, IMM_CAST = 2.0;
  const SEAR = [[18, 23, 45, .6, 24], [26, 33, 68, .7, 32], [34, 44, 91, .8, 40], [42, 62, 118, .9, 48], [50, 85, 141, 1.0, 56], [58, 114, 168, 1.2, 64]];
  const CONF = [[25, 95, 100, .9, 30], [32, 122, 130, .9, 38], [40, 146, 165, 1.0, 46], [48, 194, 200, 1.1, 54], [54, 239, 230, 1.2, 60], [60, 282, 255, 1.3, 66]];
  const BURN = [[20, 66, 105, .9, 24], [24, 80, 130, 1.0, 30], [32, 118, 190, 1.3, 38], [40, 148, 245, 1.3, 46], [48, 203, 305, 1.6, 54], [56, 266, 365, 1.8, 62]];
  const INCIN = [[40, 97, 205, 1.1, 49], [50, 145, 265, 1.3, 59], [60, 217, 325, 1.4, 69]];
  const SOULFIRE = [[48, 377, 305, 1.7, 54], [56, 431, 335, 1.9, 62]];
  const DCOIL = [[42, 272, 435, 2.2, 48], [50, 359, 525, 2.6, 56], [58, 454, 600, 3.0, 64]];
  const COE = [[20, .04, 50], [30, .06, 100], [40, .08, 150], [50, .10, 200]];
  const SEAR_SP = 0.429, CONF_SP = 0.429, BURN_SP = 0.429;
  const INCIN_SP = 0.714, SOULFIRE_SP = 1.0, DCOIL_SP = 0.214;
  // talent per-rank values (src/builder.js)
  const CATA = [0, .03, .07, .10], AFLAMES = [0, .03, .07, .10], FNB = [0, .08, .17, .25], SH_BONUS = [0, .5, 1.0];
  const BASE_HIT = { 0: .96, 1: .95, 2: .94, 3: .83 };
  const ISB_DUR = 12.0, SNF_DUR = 20.0;
  const DT = 0.02;

  function rank(table, lvl) {
    let best = null;
    for (const row of table) if (row[0] <= lvl) best = row;
    return best;
  }
  // 'base': client base points; 'scaled': + per-level points up to MaxLevel (in game); 'wowhead': at MaxLevel (tooltips)
  function ddAvg(row, lvl, mode) {
    const per = row[row.length - 2], top = row[row.length - 1];
    if (mode === 'scaled') return row[1] + per * Math.max(0, Math.min(lvl, top) - row[0]);
    if (mode === 'wowhead') return row[1] + per * (top - row[0]);
    return row[1];
  }
  function ltHealth(row, lvl, mode) {
    if (mode === 'scaled') return row[1] - Math.max(0, row[2] - lvl);
    return row[1];
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
  const DESTRO = { DestructiveReach: [0, 2], ImprovedShadowBolt: [0, 5], Bane: [0, 5],
    MoltenSkin: [1, 5], Cataclysm: [1, 3], Aftermath: [1, 5],
    Ruin: [2, 5], Shadowburn: [2, 1],
    Intensity: [3, 3], AgonizingFlames: [3, 3], Conflagrate: [3, 1],
    Pyroclasm: [4, 2], BaneOfHavoc: [4, 1], FireAndBrimstone: [4, 3],
    ShadowAndFlame: [5, 5], Incinerate: [6, 1] };
  const PREREQ = { Wrack: ['SiphonLife', 1], SoulLink: ['DemonicSacrifice', 1], DemonicPact: ['SoulLink', 1], FelDomination: ['MasterSummoner', 2],
    Pyroclasm: ['Intensity', 3], FireAndBrimstone: ['Conflagrate', 1], Incinerate: ['BaneOfHavoc', 1] };

  function valid(tal) {
    for (const tree of [AFF, DEMO, DESTRO]) {
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

  // lashShare: the share of Succubus damage that is Lash of Pain (Improved Sayaad), unknown, assumed 0.4
  function makeChar(L, tal, spPerLevel, pet, lashShare) {
    spPerLevel = spPerLevel === undefined ? 1.0 : spPerLevel;
    pet = pet || 'voidwalker';
    lashShare = lashShare === undefined ? 0.4 : lashShare;
    const t = k => tal[k] || 0;
    let hp = 20 + 28 * L + 0.4 * L * L;
    let mana = 20 + 25 * L + 0.45 * L * L;
    hp *= 1 + 0.02 * t('DemonicEmbrace') * 0.65;
    mana *= 1 + 0.05 * t('FelVitality') * 0.7;
    let petDps = PET_BASE[pet] * L * (1 + .02 * t('UnholyPower'));
    if (pet === 'imp') petDps *= 1 + .10 * t('ImprovedImp');
    if (pet === 'succubus') petDps *= 1 + .10 * t('ImprovedSayaad') * lashShare;
    let shadow = 1.0, fire = 1.0, felSac = false, vwSac = false;
    const pact = t('DemonicPact'), sac = tal._sac;
    if (sac && (pact || pet === 'none')) {
      if (sac === 'imp') shadow *= 1.15;
      if (sac === 'succubus') fire *= 1.15;
      if (sac === 'felhunter') felSac = true;
      if (sac === 'voidwalker') vwSac = true;
    }
    if (pet === 'succubus') shadow *= 1 + .02 * t('MasterDemonologist');
    if (pet === 'imp') fire *= 1 + .02 * t('MasterDemonologist');
    if (t('SoulLink') && pet !== 'none') { shadow *= 1.03; fire *= 1.03; petDps *= 1.03; }
    const taken = PET_TAKEN[pet];
    return { level: L, sp: spPerLevel * L, crit: 0.05, spirit: 15 + 1.2 * L, maxHp: hp, maxMana: mana,
      wandDps: 0.9 * L + 3, petDps, talents: tal, shadowMult: shadow, fireMult: fire, mobLevelDiff: 0,
      mobDps: 0.035 * L * L, takenFrac: taken * takenScale(tal, pet), felhunterSac: felSac, voidwalkerSac: vwSac,
      ddMode: 'base', suppAll: true };
  }
  // Soul Link sends 30% of your damage taken to the demon; Molten Skin takes 2% a point off the rest
  function takenScale(tal, pet) {
    const s = (tal.SoulLink && pet !== 'none') ? 0.70 : 1.0;
    return s * (1 - .02 * (tal.MoltenSkin || 0));
  }
  const mobHp = L => 18 * L + 0.62 * L * L;

  // base rotations, simplest first (on a tie the first name wins); evaluate() adds the modifiers on the best few
  const POLICIES = [
    ['Corr+Wand', ['Corruption', 'Wand']],
    ['Corr+DrainLife', ['Corruption', 'DrainLife']],
    ['Corr+SB', ['Corruption', 'ShadowBolt']],
    ['Corr+SP', ['Corruption', 'SearingPain']],
    ['Corr+BoA+Wand', ['Corruption', 'BoA', 'Wand']],
    ['Corr+BoA+DrainLife', ['Corruption', 'BoA', 'DrainLife']],
    ['Corr+BoA+SB', ['Corruption', 'BoA', 'ShadowBolt']],
    ['Corr+BoA+SP', ['Corruption', 'BoA', 'SearingPain']],
    ['Corr+SL+Wand', ['Corruption', 'SiphonLife', 'Wand']],
    ['Corr+SL+DrainLife', ['Corruption', 'SiphonLife', 'DrainLife']],
    ['Corr+SL+SB', ['Corruption', 'SiphonLife', 'ShadowBolt']],
    ['Corr+SL+SP', ['Corruption', 'SiphonLife', 'SearingPain']],
    ['DoTs+Wand', ['Corruption', 'BoA', 'SiphonLife', 'Wand']],
    ['DoTs+DrainLife', ['Corruption', 'BoA', 'SiphonLife', 'DrainLife']],
    ['DoTs+ShadowBolt', ['Corruption', 'BoA', 'SiphonLife', 'ShadowBolt']],
    ['DoTs+SP', ['Corruption', 'BoA', 'SiphonLife', 'SearingPain']],
    ['DoTs+Wrack+DL', ['Corruption', 'BoA', 'SiphonLife', 'Wrack', 'DrainLife']],
    ['Imm+Wand', ['Immolate', 'Conflagrate', 'Wand']],
    ['Imm+DrainLife', ['Immolate', 'Conflagrate', 'DrainLife']],
    ['Imm+SB', ['Immolate', 'Conflagrate', 'ShadowBolt']],
    ['Imm+SP', ['Immolate', 'Conflagrate', 'SearingPain']],
    ['Imm+Incin', ['Immolate', 'Conflagrate', 'Incinerate']],
    ['Corr+Imm+Wand', ['Corruption', 'Immolate', 'Conflagrate', 'Wand']],
    ['Corr+Imm+DrainLife', ['Corruption', 'Immolate', 'Conflagrate', 'DrainLife']],
    ['Corr+Imm+SB', ['Corruption', 'Immolate', 'Conflagrate', 'ShadowBolt']],
    ['Corr+Imm+SP', ['Corruption', 'Immolate', 'Conflagrate', 'SearingPain']],
    ['Corr+Imm+Incin', ['Corruption', 'Immolate', 'Conflagrate', 'Incinerate']],
    ['Corr+BoA+Imm+Wand', ['Corruption', 'BoA', 'Immolate', 'Conflagrate', 'Wand']],
    ['Corr+BoA+Imm+DrainLife', ['Corruption', 'BoA', 'Immolate', 'Conflagrate', 'DrainLife']],
    ['Corr+BoA+Imm+SB', ['Corruption', 'BoA', 'Immolate', 'Conflagrate', 'ShadowBolt']],
    ['Corr+BoA+Imm+SP', ['Corruption', 'BoA', 'Immolate', 'Conflagrate', 'SearingPain']],
    ['Corr+BoA+Imm+Incin', ['Corruption', 'BoA', 'Immolate', 'Conflagrate', 'Incinerate']],
    ['DoTs+Imm+Wand', ['Corruption', 'BoA', 'SiphonLife', 'Immolate', 'Conflagrate', 'Wand']],
    ['DoTs+Imm+DrainLife', ['Corruption', 'BoA', 'SiphonLife', 'Immolate', 'Conflagrate', 'DrainLife']],
    ['DoTs+Imm+SB', ['Corruption', 'BoA', 'SiphonLife', 'Immolate', 'Conflagrate', 'ShadowBolt']],
    ['DoTs+Imm+SP', ['Corruption', 'BoA', 'SiphonLife', 'Immolate', 'Conflagrate', 'SearingPain']],
    ['DoTs+Imm+Incin', ['Corruption', 'BoA', 'SiphonLife', 'Immolate', 'Conflagrate', 'Incinerate']],
    ['DoTs+Imm+Wrack+DL', ['Corruption', 'BoA', 'SiphonLife', 'Immolate', 'Conflagrate', 'Wrack', 'DrainLife']],
  ];

  // ---------------------------------------------------------------- simulator (models/leveling_sim.py)
  const AFF_DOTS = ['Corruption', 'BoA', 'SiphonLife'];
  const FILLERS = ['Wand', 'DrainLife', 'ShadowBolt', 'SearingPain', 'Incinerate', 'Wrack'];
  const CHANNELS = ['DrainLife', 'DrainSoul', 'Wrack'];
  const INSTANTS = ['Conflagrate', 'Shadowburn', 'DeathCoil'];
  const NO_NIGHTFALL = AFF_DOTS.concat(['Immolate', 'CoE', 'Conflagrate', 'Shadowburn', 'SoulFire', 'DeathCoil']);
  const charHit = ch => Math.min(.99, BASE_HIT[ch.mobLevelDiff] + .01 * (ch.talents.Suppression || 0));
  // the client's Suppression has no spell family mask; suppAll false is the Classic reading (Affliction only)
  const charHitDestro = ch => (ch.suppAll === false ? Math.min(.99, BASE_HIT[ch.mobLevelDiff]) : charHit(ch));

  function fullPrio(policy) {
    const prio = policy.prio.slice();
    let i = prio.findIndex(s => FILLERS.includes(s));
    if (i < 0) i = prio.length;
    const mods = (policy.dc ? ['DeathCoil'] : []).concat(policy.fin ? [policy.fin] : []);
    return (policy.coe ? ['CoE'] : []).concat(prio.slice(0, i), mods, prio.slice(i));
  }

  function fightRanks(ch) {
    const L = ch.level, T = k => ch.talents[k] || 0;
    return { corr: rank(CORR, L), boa: rank(BOA, L), sb: rank(SB, L), dl: rank(DL, L), ds: rank(DS, L),
      imm: rank(IMM, L), lt: rank(LT, L), sear: rank(SEAR, L), coe: rank(COE, L), dc: rank(DCOIL, L),
      sl: T('SiphonLife') ? rank(SL, L) : null, conf: T('Conflagrate') ? rank(CONF, L) : null,
      burn: T('Shadowburn') ? rank(BURN, L) : null, incin: T('Incinerate') ? rank(INCIN, L) : null,
      sf: T('Decimation') ? rank(SOULFIRE, L) : null, wrack: (T('Wrack') && L >= 40) ? WRACK : null };
  }

  // the steps of a priority list this character can cast, without a trailing wand; evaluate() skips repeats
  function usableSteps(prio, ch) {
    const r = fightRanks(ch);
    const have = { Corruption: r.corr, BoA: r.boa, SiphonLife: r.sl, Wrack: r.wrack, DrainLife: r.dl, DrainSoul: r.ds,
      ShadowBolt: r.sb, Immolate: r.imm, Conflagrate: r.conf, SearingPain: r.sear, Incinerate: r.incin, Wand: true };
    const steps = prio.filter(s => have[s]);
    while (steps.length && steps[steps.length - 1] === 'Wand') steps.pop();
    return steps;
  }

  function fightMults(ch) {
    const T = k => ch.talents[k] || 0;
    const critS = ch.crit + .01 * T('Malevolence'), critF = ch.crit;
    const ruin = 1.5 + .1 * T('Ruin');
    const pand = 1.5 + 0.5 * T('Pandemic') / 3.0;
    const af = AFLAMES[T('AgonizingFlames')];
    const hitD = charHitDestro(ch);
    return { hit: charHit(ch), hit_d: hitD, sm: 1 + .01 * T('ShadowMastery'), mal: 1 + .01 * T('Malediction'),
      af: 1 + af, cata: 1 - CATA[T('Cataclysm')], after: 1 + .1 * T('Aftermath'),
      evc_dot: 1 + critS * (pand - 1),
      evc_sd: 1 + critS * (ruin - 1),
      evc_fd: 1 + critF * (ruin - 1),
      evc_sear: 1 + (critF + af) * (ruin - 1),
      evc_conf: 1 + (critF + FNB[T('FireAndBrimstone')]) * (ruin - 1),
      evc_dc: 1 + critS * 0.5,
      isb: .04 * T('ImprovedShadowBolt'), isb_p: hitD * critS,
      snf: .02 * T('ShadowAndFlame'), keep: .2 * T('ShadowAndFlame') };
  }

  const at = (row, i, mult) => (row ? row[i] * (mult === undefined ? 1.0 : mult) : 0.0);

  function fightCosts(k) {
    const cata = k.cata;
    return { Corruption: at(k.corr, 3), BoA: at(k.boa, 2), SiphonLife: at(k.sl, 2),
      DrainLife: at(k.dl, 2), DrainSoul: at(k.ds, 2), Wrack: at(k.wrack, 2),
      CoE: at(k.coe, 2), ShadowBolt: at(k.sb, 3, cata), Immolate: at(k.imm, 2, cata),
      SearingPain: at(k.sear, 2, cata), Conflagrate: at(k.conf, 2, cata),
      Shadowburn: at(k.burn, 2, cata), Incinerate: at(k.incin, 2, cata),
      SoulFire: at(k.sf, 2, cata * k.p_sf), DeathCoil: at(k.dc, 2, k.p_dc), Wand: 0.0 };
  }

  function fightCasts(k, bane, ic) {
    const sf = Math.max(1.5, (6.0 - .4 * bane) * 0.6);
    return { Corruption: Math.max(0.0, 2.0 - 0.4 * ic), ShadowBolt: Math.max(1.5, k.sb[2] - .1 * bane),
      Immolate: Math.max(1.5, IMM_CAST - .1 * bane), SearingPain: 1.5, Incinerate: Math.max(1.5, 2.5 - .1 * bane),
      SoulFire: sf * k.p_sf };
  }

  function fightHits(k, L, mode) {
    const sp = k.sp, af = k.af, hitD = k.hit_d;
    const part = (row, coef) => (row ? ddAvg(row, L, mode) + coef * sp : 0.0);
    return {
      ShadowBolt: part(k.sb, k.sb[4]) * af * k.evc_sd * hitD,
      Shadowburn: part(k.burn, BURN_SP) * af * k.evc_sd * hitD,
      Immolate: part(k.imm, IMM_SP) * af * k.after * k.evc_fd * hitD,
      ImmolateTick: (k.imm[3] + IMM_TICK_SP * sp) * af * k.mal * k.evc_fd * hitD,
      SearingPain: part(k.sear, SEAR_SP) * af * k.evc_sear * hitD,
      Conflagrate: part(k.conf, CONF_SP) * af * k.evc_conf * hitD,
      Incinerate: part(k.incin, INCIN_SP) * af * k.evc_fd * hitD,
      SoulFire: part(k.sf, SOULFIRE_SP) * af * k.evc_fd * hitD * k.p_sf,
      DeathCoil: part(k.dc, DCOIL_SP) * k.evc_dc * k.hit * k.p_dc };
  }

  function fightConsts(ch, policy) {
    const L = ch.level, T = k => ch.talents[k] || 0, mode = ch.ddMode || 'base';
    const k = Object.assign(fightRanks(ch), fightMults(ch));
    k.sp = ch.sp + ch.level * T('DemonicKnowledge') / 3.0;
    k.prio = fullPrio(policy);
    k.p_amp = T('AmplifyCurse') ? (policy.p_amp === undefined ? (policy.amp ? 1.0 : 0.0) : policy.p_amp) : 0.0;
    k.p_dc = policy.p_dc === undefined ? 1.0 : policy.p_dc;
    k.p_sf = policy.p_sf === undefined ? 1.0 : policy.p_sf;
    k.lt_amt = k.lt ? ltHealth(k.lt, L, mode) + ch.spirit : 0.0;    // Life Tap is learned at level 6
    k.ilt = 1 + .10 * T('ImprovedLifeTap');
    k.nf = .02 * T('Nightfall');
    k.dec = !!T('Decimation');
    k.sf_cd = 60 * (1 - .45 * T('Decimation'));
    k.coe_mult = k.coe ? 1 + k.coe[1] * k.hit : 1.0;
    k.cost = fightCosts(k);
    k.ct = fightCasts(k, T('Bane'), T('ImprovedCorruption'));
    k.base = fightHits(k, L, mode);
    return k;
  }

  function simulate(ch, mobHpV, policy, maxTime) {
    maxTime = maxTime === undefined ? 240.0 : maxTime;
    const k = fightConsts(ch, policy);
    const T = n => ch.talents[n] || 0;
    const S = { mana_spent: 0.0, lt_mana: 0.0, hp_spent: 0.0, healed: 0.0, casts: {}, dmg: {}, hp_taken: 0.0, ds_kill: false };
    const st = { hp: mobHpV, t: 0.0, mana: ch.maxMana, php: ch.maxHp, wrack_until: -1.0, nfc: 0.0, gcd: 0.0, wand: false,
      amp: k.p_amp, coe: 1.0, coe_on: false, cd: { Conflagrate: 0.0, Shadowburn: 0.0, SoulFire: 0.0 },
      dec_until: -1.0, dc_done: false };
    const dots = new Map();
    let chan = null, cast = null;
    const procs = { isb: [], snf_s: [], snf_f: [] };

    const dmg = (name, x) => { st.hp -= x; S.dmg[name] = (S.dmg[name] || 0) + x; };
    const heal = x => { st.php = Math.min(ch.maxHp, st.php + x); S.healed += x; };
    const pUp = (evs, dur) => {
      let q = 1.0;
      for (const [t0, p] of evs) if (t0 <= st.t && st.t < t0 + dur) q *= 1 - p;
      return 1 - q;
    };
    const shadowNow = () => {
      let m = k.sm * ch.shadowMult * st.coe;
      if (k.isb) m *= 1 + k.isb * pUp(procs.isb, ISB_DUR);
      if (k.snf) m *= 1 + k.snf * pUp(procs.snf_s, SNF_DUR);
      return m;
    };
    const fireNow = () => {
      let m = ch.fireMult * st.coe;
      if (k.snf) m *= 1 + k.snf * pUp(procs.snf_f, SNF_DUR);
      return m;
    };
    const nAffl = () => Math.min(3, AFF_DOTS.filter(d => dots.has(d)).length);
    const dotMult = name => {
      let m = shadowNow() * k.mal * k.evc_dot * k.hit;
      if (name === 'Corruption') m *= 1 + .02 * T('ImprovedCorruption');
      if (name === 'BoA') m *= 1 + .05 * T('ImprovedBoA');
      if (st.t < st.wrack_until) m *= 1.10;
      return m;
    };
    const drainMult = () => shadowNow() * k.mal * k.evc_dot * k.hit * (1 + IMPDRAINS[T('ImprovedDrains')]) * (1 + .04 * T('SoulSiphon') * nAffl());
    const spend = (name, cost) => { st.mana -= cost; S.mana_spent += cost; S.casts[name] = (S.casts[name] || 0) + 1; };
    const lifeTap = () => {
      const amt = k.lt_amt;
      st.php -= amt; S.hp_spent += amt;
      const gain = amt * k.ilt;
      st.mana += gain; S.lt_mana += gain;
      S.casts.LifeTap = (S.casts.LifeTap || 0) + 1;
    };
    const applyDot = name => {
      const t = st.t, sp = k.sp;
      if (name === 'Corruption') dots.set(name, { next: t + 3, left: k.corr[2], per: k.corr[1] + CORR_SP * sp, period: 3 });
      else if (name === 'BoA') {
        const amp = 1 + 0.5 * st.amp;
        st.amp = 0.0;
        dots.set(name, { next: t + 2, left: 12, per: (k.boa[1] + BOA_SP * sp) * amp, period: 2, n: 0 });
      } else if (name === 'SiphonLife') dots.set(name, { next: t + 3, left: 10, per: k.sl[1] + SL_SP * sp, period: 3 });
      else if (name === 'Immolate') dots.set(name, { next: t + 3, left: 5, per: k.base.ImmolateTick, period: 3, q: 1.0 });
    };
    const tickDots = t => {
      for (const name of [...dots.keys()]) {
        const d = dots.get(name);
        if (t < d.next - 1e-9) continue;
        let per = d.per;
        if ('n' in d) { d.n += 1; per *= d.n <= 4 ? 0.5 : (d.n <= 8 ? 1.0 : 1.5); }
        const x = per * (name === 'Immolate' ? fireNow() : dotMult(name));
        dmg(name, x);
        if (name === 'SiphonLife') heal(x);
        if (name === 'Corruption' && k.nf) st.nfc += k.nf;
        d.left -= 1; d.next += d.period;
        if (d.left <= 0) dots.delete(name);
      }
    };
    const tickChannel = t => {
      const c = chan;
      if (!c || t < c.next - 1e-9) return;
      const x = c.per * drainMult();
      dmg(c.name, x);
      if (c.name === 'DrainLife') heal(x);
      if (k.nf) st.nfc += k.nf;
      c.left -= 1; c.next += c.period;
      if (c.left <= 0) chan = null;
    };
    const decimate = below => { if (k.dec && below) st.dec_until = st.t + 10.0; };
    const bolt = name => {
      const below = st.hp < .35 * mobHpV;
      dmg(name, k.base.ShadowBolt * shadowNow());
      if (k.isb) procs.isb.push([st.t, k.isb_p]);
      decimate(below);
    };
    const land = a => {
      if (a === 'Corruption') applyDot(a);
      else if (a === 'ShadowBolt') bolt(a);
      else if (a === 'Immolate') { dmg(a, k.base[a] * fireNow()); applyDot(a); }
      else if (a === 'SearingPain') {
        const below = st.hp < .35 * mobHpV;
        dmg(a, k.base[a] * fireNow());
        decimate(below);
      } else if (a === 'Incinerate') {
        const d = dots.get('Immolate');
        dmg(a, k.base[a] * (1 + .25 * (d ? d.q : 0.0)) * fireNow());
      } else if (a === 'SoulFire') { dmg(a, k.base[a] * fireNow()); st.cd[a] = st.t + k.sf_cd; }
    };
    const instant = (a, t) => {
      if (a === 'Conflagrate') {
        dmg(a, k.base[a] * fireNow());
        st.cd[a] = t + 10.0;
        if (k.snf) procs.snf_s.push([t, k.hit_d]);
        if (k.keep < 1) {
          const d = dots.get('Immolate'), q = 1 - k.hit_d * (1 - k.keep);
          d.per *= q; d.q *= q; d.gone = true;
        }
      } else if (a === 'Shadowburn') {
        dmg(a, k.base[a] * shadowNow());
        st.cd[a] = t + 15.0;
        if (k.snf) procs.snf_f.push([t, k.hit_d]);
      } else if (a === 'DeathCoil') {
        const x = k.base[a] * shadowNow();
        dmg(a, x); heal(x); st.dc_done = true;
      }
    };
    const channel = (a, t) => {
      const sp = k.sp;
      if (a === 'DrainLife') chan = { name: a, next: t + 1, left: 5, period: 1, per: k.dl[1] + DL_SP * sp };
      else if (a === 'DrainSoul') chan = { name: a, next: t + 3, left: 5, period: 3, per: k.ds[1] + DS_SP * sp };
      else { chan = { name: a, next: t + 1, left: 6, period: 1, per: WRACK[1] + WRACK_SP * sp }; st.wrack_until = t + 6; }
    };
    const start = (a, t) => {
      if (CHANNELS.includes(a)) channel(a, t);
      else if (a === 'BoA' || a === 'SiphonLife') applyDot(a);
      else if (a === 'CoE') { st.coe = k.coe_mult; st.coe_on = true; }
      else if (INSTANTS.includes(a)) instant(a, t);
      else if (k.ct[a] > 0) cast = { end: t + k.ct[a], fn: () => land(a) };
      else land(a);
    };
    const act = (a, t) => {
      if (a !== 'Wand') {
        st.wand = false;
        st.gcd = t + 1.5 * (a === 'DeathCoil' ? k.p_dc : (a === 'SoulFire' ? k.p_sf : 1.0));
      }
      if (a === 'LifeTap') lifeTap();
      else if (a === 'Wand') st.wand = true;
      else if (a === 'NightfallSB') { st.nfc -= 1; spend('ShadowBolt', k.cost.ShadowBolt); bolt('Nightfall'); }
      else { spend(a, k.cost[a]); start(a, t); }
    };

    while (st.hp > 0 && st.t < maxTime) {
      const t = st.t;
      const dsOn = chan !== null && chan.name === 'DrainSoul';
      tickDots(t);
      tickChannel(t);
      const kc = cast;
      if (kc && t >= kc.end - 1e-9) { cast = null; kc.fn(); }
      dmg('Pet', ch.petDps * DT);
      const taken = ch.mobDps * ch.takenFrac * DT;
      st.php -= taken;
      S.hp_taken += taken;
      if (ch.felhunterSac) heal(0.03 * ch.maxHp / 4 * DT);
      if (ch.voidwalkerSac) st.mana = Math.min(ch.maxMana * 2, st.mana + 0.02 * ch.maxMana / 4 * DT);
      const busy = chan !== null || cast !== null;
      if (st.wand && !busy) dmg('Wand', ch.wandDps * DT * k.hit * st.coe);
      if (!busy && t >= st.gcd - 1e-9 && st.hp > 0) {
        let a = choose(policy, ch, dots, st, mobHpV, k);
        if (st.nfc >= 1 && st.mana >= k.cost.ShadowBolt && !NO_NIGHTFALL.includes(a)) a = 'NightfallSB';
        act(a, t);
      }
      if (st.hp <= 0) S.ds_kill = dsOn;
      st.t += DT;
    }
    S.ttk = st.t; S.end_mana = st.mana; S.end_hp = st.php;
    S.net_mana = st.mana - ch.maxMana; S.net_hp = st.php - ch.maxHp;
    return S;
  }

  const immUp = dots => dots.has('Immolate') && !dots.get('Immolate').gone;
  const pol = (policy, key, dflt) => (policy[key] === undefined ? dflt : policy[key]);

  // whether a priority step can be cast now, mana aside
  function ready(step, policy, dots, st, frac, k) {
    const t = st.t;
    if (step === 'Corruption') return !!k.corr && !dots.has('Corruption') && frac > pol(policy, 'corr_min', 0.15);
    if (step === 'BoA') return !!k.boa && !dots.has('BoA') && frac > pol(policy, 'boa_min', 0.5);
    if (step === 'SiphonLife') return !!k.sl && !dots.has('SiphonLife') && frac > pol(policy, 'sl_min', 0.4);
    if (step === 'Wrack') return !!k.wrack && frac > 0.25 && AFF_DOTS.filter(d => dots.has(d)).length >= 2;
    if (step === 'DrainLife') return !!k.dl;
    if (step === 'DrainSoul') return !!k.ds && frac <= pol(policy, 'ds_below', 0.25);
    if (step === 'Immolate') return !immUp(dots) && frac > pol(policy, 'imm_min', 0.2);
    if (step === 'Conflagrate') return !!k.conf && immUp(dots) && t >= st.cd.Conflagrate - 1e-9;
    if (step === 'SearingPain') return !!k.sear;
    if (step === 'Incinerate') return !!k.incin;
    if (step === 'Shadowburn') return !!k.burn && t >= st.cd.Shadowburn - 1e-9 && frac <= pol(policy, 'burn_below', 0.2);
    if (step === 'SoulFire') return !!k.sf && t < st.dec_until && t >= st.cd.SoulFire - 1e-9;
    if (step === 'DeathCoil') return !!k.dc && !st.dc_done;
    if (step === 'CoE') return !!k.coe && !st.coe_on;
    return step === 'ShadowBolt' || step === 'Wand';
  }

  function choose(policy, ch, dots, st, mobHpV, k) {
    const frac = st.hp / mobHpV;
    const hasLt = !!k.lt;                     // no Life Tap before level 6: never tap, wand when out of mana
    const ltGain = k.lt_amt * k.ilt;
    if (hasLt && st.php - k.lt_amt > pol(policy, 'tap_above', 0.75) * ch.maxHp && st.mana + ltGain <= ch.maxMana) return 'LifeTap';
    const ltOk = hasLt && st.php > pol(policy, 'lt_hp_floor', 0.35) * ch.maxHp;
    for (const step of k.prio) {
      if (!ready(step, policy, dots, st, frac, k)) continue;
      if (step === 'Wand') return 'Wand';
      if (st.mana >= k.cost[step]) return step;
      if (ltOk) return 'LifeTap';
      return 'Wand';
    }
    return 'Wand';
  }

  // ---------------------------------------------------------------- per-kill economics
  // Soul Harvest (10 sec after a Drain Soul kill) spent walking adds walkGain; with harvest_drink the player may
  // drink first instead, at restRate + drinkBoost for up to 10 sec; the better order counts
  function restSeconds(deficit, restRate, walkGain, drinkBoost) {
    let rest = Math.max(0.0, deficit - walkGain) / restRate;
    if (drinkBoost > 0) {
      const fast = restRate + drinkBoost;
      const first = deficit <= 10 * fast ? deficit / fast : 10 + (deficit - 10 * fast) / restRate;
      rest = Math.min(rest, first);
    }
    return rest;
  }

  // Before level 6 there is no Life Tap, so health and mana rest apart: eat and drink together, the slower counts.
  function secondsPerKill(ch, mobHpV, policy, travel, opts) {
    travel = travel === undefined ? 8.0 : travel;
    opts = opts || {};
    const L = ch.level;
    const k = 1 + .10 * (ch.talents.ImprovedLifeTap || 0);
    const drink = 2.2 * L;
    const restRate = drink + 1.2 * L * k;
    const manaRegen = (8 + ch.spirit / 4) / 2;
    const regenRate = manaRegen + ch.spirit / 5 * k * 0.5;
    const s = simulate(ch, mobHpV, policy);
    const bonus = s.ds_kill ? SH_BONUS[ch.talents.SoulHarvesting || 0] : 0.0;
    const walk = bonus * manaRegen * Math.min(10.0, travel);
    const boost = opts.harvestDrink ? bonus * drink : 0.0;
    if (rank(LT, L)) {
      const net = s.net_mana + k * s.net_hp + regenRate * travel;
      s.rest = restSeconds(Math.max(0.0, -net), restRate, walk, boost);
    } else {
      // restRate and regenRate count health at k mana a point; the health side takes k back out (k >= 1)
      const eat = (restRate - drink) / k, hpRegen = (regenRate - manaRegen) / k;
      const mDef = Math.max(0.0, -(s.net_mana + manaRegen * travel));
      const hDef = Math.max(0.0, -(s.net_hp + hpRegen * travel));
      s.rest = Math.max(restSeconds(mDef, drink, walk, boost), hDef / eat);
    }
    s.spk = s.ttk + travel + s.rest;
    return s;
  }

  // modifier groups for the best base rotations; every combination is tried, each group off or one option
  function modOptions(L, tal) {
    const fins = [['fin', 'DrainSoul', ' +Drain Soul finish']];
    if (tal.Shadowburn && L >= 20) fins.push(['fin', 'Shadowburn', ' +Shadowburn finish']);
    if (tal.Decimation && L >= 48) fins.push(['fin', 'SoulFire', ' +Soul Fire finish']);
    const groups = L >= 20 ? [[['coe', true, ' +Curse of the Elements']]] : [];
    groups.push(fins);
    if (L >= 42) groups.push([['dc', true, ' +Death Coil']]);
    return groups;
  }

  // every combination of the modifier groups on one base rotation; a cooldown longer than a kill is ready on
  // (base kill cycle / cooldown) of pulls: Amplify Curse 3 min, Death Coil 2 min, Soul Fire 60 sec less Decimation
  function searchMods(L, tal, name, policy, s, run) {
    const ref = s.spk;
    const base = Object.assign({}, policy);
    if (tal.AmplifyCurse && policy.prio.includes('BoA')) base.p_amp = Math.min(1.0, ref / 180.0);
    let combos = [[base, name]];
    for (const group of modOptions(L, tal)) {
      const more = [];
      for (const [p, n] of combos) for (const [key, val, label] of group) more.push([Object.assign({}, p, { [key]: val }), n + label]);
      combos = combos.concat(more);
    }
    let bestName = null, best = null;
    for (const [p, n] of combos) {
      if (p.dc) p.p_dc = Math.min(1.0, ref / 120.0);
      if (p.fin === 'SoulFire') p.p_sf = Math.min(1.0, ref / (60 * (1 - .45 * (tal.Decimation || 0))));
      const r = (p === base && base.p_amp === undefined) ? s : run(p);
      if (best === null || r.spk < best.spk) { best = r; bestName = n; }
    }
    return [bestName, best];
  }

  // Best rotation for a build: the lowest seconds per kill (first wins ties, as in Python). Each base policy the build
  // can cast runs once, then the best opts.top (3) get the modifier search.
  // opts.aggro: the pet holds the mob like a Voidwalker (a Demonic Brand scenario, not the default).
  // opts.harvestDrink, opts.ddMode ('base', 'scaled', 'wowhead'), opts.suppAll, opts.lashShare: see the Python.
  // opts.hpMults: average each rotation over mobs of these HP multiples (kill time snaps to DoT and drain ticks).
  function evaluate(L, tal, pet, spPerLevel, opts) {
    opts = opts || {};
    const top = opts.top === undefined ? 3 : opts.top;
    const hpMults = opts.hpMults || [1.0];
    const char = () => {
      const ch = makeChar(L, tal, spPerLevel, pet, opts.lashShare);
      if (opts.aggro && pet !== 'voidwalker' && pet !== 'none') ch.takenFrac = 0.10 * takenScale(tal, pet);
      ch.ddMode = opts.ddMode || 'base';
      ch.suppAll = opts.suppAll !== false;
      return ch;
    };
    const run = policy => {
      const rs = hpMults.map(m => secondsPerKill(char(), mobHp(L) * m, policy, undefined, { harvestDrink: !!opts.harvestDrink }));
      if (rs.length === 1) return rs[0];
      const out = Object.assign({}, rs[0]);
      for (const key of ['spk', 'ttk', 'rest', 'healed']) out[key] = rs.reduce((a, r) => a + r[key], 0) / rs.length;
      return out;
    };
    const ch0 = char(), seen = new Set(), base = [];
    for (const [name, prio] of POLICIES) {
      const sig = usableSteps(prio, ch0).join(',');
      if (seen.has(sig)) continue;
      seen.add(sig);
      const policy = { prio };
      base.push([name, policy, run(policy)]);
    }
    let bestName = null, best = null;
    for (const [name, , s] of base) if (best === null || s.spk < best.spk) { best = s; bestName = name; }
    if (opts.mods !== false) {
      const ranked = base.slice().sort((a, b) => a[2].spk - b[2].spk).slice(0, top);
      for (const [name, policy, s] of ranked) {
        const [n2, s2] = searchMods(L, tal, name, policy, s, run);
        if (s2.spk < best.spk) { best = s2; bestName = n2; }
      }
    }
    best.policy = bestName;
    return best;
  }

  const api = { rank, valid, makeChar, mobHp, simulate, secondsPerKill, evaluate, POLICIES, AFF, DEMO, DESTRO, PREREQ, ddAvg, usableSteps };
  if (typeof module !== 'undefined') module.exports = api; else root.LevelingModel = api;
})(this);
