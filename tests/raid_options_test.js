// Parity for the v8 raid options (fireImmune, execute, coe, mp5, consumables, targets, impDps, shadowburn,
// brandHits, brandScaling, Life Tap 430 + Spirit, and v8.4's trainerRanks) and the deep Demonology spec: model.js
// against models/raid_model.py.
// Expected values live in raid_options_fixtures.json (python tests/make_raid_fixtures.py regenerates them).
// Checks every spec function with both Banes, rank() totals, order and viability, and that statWeights and
// compareItems carry the options. Run from the repo root: node tests/raid_options_test.js
const path = require('path');
const m = require(path.join(__dirname, '..', 'model.js'));
const fixtures = require(path.join(__dirname, 'raid_options_fixtures.json'));

const TOLERANCE = 0.001;
let failed = 0, checked = 0;
const check = (label, ok, detail) => {
  checked++;
  if (!ok) { failed++; console.error('FAIL ' + label + (detail ? '  ' + detail : '')); }
};

function baseOpts(sp, crit) {
  return { sp, crit, race: 'none', sword: false, lifeTapMode: '840', spirit: 100, bodCoef: 4.0, isbDuration: 12,
           gearHitCapped: false, petDps: 50 };
}

const RUN = {
  'destro-fire': (o, b) => m.destro(o, b, 'incin'),
  'destro-keep': (o, b) => m.destro(o, b, 'keep'),
  'destro-shadow': (o, b) => m.destro(o, b, 'sb'),
  'demo-pact': (o, b) => m.demo(o, b),
  'demo-deep': (o, b) => m.demoDeep(o, b),
  'aff-sac': (o, b) => m.aff(o, b, false),
  'aff-keep': (o, b) => m.aff(o, b, true),
};

fixtures.cases.forEach(cs => {
  const o = Object.assign(baseOpts(cs.opts.sp, cs.opts.crit), cs.opts);
  const tag = JSON.stringify(cs.opts);
  for (const key in cs.funcs) {
    const [spec, bane] = key.split('|');
    const got = RUN[spec](o, bane).dps;
    check(`${tag} ${key}`, Math.abs(got - cs.funcs[key]) <= TOLERANCE, `got ${got.toFixed(4)} expected ${cs.funcs[key]}`);
  }
  const ranked = m.rank(o);
  cs.rank.forEach((exp, i) => {
    const r = ranked[i];
    check(`${tag} rank #${i + 1}`, r.id === exp.id && r.viable === exp.viable && Math.abs(r.total - exp.total) <= TOLERANCE
      && r.execPlan === exp.execPlan,
      `got ${r.id} ${r.viable} ${r.total.toFixed(4)} ${r.execPlan} expected ${exp.id} ${exp.viable} ${exp.total} ${exp.execPlan}`);
    if (!r.viable) check(`${tag} ${r.id} carries a reason`, typeof r.reason === 'string' && r.reason.length > 0);
  });
  const deep = ranked.find(r => r.id === 'demo-deep');
  console.log(`ok   ${tag}  #1 ${ranked[0].id} ${ranked[0].total.toFixed(1)}${deep.execPlan ? ', deep execute plan ' + deep.execPlan : ''}`);
});

// statWeights and compareItems pass the options through.
const base = baseOpts(500, 0.10);
const withOpts = Object.assign({}, base, { targets: 2, coe: true, mp5: 80, consumables: true, execute: true, brandHits: 3 });
m.SPECS.forEach(s => {
  const direct = m.specTotal(withOpts, s.id);
  const swap = m.compareItems(withOpts, s.id, { sp: 30, crit: 0, hit: 0 }, { sp: 30, crit: 0, hit: 0 });
  check('compareItems base carries options: ' + s.id, Math.abs(swap.base - direct) < 1e-9);
  const w = m.statWeights(withOpts, s.id);
  const up = m.specTotal(Object.assign({}, withOpts, { sp: 510 }), s.id) - m.specTotal(Object.assign({}, withOpts, { sp: 490 }), s.id);
  check('statWeights carries options: ' + s.id, Math.abs(w.sp - up / 20) < 1e-9);
});
const fi = Object.assign({}, base, { fireImmune: true });
check('fire-immune Fire spec total is 0', m.specTotal(fi, 'destro-fire') === 0);
check('fire-immune Fire spec weight is 0', m.statWeights(fi, 'destro-keep').sp === 0);
check('fire-immune Fire specs rank last', m.rank(fi).slice(-2).every(r => !r.viable));
// consumables are 3 potions and 3 runes over 300 s: 9,000 mana, the same as 150 mp5.
m.SPECS.forEach(s => check('consumables equal 150 mp5: ' + s.id,
  Math.abs(m.specTotal(Object.assign({}, base, { consumables: true }), s.id) - m.specTotal(Object.assign({}, base, { mp5: 150 }), s.id)) < 1e-9));

if (failed) { console.error(`\n${failed} of ${checked} option checks failed`); process.exit(1); }
console.log(`\nAll ${checked} option checks passed (tolerance ${TOLERANCE}).`);
