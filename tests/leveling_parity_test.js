// Checks leveling.js against the Python leveling model on a grid of levels, builds, pets and gear.
// Run from the repo root: node tests/leveling_parity_test.js
// Regenerate the fixtures with: python tests/make_leveling_fixtures.py
const m = require('../leveling.js');
const cases = require('./leveling_fixtures.json');
let failed = 0;
for (const c of cases) {
  const r = m.evaluate(c.level, c.talents, c.pet, c.sp, { aggro: c.aggro });
  const ok = r.policy === c.policy && Math.abs(r.spk - c.spk) < 1e-6 && Math.abs(r.ttk - c.ttk) < 1e-6 &&
             Math.abs(r.rest - c.rest) < 1e-6 && Math.abs(r.healed - c.healed) < 1e-6;
  if (!ok) {
    failed++;
    if (failed <= 10) console.log('FAIL', c.level, c.build, c.pet, 'sp', c.sp, 'aggro', c.aggro,
      '| py', c.policy, c.spk.toFixed(6), '| js', r.policy, r.spk.toFixed(6));
  }
}
if (failed) { console.log(`\n${failed} of ${cases.length} leveling cases failed`); process.exit(1); }
console.log(`All ${cases.length} leveling cases match the Python model.`);
