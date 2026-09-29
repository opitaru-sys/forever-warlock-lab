/* Forever Warlock raid model (level 60, single target, steady state).
 * Port of the reviewed Python model (review_check.py). Expected values, no RNG.
 * Budget: DoT/cooldown cast time + Nightfall Shadow Bolts + Life Tap time + filler time = 1 second.
 * Mana: everything is funded by Life Tap (no regen, no potions): the same limit for every spec.
 */
(function (root) {
  const GCD = 1.5;
  const ev = (c, bonus) => 1 + c * bonus;

  function solve(periodic, filler, lt, nf, ampFrac, shadowDotNames) {
    let A = 0, M = 0;
    for (const k in periodic) { const [, T, t, m] = periodic[k]; A += t / T; M += m / T; }
    const [dF, cF, mF, tps] = filler;
    let r0 = 0, r1 = 0, sbd = 0, sbm = 0;
    if (nf) { const [p, corrTps, d, m] = nf; r0 = p * corrTps; r1 = p * tps; sbd = d; sbm = m; }
    const k = GCD / lt;
    const f = (1 - A - GCD * r0 - k * (M + sbm * r0)) / (1 + GCD * r1 + k * (sbm * r1 + mF / cF));
    const parts = {};
    let shadowDots = 0;
    for (const n in periodic) {
      const [D, T] = periodic[n];
      parts[n] = D / T;
      if ((shadowDotNames || []).includes(n)) shadowDots += D / T;
    }
    parts.Filler = f * (dF / cF + (ampFrac || 0) * shadowDots);
    if (nf) parts['Nightfall'] = (r0 + r1 * f) * sbd;
    const dps = Object.values(parts).reduce((a, b) => a + b, 0);
    return { dps, parts, f };
  }

  // race: { crit, spMult, castSpeed, eureka }
  function raceMods(race, opts) {
    const r = { crit: 0, spMult: 1, castSpeed: 1, eureka: 0, spiritMult: 1 };
    if (race === 'human') { if (opts.sword) r.crit = 0.02; r.spiritMult = 1.05; }
    if (race === 'orc') r.spMult = 1 + 0.10 * 15 / 120;        // Blood Fury: +10% SP, 15 s every 2 min
    if (race === 'troll') r.castSpeed = 1 + 0.10 * 10 / 180;    // Berserking: casts only, not DoTs or channels
    if (race === 'gnome') r.eureka = 0.10 * 3 / 120;            // Eureka!: next 3 spells +10%, every 2 min
    return r;
  }

  function lifeTap(opts, rm, ilt) {
    const base = opts.lifeTapMode === 'spirit' ? 430 + opts.spirit * rm.spiritMult : 840;
    return base * (ilt ? 1.2 : 1.0);
  }

  function withEureka(res, fillerDmg, rm) {
    if (!rm.eureka) return res;
    const extra = rm.eureka * fillerDmg;          // 10% of 3 filler casts per 120 s
    res.parts.Racial = extra;
    res.dps += extra;
    return res;
  }

  function aff(o, bane, keepSuccubus) {
    const rm = raceMods(o.race, o);
    const sp = o.sp * rm.spMult, c = o.crit + rm.crit, cs = c + 0.05;
    const sh = (keepSuccubus ? 1.0 : 1.15) * 1.05, mal = 1.05, dc = ev(cs, 1.0);
    const P = {};
    P.Corruption = [(438 + 1.2 * sp) * sh * mal * 1.10 * dc, 18, GCD, 340];
    if (bane === 'BoA') P['Bane of Agony'] = [(552 + 1.596 * sp) * sh * mal * 1.10 * dc, 24, GCD, 215];
    else P['Bane of Doom'] = [(1742 + o.bodCoef * sp) * sh * mal * dc, 60, GCD, 300];
    P['Siphon Life'] = [(420 + 0.5 * sp) * sh * mal * dc, 30, GCD, 365];
    P.Immolate = [(159 + 0.2 * sp) * ev(c, 0.5) + (280 + 0.65 * sp) * mal * ev(c, 0.5), 15, 2.0, 380];
    const sb = (268 + 0.857 * sp) * sh * ev(cs, 0.5);
    const drains = 1.20 * 1.36;
    const F = [(222 + 0.858 * sp) * sh * mal * drains * dc, 6.0, 200, 1.0];   // Wrack
    const res = solve(P, F, lifeTap(o, rm, false), [0.04, 1 / 3, sb, 380], 0.10,
      ['Corruption', 'Bane of Agony', 'Bane of Doom', 'Siphon Life']);
    return withEureka(res, F[0], rm);
  }

  function destro(o, bane, version) {
    // version: 'sb' = Imp sac + Shadow Bolt (+Shadowburn); 'incin' = Succubus sac + Incinerate; 'keep' = Succubus out
    const rm = raceMods(o.race, o);
    const sp = o.sp * rm.spMult, c = o.crit + rm.crit;
    const aftermath = version !== 'sb';
    const sh = (version === 'sb' ? 1.15 : 1.0) * 1.10;
    const fi = (version === 'incin' ? 1.15 : 1.0) * 1.10;
    const AF = 1.10, mal = 1.02, cat = 0.9, dstr = ev(c, 1.0), dotc = ev(c, 0.5);
    const lt = lifeTap(o, rm, true);
    function build(isb) {
      const P = {};
      P.Corruption = [(438 + 1.2 * sp) * sh * mal * dotc * isb, 18, 2.0, 340];
      if (bane === 'BoA') P['Bane of Agony'] = [(552 + 1.596 * sp) * sh * mal * dotc * isb, 24, GCD, 215];
      else P['Bane of Doom'] = [(1742 + o.bodCoef * sp) * sh * mal * dotc * isb, 60, GCD, 300];
      const direct = (159 + 0.2 * sp) * (aftermath ? 1.5 : 1.0);
      P.Immolate = [(direct + (280 + 0.65 * sp) * mal) * fi * AF * dstr, 15, 1.5, 380 * cat];
      P.Conflagrate = [(282 + 0.429 * sp) * fi * AF * dstr, 10, GCD, 255 * cat];
      P.Shadowburn = [(266 + 0.429 * sp) * sh * AF * dstr * isb, 15, GCD, 365 * cat];
      const F = version === 'sb'
        ? [(268 + 0.857 * sp) * sh * AF * dstr * isb, 2.5 / rm.castSpeed, 380 * cat, 0]
        : [(217 + 0.714 * sp) * 1.25 * fi * AF * dstr, 2.0 / rm.castSpeed, 325 * cat, 0];
      return [P, F];
    }
    let [P, F] = build(1.0);
    let res = solve(P, F, lt);
    if (version === 'sb') {
      const n = o.isbDuration * res.f / (2.5 / rm.castSpeed);
      const u = 1 - Math.pow(1 - c, n);
      [P, F] = build(1 + 0.2 * u);
      res = solve(P, F, lt);
    }
    return withEureka(res, F[0], rm);
  }

  function demo(o, bane) {
    const rm = raceMods(o.race, o);
    const sp = o.sp * rm.spMult + 60, c = o.crit + rm.crit;    // Demonic Knowledge +60
    const sh = 1.15 * 1.10;                                     // Imp sac + Master Demonologist
    const allm = 1.03 * (o.gearHitCapped ? 1 : 0.95);           // Soul Link; no Suppression in this build
    const dstr = ev(c, 1.0), dotc = ev(c, 0.5), cat = 0.9;
    const lt = lifeTap(o, rm, false);
    function build(isb) {
      const P = {};
      P.Corruption = [(438 + 1.2 * sp) * sh * allm * dotc * isb, 18, 2.0, 340];
      if (bane === 'BoA') P['Bane of Agony'] = [(552 + 1.596 * sp) * sh * allm * dotc * isb, 24, GCD, 215];
      else P['Bane of Doom'] = [(1742 + o.bodCoef * sp) * sh * allm * dotc * isb, 60, GCD, 300];
      P.Immolate = [((159 + 0.2 * sp) + (280 + 0.65 * sp)) * allm * dstr, 15, 1.5, 380 * cat];
      const F = [(268 + 0.857 * sp) * sh * allm * dstr * isb, 2.5 / rm.castSpeed, 380 * cat, 0];
      return [P, F];
    }
    let [P, F] = build(1.0);
    const f0 = solve(P, F, lt).f;
    const u = 1 - Math.pow(1 - c, o.isbDuration * f0 / (2.5 / rm.castSpeed));
    [P, F] = build(1 + 0.2 * u);
    return withEureka(solve(P, F, lt), F[0], rm);
  }

  const SPECS = [
    { id: 'destro-fire', name: 'Destruction, Fire', note: 'Succubus sacrificed, Incinerate filler, Aftermath', pet: 0,
      run: (o, b) => destro(o, b, 'incin') },
    { id: 'destro-keep', name: 'Destruction, Fire + Succubus', note: 'Succubus kept out, Incinerate filler', pet: 1.0,
      run: (o, b) => destro(o, b, 'keep') },
    { id: 'destro-shadow', name: 'Destruction, Shadow (published)', note: 'Imp sacrificed, Shadow Bolt and Shadowburn', pet: 0,
      run: (o, b) => destro(o, b, 'sb') },
    { id: 'demo-pact', name: 'Demonology, Pact', note: 'Imp sacrificed, Succubus out, Shadow Bolt', pet: 1.156,
      run: (o, b) => demo(o, b) },
    { id: 'aff-sac', name: 'Affliction', note: 'Imp sacrificed, Wrack filler, Immolate kept up', pet: 0,
      run: (o, b) => aff(o, b, false) },
    { id: 'aff-keep', name: 'Affliction + Succubus', note: 'Succubus kept out, Wrack filler', pet: 1.0,
      run: (o, b) => aff(o, b, true) },
  ];

  function rank(o) {
    return SPECS.map(s => {
      const a = s.run(o, 'BoA'), d = s.run(o, 'BoD');
      const best = d.dps >= a.dps ? { r: d, bane: 'Bane of Doom' } : { r: a, bane: 'Bane of Agony' };
      const pet = s.pet * o.petDps;
      const total = best.r.dps + pet;
      return { id: s.id, name: s.name, note: s.note, bane: best.bane, lock: best.r.dps, pet, total,
               petShare: total ? pet / total : 0, parts: best.r.parts, filler: best.r.f };
    }).sort((x, y) => y.total - x.total);
  }

  const api = { rank, aff, destro, demo, SPECS };
  if (typeof module !== 'undefined') module.exports = api; else root.WarlockModel = api;
})(this);
