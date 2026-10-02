// Checks the talent builder's preset orders and talent table (added in v8.5).
// fromOrder() in src/builder.js looks talents up by display name and silently drops a name it cannot find, so a
// rename that misses one order (Soul Harvesting became Soul Harvest on 1 Oct 2026) would quietly shrink a preset.
// Saved builds use the talent keys and #b- share links use the table's order, so keys must stay what the model reads.
// Run from the repo root: node tests/preset_names_test.js
const fs = require('fs');
const path = require('path');
const vm = require('vm');
const lv = require('../leveling.js');

let failed = 0;
const check = (label, ok, detail) => {
  console.log((ok ? 'ok   ' : 'FAIL ') + label + (detail ? '  ' + detail : ''));
  if (!ok) failed++;
};
const read = rel => fs.readFileSync(path.join(__dirname, '..', rel), 'utf8');
const builder = read('src/builder.js');
const page = read('src/page.src.html');

// The talent table, evaluated as the plain literal it is.
const tm = builder.match(/const TALENTS = (\[[\s\S]*?\r?\n  \]);/);
const TALENTS = tm ? vm.runInNewContext('(' + tm[1] + ')') : [];
check('talent table found', TALENTS.length > 0, TALENTS.length + ' talents');
const byName = new Map(TALENTS.map(x => [x.n, x]));
check('talent names are unique', byName.size === TALENTS.length);
check('talent keys are unique', new Set(TALENTS.map(x => x.k)).size === TALENTS.length);

// Every key is one the leveling model reads, and the other way round.
const modelKeys = Object.keys(Object.assign({}, lv.AFF, lv.DEMO, lv.DESTRO));
const builderKeys = TALENTS.map(x => x.k);
const unknownKeys = builderKeys.filter(k => !modelKeys.includes(k));
const missingKeys = modelKeys.filter(k => !builderKeys.includes(k));
check('every builder key is a leveling.js talent', !unknownKeys.length, unknownKeys.join(', '));
check('every leveling.js talent is in the builder', !missingKeys.length, missingKeys.join(', '));

// #b- share links store one rank per talent by table position, and saved builds store ranks by key. Pin both, so a
// reorder or a key rename fails here. This is the v8.4 order (4f67f88); a new talent goes at the end, on purpose.
const KEY_ORDER = (
  'ImprovedLifeTap Suppression ImprovedCorruption Malediction SoulHarvesting ImprovedDrains ImprovedBoA ' +
  'FelConcentration AmplifyCurse Pandemic Malevolence Nightfall CurseOfExhaustion SiphonLife SoulSiphon ' +
  'ShadowMastery Wrack ImprovedHealthFunnel ImprovedImp DemonicEmbrace UnholyPower DemonicAegis ' +
  'ImprovedVoidwalker FelVitality DemonicEnergies ImprovedSayaad DemonicSacrifice MasterSummoner ' +
  'Decimation FelDomination DemonicBrand ImprovedFelhunter SoulLink DemonicKnowledge MasterDemonologist ' +
  'DemonicPact DestructiveReach ImprovedShadowBolt Bane MoltenSkin Cataclysm Aftermath Ruin Shadowburn ' +
  'Intensity AgonizingFlames Conflagrate Pyroclasm BaneOfHavoc FireAndBrimstone ShadowAndFlame ' +
  'Incinerate').split(' ');
const firstMoved = KEY_ORDER.findIndex((k, i) => builderKeys[i] !== k);
check('talent keys keep their share-link order', firstMoved < 0 && builderKeys.length === KEY_ORDER.length,
  firstMoved >= 0 ? 'position ' + firstMoved + ': ' + builderKeys[firstMoved] + ' where ' + KEY_ORDER[firstMoved] + ' was'
    : builderKeys.length + ' talents, ' + KEY_ORDER.length + ' pinned');

// Share links carry one digit per talent; the decoder's length must match the table.
const lm = builder.match(/\(\[0-5\]\{(\d+)\}\)/);
check('share link length matches the talent table', lm && Number(lm[1]) === TALENTS.length,
  (lm ? lm[1] : 'none') + ' digits, ' + TALENTS.length + ' talents');

// Every preset order in builder.js and the page plan orders in page.src.html.
const seq = pairs => pairs.flatMap(([n, c]) => Array(c).fill(n));
const ORDERS = {};
for (const src of [builder, page]) {
  for (const m of src.matchAll(/const (\w+) = seq\((\[[\s\S]*?\])\);/g)) ORDERS[m[1]] = seq(vm.runInNewContext(m[2]));
}
const used = new Set();
for (const m of builder.matchAll(/fromOrder\(([^,]+),/g)) {
  for (const id of m[1].match(/\b(?:ORDER_\w+|TAL_ORDER|SOLO56)\b/g) || []) used.add(id);
}
check('preset orders found', used.size >= 7, [...used].join(', '));
used.forEach(id => check('order defined: ' + id, Array.isArray(ORDERS[id])));

Object.entries(ORDERS).forEach(([id, order]) => {
  const bad = [...new Set(order.filter(n => !byName.has(n)))];
  check('every name resolves: ' + id, !bad.length, bad.length ? 'unknown: ' + bad.join(', ') : order.length + ' points');
  const counts = {};
  order.forEach(n => { counts[n] = (counts[n] || 0) + 1; });
  const over = Object.entries(counts).filter(([n, c]) => byName.has(n) && c > byName.get(n).m).map(([n, c]) => n + ' ' + c);
  check('no talent past its max rank: ' + id, !over.length, over.join(', '));
});

if (failed) { console.log(`\n${failed} preset checks failed`); process.exit(1); }
console.log('\nAll preset checks passed.');
