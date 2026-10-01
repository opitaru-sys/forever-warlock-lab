/* Forever Warlock raid model (level 60, steady state). Expected values, no RNG.
 * Port of models/raid_model.py, the reference (tests/parity_test.js, tests/raid_options_test.js).
 * Budget: DoT/cooldown cast time + Nightfall Shadow Bolts + Life Tap time + filler time = 1 second.
 * Mana: Life Tap funds whatever mana regen (mp5) does not cover.
 * Spell values: beta client 1.60.1.69893 (SpellEffect table), max ranks unless trainerRanks is on.
 *
 * Options on o, all off by default (the reviewed numbers do not move):
 *   fireImmune  for bosses immune to Fire. Other specs drop their Fire spells. rank() keeps the two Fire
 *               Destruction specs but lists them last with viable: false, a reason, and zero damage;
 *               specTotal() returns 0 for them.
 *   execute     true (the boss spends the last 35% of the fight under 35% health) or a share from 0 to 1.
 *               Only the Decimation specs (demo-pact, demo-deep) change.
 *   coe         Curse of the Elements on the main target: +10% magic damage taken. The Succubus gains it
 *               on Lash of Pain only, about 10% of her damage; her melee is Physical.
 *   mp5         mana per 5 seconds from gear and buffs.
 *   consumables a Major Mana Potion and a Demonic or Dark Rune on cooldown from the pull, spread over a
 *               300 s fight as extra mana per second (30, the same as 150 mp5); stacks with mp5. The
 *               rune's life cost is treated like Life Tap's health: healed by the raid.
 *   targets     1 or 2. On 2, each spec takes its best second-target plan (a DoT and Bane spread, or
 *               Destruction's Bane of Havoc). Damage is the total over both targets.
 *   impDps      deep Demonology's Imp under 35%, damage per second before talents (default about 41:
 *               Firebolt 45 to 50 every 2 s plus Demonic Knowledge's +60 pet spell power).
 *   trainerRanks the trainer's level-60 ranks (Shadow Bolt 9, Corruption 6, Immolate 7) instead of the book
 *               ranks (Shadow Bolt 10, Corruption 7, Immolate 8), which only Ruins of Ahn'Qiraj taught in
 *               Classic. The page turns it on unless the books box is ticked.
 * And three with a non-off default:
 *   shadowburn  true (default): Destruction casts Shadowburn on cooldown. false: never, because each
 *               cast costs a Soul Shard; the Fire builds then also lose Shadow and Flame's +10% Fire.
 *   brandHits   branded pet attacks per Demonic Brand in deep Demonology: 6 (default, client rank
 *               text), 3 (Wowhead tooltip) or 0 (the brand deals no damage, threat only).
 *   brandScaling 'lock' (default): brand damage scales with your spell power; 'pet': with the demon's
 *               (Demonic Knowledge, +60).
 */
(function (root) {
  const GCD = 1.5;
  const ev = (c, bonus) => 1 + c * bonus;
  const dmg = (spell, sp) => spell[0] + spell[1] * sp;

  // [base damage, spell power coefficient] over the full duration, max rank.
  const CORRUPTION = [438, 1.2], AGONY = [552, 1.596], SIPHON_LIFE = [410, 0.5];
  const IMMOLATE_HIT = [158, 0.2], IMMOLATE_DOT = [275, 0.65], SHADOW_BOLT = [268, 0.857];
  const WRACK = [216, 0.858], CONFLAGRATE = [282, 0.429], SHADOWBURN = [266, 0.429];
  const INCINERATE = [217, 0.714], SOUL_FIRE = [431, 1.0], SEARING_PAIN = [114, 0.429];
  const BRAND_HIT = [66.5, 0.078];          // Demonic Brand, per branded pet attack at level 60
  const doom = o => [1742, typeof o.bodCoef === 'number' ? o.bodCoef : 4.0];
  // Shadow Bolt 10, Corruption 7 and Immolate 8 above are taught by Grimoires 21281 to 21283, whose only Classic
  // source was Ruins of Ahn'Qiraj. The trainer's ranks at level 60, same client table: Shadow Bolt 9 (11661),
  // Corruption 6 (11672, 57 a tick x 6), Immolate 7 (11668, 52 a tick x 5). Mana per cast goes with each rank.
  const BOOK_RANKS = { sb: SHADOW_BOLT, sbMana: 380, corr: CORRUPTION, corrMana: 340,
                       immHit: IMMOLATE_HIT, immDot: IMMOLATE_DOT, immMana: 380 };
  const TRAINER_RANKS = { sb: [251, 0.857], sbMana: 370, corr: [342, 1.2], corrMana: 290,
                          immHit: [146, 0.2], immDot: [260, 0.65], immMana: 370 };
  const ranks = o => o.trainerRanks ? TRAINER_RANKS : BOOK_RANKS;
  const DRAINS = 1.20 * 1.36;               // Improved Drains 3/3, Soul Siphon 3/3

  const EXEC_SHARE = 0.35, COE = 1.10, LASH_SHARE = 0.10, HAVOC_COPY = 0.15;
  const HAVOC = [0, 300, GCD, 65];          // 5 min Bane, one GCD, 5% of base mana (about 1,300 assumed)
  const DECIMATION = 1.06;                  // Shadow Bolt and Searing Pain +6% on a target under 35%
  const SOUL_FIRE_EXEC = [2.4, 6.0];        // Decimation Soul Fire: cast s, cooldown s
  const BRAND_ATTACKS = 6, BRAND_S = 10;    // Demonic Brand 3/3: pet attacks per brand, brand duration
  const SUCC_RATE = 0.5 + 1 / 12, IMP_RATE = 0.5;   // pet attacks per second (Succubus melee 2.0 s assumed)
  const SUCC_FULL = 50;     // Succubus dps that means she is on the boss all fight; below it her attack rate scales down (assumption)
  const PET_HIT = 0.86;     // pet attacks that land on a raid boss (about 14% miss or dodge, assumed); a miss still uses a brand charge
  const PET_SP = 60;                       // demon spell power from Demonic Knowledge 3/3
  const IMP_BASE = (47 + 0.571 * PET_SP) / 2;  // Imp dps before talents: Firebolt 11763, 2 s cast
  const FIGHT_S = 300;
  const SWAP = [7.5, 884];   // one-off Imp summon under 35%: 6 s cast (no Fel Domination, Master Summoner 2/2) plus the
                             // Soul Link GCD; 68% of base mana (about 1,300, assumed)
  const POTION_MANA = (1350 + 2250) / 2, RUNE_MANA = (900 + 1500) / 2;   // items 13444, 12662 / 20520, 2 min each
  const CONSUMABLE_REGEN = (Math.floor(FIGHT_S / 120) + 1) * (POTION_MANA + RUNE_MANA) / FIGHT_S;   // 30 mana per s
  // Succubus talents: [Soul Link x Unholy Power, Master Demonologist, Improved Sayaad]. Master Demonologist (+10% Shadow)
  // and Improved Sayaad (+30% Lash of Pain) reach only her Lash of Pain share (LASH_SHARE); her melee is Physical.
  const SUCC_PLAIN = [1, 1, 1], SUCC_PACT = [1.03 * 1.02, 1.10, 1.30], SUCC_DEEP = [1.03 * 1.10, 1.10, 1.30];
  const DEEP_IMP_PET = 1.03 * 1.10 * 1.10, BRAND_PET = 1.03 * 1.10 * 1.10;   // Imp: no Improved Imp in 5/31/15
  const SECOND = ' (2nd)';
  const NAMES = { Corruption: 'Corruption', BoA: 'Bane of Agony', BoD: 'Bane of Doom', SiphonLife: 'Siphon Life',
                  Immolate: 'Immolate', Havoc: 'Bane of Havoc' };
  const FIRE_REASON = 'Not viable on a boss immune to Fire: Immolate, Conflagrate and Incinerate deal nothing. Use Destruction, Shadow.';

  const execShare = o => o.execute === true ? EXEC_SHARE
    : (typeof o.execute === 'number' ? Math.min(1, Math.max(0, o.execute)) : 0);
  const regen = o => (typeof o.mp5 === 'number' ? o.mp5 : 0) / 5 + (o.consumables ? CONSUMABLE_REGEN : 0);   // items are off the GCD
  const coeMult = o => o.coe ? COE : 1;
  const succMult = (o, t) => t[0] * ((1 - LASH_SHARE) + LASH_SHARE * t[1] * t[2] * coeMult(o));
  const impDps = o => typeof o.impDps === 'number' ? o.impDps : IMP_BASE;
  const brandHits = o => typeof o.brandHits === 'number' ? o.brandHits : BRAND_ATTACKS;

  function solve(periodic, filler, lt, nf, ampFrac, ampNames, regenRate) {
    let A = 0, M = 0;
    for (const k in periodic) { const [, T, t, m] = periodic[k]; A += t / T; M += m / T; }
    const [dF, cF, mF, tps] = filler;
    const rg = regenRate || 0;
    let r0 = 0, r1 = 0, sbd = 0, sbm = 0;
    if (nf) { const [p, corrTps, d, m] = nf; r0 = p * corrTps; r1 = p * tps; sbd = d; sbm = m; }
    const k = GCD / lt;
    let f = (1 - A - GCD * r0 - k * (M + sbm * r0 - rg)) / (1 + GCD * r1 + k * (sbm * r1 + mF / cF));
    if ((M + sbm * (r0 + r1 * f) + f * mF / cF - rg) / lt < 0) f = (1 - A - GCD * r0) / (1 + GCD * r1);  // no Life Tap needed
    const parts = {};
    let shadowDots = 0;
    for (const n in periodic) {
      const [D, T] = periodic[n];
      parts[n] = D / T;
      if ((ampNames || []).includes(n)) shadowDots += D / T;
    }
    parts.Filler = f * (dF / cF + (ampFrac || 0) * shadowDots);
    if (nf) parts['Nightfall'] = (r0 + r1 * f) * sbd;
    const dps = Object.values(parts).reduce((a, b) => a + b, 0);
    return { dps, parts, f };
  }

  // Curse of the Elements on the main target, then the Bane of Havoc copy of main-target damage.
  function finish(res, coe, copy) {
    if (!coe && !copy) return res;
    const parts = {};
    for (const n in res.parts) parts[n] = coe && !n.endsWith(SECOND) ? res.parts[n] * COE : res.parts[n];
    if (copy) {
      let main = 0;
      for (const n in parts) if (!n.endsWith(SECOND)) main += parts[n];
      parts['Havoc copy'] = copy * main;
    }
    return { dps: Object.values(parts).reduce((a, b) => a + b, 0), parts, f: res.f };
  }

  // Time-weighted mix of two phases: r1 for (1 - x) of the fight, r2 for x.
  function blend(r1, r2, x) {
    const parts = {};
    new Set(Object.keys(r1.parts).concat(Object.keys(r2.parts))).forEach(n => {
      parts[n] = (1 - x) * (r1.parts[n] || 0) + x * (r2.parts[n] || 0);
    });
    return { dps: (1 - x) * r1.dps + x * r2.dps, parts, f: (1 - x) * r1.f + x * r2.f };
  }

  // Second-target plans: every subset of the optional DoTs with each Bane choice (null = none).
  function plans(targets, optional, banes) {
    if (targets !== 2) return [[]];
    const out = [];
    banes.forEach(bane => {
      for (let mask = 0; mask < 1 << optional.length; mask++) {
        const plan = optional.filter((n, i) => (mask >> i) & 1);
        out.push(bane ? plan.concat([bane]) : plan);
      }
    });
    return out;
  }
  // Highest damage among feasible rotations: null marks an infeasible option, a negative filler share a rotation
  // that needs more than 100% of the time. Falls back to the best of all only if none fits.
  function best(list) {
    const all = list.filter(x => x !== null);
    const ok = all.filter(x => x.res.f >= 0);
    return (ok.length ? ok : all).reduce((a, b) => (a === null || b.res.dps > a.res.dps ? b : a), null);
  }

  // race: { crit, spMult, castSpeed, eureka, totg }
  function raceMods(race, opts) {
    const r = { crit: 0, spMult: 1, castSpeed: 1, eureka: 0, totg: 0, spiritMult: 1 };
    if (race === 'human') { if (opts.sword) r.crit = 0.02; r.spiritMult = 1.05; }
    if (race === 'orc') r.spMult = 1 + 0.10 * 15 / 120;        // Blood Fury: +10% SP, 15 s every 2 min
    if (race === 'troll') r.castSpeed = 1 + 0.10 * 10 / 180;    // Berserking: casts only, not DoTs or channels
    if (race === 'gnome') r.eureka = 0.10 * 3 / 120;            // Eureka!: next 3 spells +10%, every 2 min
    if (race === 'undead') r.totg = 0.10;                       // Touch of the Grave, caster version (spell 1260201)
    return r;
  }

  // Hit below the boss cap: each 1% short of 16% loses 1% of landed damage.
  // Legacy switch kept so the reviewed defaults reproduce exactly:
  // gearHitCapped true = 16% from gear, false = 11% (Suppression's 5% then caps every build).
  function gearHit(o) {
    if (typeof o.gearHit === 'number') return o.gearHit;
    return o.gearHitCapped ? 0.16 : 0.11;
  }
  function hitMult(o, talentHit) { return 1 - Math.max(0, 0.16 - gearHit(o) - talentHit); }
  function scaleHit(res, m) {
    if (m === 1) return res;
    for (const k in res.parts) res.parts[k] *= m;
    res.dps *= m;
    return res;
  }

  function lifeTap(opts, rm, ilt) {
    const base = opts.lifeTapMode === 'spirit' ? 430 + opts.spirit * rm.spiritMult : 840;
    return base * (ilt ? 1.2 : 1.0);
  }

  function withEureka(res, fillerDmg, rm) {
    if (!rm.eureka) return res;
    const extra = rm.eureka * fillerDmg;          // 10% of 3 filler casts per 120 s
    res.parts.Racial = (res.parts.Racial || 0) + extra;
    res.dps += extra;
    return res;
  }

  // Touch of the Grave: 10% chance per damaging cast, 1 s cooldown, drains 5% of max health from the target.
  // Counts casts only (periodic casts, filler casts, extra casts such as Nightfall). A reader's beta test: applying a DoT procs it, ticks don't.
  function withTotg(res, periodic, filler, rm, o, extraCasts, hitM) {
    if (!rm.totg) return res;
    let casts = res.f / filler[1] + (extraCasts || 0);
    for (const k in periodic) if (periodic[k][2] > 0) casts += 1 / periodic[k][1];
    const pl = rm.totg * casts;
    const extra = pl / (1 + pl) * 0.05 * (o.maxHp || 4500) * (hitM || 1);   // renewal rate with a 1 s dead time
    res.parts.Racial = (res.parts.Racial || 0) + extra;
    res.dps += extra;
    return res;
  }

  function aff(o, bane, keepSuccubus) {
    const rm = raceMods(o.race, o);
    const sp = o.sp * rm.spMult, c = o.crit + rm.crit, cs = c + 0.05;
    const sh = (keepSuccubus ? 1.0 : 1.15) * 1.05, mal = 1.05, dc = ev(cs, 1.0);
    const fireOk = !o.fireImmune, rk = ranks(o);
    const dot = n => {
      if (n === 'Corruption') return [dmg(rk.corr, sp) * sh * mal * 1.10 * dc, 18, GCD, rk.corrMana];
      if (n === 'BoA') return [dmg(AGONY, sp) * sh * mal * 1.10 * dc, 24, GCD, 215];
      if (n === 'BoD') return [dmg(doom(o), sp) * sh * mal * dc, 60, GCD, 300];
      if (n === 'SiphonLife') return [dmg(SIPHON_LIFE, sp) * sh * mal * dc, 30, GCD, 365];
      return [dmg(rk.immHit, sp) * ev(c, 0.5) + dmg(rk.immDot, sp) * mal * ev(c, 0.5), 15, 2.0, rk.immMana];
    };
    const sb = dmg(rk.sb, sp) * sh * ev(cs, 0.5);
    const F = [dmg(WRACK, sp) * sh * mal * DRAINS * dc, 6.0, 200, 1.0];   // Wrack
    const lt = lifeTap(o, rm, false);
    const main = ['Corruption', bane, 'SiphonLife'].concat(fireOk ? ['Immolate'] : []);
    const optional = ['Corruption', 'SiphonLife'].concat(fireOk ? ['Immolate'] : []);
    const pick = best(plans(o.targets, optional, [null, 'BoA', 'BoD']).map(plan => {
      const P = {};
      main.forEach(n => { P[NAMES[n]] = dot(n); });
      plan.forEach(n => { P[NAMES[n] + SECOND] = dot(n); });
      const nf = [0.04, (1 + (plan.includes('Corruption') ? 1 : 0)) / 3, sb, rk.sbMana];
      // Wrack's +10% reaches Corruption and Bane of Agony only (client class mask), on its own target.
      const res = finish(solve(P, F, lt, nf, 0.10, ['Corruption', 'Bane of Agony'], regen(o)), o.coe);
      return { res, P, nfCasts: nf[0] * nf[1] + nf[0] * F[3] * res.f };
    }));
    const res = withTotg(withEureka(pick.res, F[0] * coeMult(o), rm), pick.P, F, rm, o, pick.nfCasts);
    return scaleHit(res, hitMult(o, 0.05));
  }

  function destro(o, bane, version) {
    // version: 'sb' = Imp sac + Shadow Bolt (+Shadowburn); 'incin' = Succubus sac + Incinerate; 'keep' = Succubus out
    if (o.fireImmune && version !== 'sb') return { dps: 0, parts: {}, f: 0, viable: false, reason: FIRE_REASON };
    const rm = raceMods(o.race, o);
    const sp = o.sp * rm.spMult, c = o.crit + rm.crit;
    const fireOk = !o.fireImmune, rk = ranks(o);
    const aftermath = version !== 'sb';
    const sh = (version === 'sb' ? 1.15 : 1.0) * (fireOk ? 1.10 : 1.0);   // S&F Shadow needs Conflagrate, so Immolate
    const burn = o.shadowburn !== false;                          // each Shadowburn costs a Soul Shard
    const fi = (version === 'incin' ? 1.15 : 1.0) * (burn ? 1.10 : 1.0);   // S&F Fire comes from Shadowburn
    const AF = 1.10, mal = 1.02, cat = 0.9, dstr = ev(c, 1.0), dotc = ev(c, 0.5);
    const lt = lifeTap(o, rm, true), castSb = 2.5 / rm.castSpeed;
    const direct = dmg(rk.immHit, sp) * (aftermath ? 1.5 : 1.0);
    const dot = (n, isb) => {
      if (n === 'Corruption') return [dmg(rk.corr, sp) * sh * mal * dotc * isb, 18, 2.0, rk.corrMana];
      if (n === 'BoA') return [dmg(AGONY, sp) * sh * mal * dotc * isb, 24, GCD, 215];
      if (n === 'BoD') return [dmg(doom(o), sp) * sh * mal * dotc * isb, 60, GCD, 300];
      if (n === 'Havoc') return HAVOC;
      return [(direct + dmg(rk.immDot, sp) * mal) * fi * AF * dstr, 15, 1.5, rk.immMana * cat];
    };
    function build(isb, plan) {
      const P = {};
      P.Corruption = dot('Corruption', isb);
      P[NAMES[bane]] = dot(bane, isb);     // Havoc takes the second target's Bane slot only (one Bane per target)
      if (fireOk) {
        P.Immolate = dot('Immolate', 1);
        P.Conflagrate = [dmg(CONFLAGRATE, sp) * fi * AF * dstr, 10, GCD, 255 * cat];
      }
      if (burn) P.Shadowburn = [dmg(SHADOWBURN, sp) * sh * AF * dstr * isb, 15, GCD, 365 * cat];
      plan.forEach(n => { P[NAMES[n] + SECOND] = dot(n, 1); });
      const F = version === 'sb'
        ? [dmg(rk.sb, sp) * sh * AF * dstr * isb, castSb, rk.sbMana * cat, 0]
        : [dmg(INCINERATE, sp) * 1.25 * fi * AF * dstr, 2.0 / rm.castSpeed, 325 * cat, 0];
      return [P, F];
    }
    const optional = ['Corruption'].concat(fireOk ? ['Immolate'] : []);
    const pick = best(plans(o.targets, optional, [null, 'BoA', 'BoD', 'Havoc']).map(plan => {
      let [P, F] = build(1.0, plan);
      let res = solve(P, F, lt, null, 0, null, regen(o));
      if (version === 'sb') {
        const u = 1 - Math.pow(1 - c, o.isbDuration * res.f / castSb);
        [P, F] = build(1 + 0.2 * u, plan);
        res = solve(P, F, lt, null, 0, null, regen(o));
      }
      return { res: finish(res, o.coe, plan.includes('Havoc') ? HAVOC_COPY : 0), P, F };
    }));
    return scaleHit(withTotg(withEureka(pick.res, pick.F[0] * coeMult(o), rm), pick.P, pick.F, rm, o), hitMult(o, 0.05));
  }

  // One phase of a Demonology rotation. q: sp2, c, lt, bane, allm, sh, fire, cat, immolate, decim, fil,
  // soulFire [cast, cooldown] | null, brand [period, bonus] | null, fixed {name: periodic} | null, hitM.
  // Soul Fire and the Searing Pain brand weave are cast only when they raise damage.
  function demoPhase(o, rm, q) {
    const dstr = ev(q.c, 1.0), dotc = ev(q.c, 0.5), castSb = 2.5 / rm.castSpeed, rk = ranks(o);
    const spain = dmg(SEARING_PAIN, q.sp2) * q.fire * q.allm * dstr * q.decim;
    const dot = (n, isb) => {
      if (n === 'Corruption') return [dmg(rk.corr, q.sp2) * q.sh * q.allm * dotc * isb, 18, 2.0, rk.corrMana];
      if (n === 'BoA') return [dmg(AGONY, q.sp2) * q.sh * q.allm * dotc * isb, 24, GCD, 215];
      if (n === 'BoD') return [dmg(doom(o), q.sp2) * q.sh * q.allm * dotc * isb, 60, GCD, 300];
      return [(dmg(rk.immHit, q.sp2) + dmg(rk.immDot, q.sp2)) * q.fire * q.allm * dstr, 15, 1.5, rk.immMana * q.cat];
    };
    function build(isb, plan, sf, br) {
      const P = {};
      P.Corruption = dot('Corruption', isb);
      P[NAMES[q.bane]] = dot(q.bane, isb);
      if (q.immolate) P.Immolate = dot('Immolate', 1);
      plan.forEach(n => { P[NAMES[n] + SECOND] = dot(n, 1); });
      if (sf) P['Soul Fire'] = [dmg(SOUL_FIRE, q.sp2) * q.fire * q.allm * dstr, sf[1], sf[0] / rm.castSpeed, 335 * q.cat];
      if (br) P['Searing Pain (Brand)'] = [spain + br[1], br[0], GCD, 168 * q.cat];
      Object.assign(P, q.fixed || {});
      const F = q.fil === 'SB'
        ? [dmg(rk.sb, q.sp2) * q.sh * q.allm * dstr * isb * q.decim, castSb, rk.sbMana * q.cat, 0]
        : [spain, 1.5, 168 * q.cat, 0];
      return [P, F];
    }
    function evaluate(plan, sf, br) {
      let [P, F] = build(1.0, plan, sf, br);
      let res = solve(P, F, q.lt, null, 0, null, regen(o));
      if (res.f < 0) return null;                                  // does not fit in the time
      const casts = res.f / F[1];
      // Decimation needs a Shadow Bolt or Searing Pain every 10 s, or Soul Fire is slow and costs a shard
      if (sf && q.decim > 1 && casts + (br ? 1 / br[0] : 0) < 1 / BRAND_S) return null;
      if (q.fil === 'SB') {
        const u = 1 - Math.pow(1 - q.c, o.isbDuration * res.f / castSb);
        [P, F] = build(1 + 0.2 * u, plan, sf, br);
        res = solve(P, F, q.lt, null, 0, null, regen(o));
      }
      if (q.filBrand) {                                             // the Searing Pain filler brands the Imp's attacks
        const [charges, rate, perAttack] = q.filBrand;
        const branded = Math.min(charges * casts, rate, rate * BRAND_S * casts);
        res.parts['Demonic Brand (Imp)'] = branded * perAttack;
        res.dps += branded * perAttack;
      }
      return { res: finish(res, o.coe), P, F };
    }
    const combos = [];
    (q.soulFire ? [null, q.soulFire] : [null]).forEach(sf => (q.brand ? [null, q.brand] : [null]).forEach(br => combos.push([sf, br])));
    const optional = ['Corruption'].concat(q.immolate ? ['Immolate'] : []);
    const pick = best([].concat(...plans(o.targets, optional, [null, 'BoA', 'BoD']).map(plan =>
      combos.map(([sf, br]) => evaluate(plan, sf, br)))));
    return withTotg(withEureka(pick.res, pick.F[0] * coeMult(o), rm), pick.P, pick.F, rm, o, 0, q.hitM);
  }

  // Demonology with Pact, 5/31/15 since v8.1: Suppression 5, the wowforeverbuilds Demonology 31, Improved Shadow Bolt 5,
  // Bane 5, Ruin 5 (Destructive Reach 2 and Cataclysm 3 traded for Suppression). Imp sacrificed, Succubus out, Shadow
  // Bolt. Decimation 2/2 under 35%.
  function demo(o, bane) {
    const rm = raceMods(o.race, o);
    const hitM = hitMult(o, 0.05);                              // Suppression 5/5
    const q = { sp2: o.sp * rm.spMult + 60, c: o.crit + rm.crit, lt: lifeTap(o, rm, false), bane,   // Demonic Knowledge +60
      allm: 1.03 * hitM, sh: 1.15 * 1.10, fire: 1.0, cat: 1.0, immolate: !o.fireImmune,             // Soul Link; Imp sac + Master Demonologist
      decim: 1.0, fil: 'SB', soulFire: null, brand: null, fixed: null, hitM };
    const p1 = demoPhase(o, rm, q);
    const x = execShare(o);
    if (!x) return p1;
    return blend(p1, demoPhase(o, rm, Object.assign({}, q, { decim: DECIMATION, soulFire: o.fireImmune ? null : SOUL_FIRE_EXEC })), x);
  }

  // Deep Demonology 5/31/15 (reader 510Kyle's revision): Suppression 5; Demonology 31 with Demonic Brand 3 and Unholy
  // Power 5; Improved Shadow Bolt 5, Bane 5, Ruin 5. Above 35%: as Pact, plus a Searing Pain for Demonic Brand when it
  // pays. Under 35% it takes whichever plan does more damage, demons included, and says which in execPlan: 'imp'
  // (summon the Imp, a 6 s cast without Fel Domination, which cancels the Imp sacrifice; Soul Link recast; Searing
  // Pain filler that brands the Imp's attacks as often as it lands; Decimation Soul Fire) or 'succubus' (keep her
  // out: Shadow Bolt, the brand weave and Decimation Soul Fire when they pay and fit).
  function demoDeep(o, bane) {
    const rm = raceMods(o.race, o);
    const hitM = hitMult(o, 0.05);                              // Suppression 5/5
    const sp2 = o.sp * rm.spMult + 60;
    const hits = brandHits(o), branding = hits > 0 && !o.fireImmune;   // 0 hits: Demonic Brand is threat only
    // the brand needs your Searing Pain to land (hitM) and the pet's attack to land (PET_HIT)
    const perHit = dmg(BRAND_HIT, o.brandScaling === 'pet' ? PET_SP : sp2) * hitM * PET_HIT * BRAND_PET;
    const succRate = SUCC_RATE * Math.min(1, Math.max(0, o.petDps) / SUCC_FULL);   // her time on the boss
    const impRate = IMP_RATE * Math.min(1, Math.max(0, impDps(o)) / IMP_BASE);
    const period = Math.min(BRAND_S, hits / succRate);
    const q = { sp2, c: o.crit + rm.crit, lt: lifeTap(o, rm, false), bane, allm: 1.03 * hitM, sh: 1.15 * 1.10,
      fire: 1.0, cat: 1.0, immolate: !o.fireImmune, decim: 1.0, fil: 'SB', soulFire: null, fixed: null, hitM,
      brand: !branding || !(succRate > 0) ? null : [period, period * succRate * perHit], filBrand: null };   // a brand needs a demon that attacks
    const p1 = demoPhase(o, rm, q);
    const x = execShare(o);
    if (!x) return Object.assign(p1, { execPlan: null });
    const keep = demoPhase(o, rm, Object.assign({}, q, { decim: DECIMATION, soulFire: o.fireImmune ? null : SOUL_FIRE_EXEC }));
    if (o.fireImmune) return Object.assign(blend(p1, keep, x), { execPlan: 'succubus' });   // nothing in the swap plan lands
    const fixed = { 'Pet swap': [0, x * FIGHT_S, SWAP[0], SWAP[1]] };
    const filBrand = branding && impRate > 0 ? [hits, impRate, perHit] : null;
    const swap = demoPhase(o, rm, Object.assign({}, q, { sh: 1.0, fire: 1.10, decim: DECIMATION, fil: 'SearingPain',
      brand: null, soulFire: SOUL_FIRE_EXEC, fixed, filBrand }));
    if (keep.dps + deepExecPet(o, 'succubus') >= swap.dps + deepExecPet(o, 'imp')) return Object.assign(blend(p1, keep, x), { execPlan: 'succubus' });
    return Object.assign(blend(p1, swap, x), { execPlan: 'imp' });
  }
  // Demon damage in the execute phase: the Imp for 'imp', else the Succubus.
  const deepExecPet = (o, plan) => plan === 'imp' ? DEEP_IMP_PET * impDps(o) * coeMult(o) : succMult(o, SUCC_DEEP) * o.petDps;
  // Demon damage over the fight: the Succubus above 35%, below it the demon of the plan in use.
  function deepPet(o, plan) {
    const succ = deepExecPet(o, 'succubus');
    const x = execShare(o);
    if (!x || plan !== 'imp' || o.fireImmune) return succ;
    return (1 - x) * succ + x * deepExecPet(o, 'imp');
  }

  const SPECS = [
    { id: 'destro-fire', name: 'Destruction, Fire', note: 'Succubus sacrificed, Incinerate filler, Aftermath', pet: 0, fire: true,
      run: (o, b) => destro(o, b, 'incin') },
    { id: 'destro-keep', name: 'Destruction, Fire + Succubus', note: 'Succubus kept out, Incinerate filler', pet: 1.0, succ: SUCC_PLAIN, fire: true,
      run: (o, b) => destro(o, b, 'keep') },
    { id: 'destro-shadow', name: 'Destruction, Shadow (published)', note: 'Imp sacrificed, Shadow Bolt and Shadowburn', pet: 0,
      run: (o, b) => destro(o, b, 'sb') },
    { id: 'demo-pact', name: 'Demonology, Pact', note: 'Now with Suppression 5: Imp sacrificed, Succubus out, Shadow Bolt',
      pet: succMult({}, SUCC_PACT), succ: SUCC_PACT,
      run: (o, b) => demo(o, b) },
    { id: 'demo-deep', name: 'Demonology, deep 5/31/15', note: 'Suppression 5, Imp sacrificed, Succubus out, Shadow Bolt, Searing Pain for Demonic Brand',
      pet: succMult({}, SUCC_DEEP), succ: SUCC_DEEP, petFn: deepPet, run: (o, b) => demoDeep(o, b) },
    { id: 'aff-sac', name: 'Affliction', note: 'Imp sacrificed, Wrack filler, Immolate kept up', pet: 0,
      run: (o, b) => aff(o, b, false) },
    { id: 'aff-keep', name: 'Affliction + Succubus', note: 'Succubus kept out, Wrack filler', pet: 1.0, succ: SUCC_PLAIN,
      run: (o, b) => aff(o, b, true) },
  ];

  function evalSpec(o, s) {
    const head = { id: s.id, name: s.name, note: s.note };
    if (o.fireImmune && s.fire) {
      return Object.assign(head, { viable: false, reason: FIRE_REASON, bane: '', lock: 0, pet: 0, total: 0, petShare: 0, parts: {}, filler: 0, execPlan: null });
    }
    const a = s.run(o, 'BoA'), d = s.run(o, 'BoD');
    const petOf = r => s.petFn ? s.petFn(o, r.execPlan) : (s.succ ? succMult(o, s.succ) * o.petDps : 0);
    const pa = petOf(a), pd = petOf(d);
    // deep Demonology's execute plan can differ by Bane, so it compares with the demons included
    const useD = s.petFn ? d.dps + pd >= a.dps + pa : d.dps >= a.dps;
    const best = useD ? { r: d, bane: 'Bane of Doom', pet: pd } : { r: a, bane: 'Bane of Agony', pet: pa };
    const pet = best.pet, total = best.r.dps + pet;
    return Object.assign(head, { viable: true, reason: '', bane: best.bane, lock: best.r.dps, pet, total,
      petShare: total ? pet / total : 0, parts: best.r.parts, filler: best.r.f, execPlan: best.r.execPlan || null });
  }

  // Viable specs first, by total damage; non-viable ones (fireImmune) last, flagged, at zero.
  // execPlan: deep Demonology's execute plan ('imp' | 'succubus'), null for other specs or with execute off.
  function rank(o) {
    return SPECS.map(s => evalSpec(o, s)).sort((x, y) => (y.viable - x.viable) || (y.total - x.total));
  }

  function specTotal(o, id) {
    return evalSpec(o, SPECS.find(x => x.id === id)).total;
  }

  // Damage per second gained from +1 spell power, +1% crit, +1% hit, and their spell power equivalents.
  // Every option on o (fireImmune, execute, coe, mp5, targets, trainerRanks) passes through.
  function statWeights(o, id) {
    const f = p => specTotal(Object.assign({}, o, p), id);
    const sp = (f({ sp: o.sp + 10 }) - f({ sp: Math.max(0, o.sp - 10) })) / (o.sp >= 10 ? 20 : 10 + o.sp);
    const crit = (f({ crit: o.crit + 0.01 }) - f({ crit: Math.max(0, o.crit - 0.01) })) / (o.crit >= 0.01 ? 2 : 1);
    const gh = gearHit(o);
    const hit = f({ gearHit: gh + 0.01 }) - f({ gearHit: gh });
    return { sp, crit, hit, critInSp: sp > 0 ? crit / sp : 0, hitInSp: sp > 0 ? hit / sp : 0 };
  }

  // Swap an equipped item (a) for an alternative (b). Current totals already include item a.
  function compareItems(o, id, a, b) {
    const base = specTotal(o, id);
    const swapped = specTotal(Object.assign({}, o, {
      sp: Math.max(0, o.sp - a.sp + b.sp),
      crit: Math.max(0, o.crit - a.crit + b.crit),
      gearHit: Math.max(0, gearHit(o) - a.hit + b.hit),
    }), id);
    return { base, swapped, diff: swapped - base, pct: base ? (swapped / base - 1) * 100 : 0 };
  }

  const api = { rank, aff, destro, demo, demoDeep, SPECS, statWeights, compareItems, specTotal };
  if (typeof module !== 'undefined') module.exports = api; else root.WarlockModel = api;
})(this);
