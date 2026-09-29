// Checks for the gear-hit slider, stat weights and item comparison added in v3.
// Run from the repo root: node tests/weights_test.js
const m = require('../model.js');

let failed = 0;
const check = (label, ok, detail) => {
  console.log((ok ? 'ok   ' : 'FAIL ') + label + (detail ? '  ' + detail : ''));
  if (!ok) failed++;
};
const close = (a, b, tol) => Math.abs(a - b) <= tol;

const base = { sp: 500, crit: 0.10, race: 'none', sword: false, lifeTapMode: '840', spirit: 100,
               bodCoef: 4.0, isbDuration: 12, petDps: 0 };

// 1. The hit slider reproduces the reviewed defaults.
const legacy = m.rank(Object.assign({}, base, { gearHitCapped: false }));
const slider = m.rank(Object.assign({}, base, { gearHit: 0.11 }));
legacy.forEach(l => {
  const s = slider.find(x => x.id === l.id);
  check('gearHit 0.11 equals reviewed default: ' + l.id, close(l.total, s.total, 1e-9), l.total.toFixed(2));
});
const capped = m.rank(Object.assign({}, base, { gearHitCapped: true })).find(x => x.id === 'demo-pact');
const capped2 = m.rank(Object.assign({}, base, { gearHit: 0.16 })).find(x => x.id === 'demo-pact');
check('gearHit 0.16 equals gearHitCapped for Demonology', close(capped.total, capped2.total, 1e-9));

// 2. Hit below the cap costs damage linearly; hit above the cap is worth nothing.
const a0 = m.specTotal(Object.assign({}, base, { gearHit: 0.0 }), 'destro-fire');
const a11 = m.specTotal(Object.assign({}, base, { gearHit: 0.11 }), 'destro-fire');
check('Destruction at 0% gear hit loses 11% vs capped', close(a0 / a11, 0.89, 1e-9), (a0 / a11).toFixed(4));
const a20 = m.specTotal(Object.assign({}, base, { gearHit: 0.20 }), 'destro-fire');
check('hit above cap adds nothing', close(a20, a11, 1e-9));

// 3. Stat weights are positive and sane.
m.SPECS.forEach(s => {
  const w = m.statWeights(Object.assign({}, base, { gearHit: 0.08 }), s.id);
  check('weights positive: ' + s.id, w.sp > 0 && w.crit > 0 && w.hit > 0,
        `1 SP ${w.sp.toFixed(3)} dps, 1% crit ${w.crit.toFixed(2)} dps = ${w.critInSp.toFixed(1)} SP, 1% hit ${w.hit.toFixed(2)} dps = ${w.hitInSp.toFixed(1)} SP`);
});
const wc = m.statWeights(Object.assign({}, base, { gearHit: 0.16 }), 'destro-fire');
check('hit weight is zero at the cap', wc.hit === 0);

// 4. Item comparison: swapping an item for itself changes nothing; more spell power helps.
const same = m.compareItems(Object.assign({}, base, { gearHit: 0.11 }), 'destro-fire', { sp: 30, crit: 0.01, hit: 0 }, { sp: 30, crit: 0.01, hit: 0 });
check('identical swap is zero', close(same.diff, 0, 1e-9));
const up = m.compareItems(Object.assign({}, base, { gearHit: 0.11 }), 'destro-fire', { sp: 20, crit: 0, hit: 0 }, { sp: 40, crit: 0, hit: 0 });
check('+20 spell power swap is positive', up.diff > 0, up.diff.toFixed(2) + ' dps');

if (failed) { console.log(`\n${failed} check(s) failed`); process.exit(1); }
console.log('\nAll weight checks passed.');
