// Parity check: model.js (used by index.html) against models/raid_model.py (the reviewed model).
// Runs the same 6 builds across a 3x3 grid of spell power and crit chance and compares the
// output to values pre-computed from models/raid_model.py, rounded to 0.1. Exits non-zero
// if any cell is off by more than 0.05 dps.
const path = require('path');
const m = require(path.join(__dirname, '..', 'model.js'));

// SP rows x crit columns. Column order matches the JS call shapes below:
//   aff(o,'BoD',false)   aff(o,'BoA',true)   destro(o,'BoD','incin')
//   destro(o,'BoD','keep')   destro(o,'BoD','sb')   demo(o,'BoD')
const EXPECTED = {
  '300,0.05': [325.8, 282.9, 401.5, 367.5, 373.3, 350.5],
  '300,0.10': [339.1, 294.3, 418.1, 382.5, 392.1, 371.2],
  '300,0.20': [365.7, 317.2, 451.4, 412.5, 430.0, 412.1],
  '500,0.05': [422.1, 368.0, 511.2, 467.8, 475.0, 446.8],
  '500,0.10': [439.4, 382.9, 532.3, 486.9, 498.9, 473.2],
  '500,0.20': [473.9, 412.8, 574.6, 525.0, 547.3, 525.5],
  '800,0.05': [566.6, 495.8, 675.7, 618.3, 627.6, 591.2],
  '800,0.10': [589.8, 515.9, 703.6, 643.5, 659.1, 626.3],
  '800,0.20': [636.3, 556.2, 759.4, 693.8, 723.1, 695.7],
};

const TOLERANCE = 0.05;
const SP_VALUES = [300, 500, 800];
const CRIT_VALUES = [0.05, 0.10, 0.20];

function baseOpts(sp, crit) {
  return {
    sp, crit,
    race: 'none',
    sword: false,
    lifeTapMode: '840',
    spirit: 100,
    bodCoef: 4.0,
    isbDuration: 12,
    gearHitCapped: false,
    petDps: 0,
  };
}

let failures = 0;
let checked = 0;

for (const sp of SP_VALUES) {
  for (const crit of CRIT_VALUES) {
    const o = baseOpts(sp, crit);
    const got = [
      m.aff(o, 'BoD', false).dps,
      m.aff(o, 'BoA', true).dps,
      m.destro(o, 'BoD', 'incin').dps,
      m.destro(o, 'BoD', 'keep').dps,
      m.destro(o, 'BoD', 'sb').dps,
      m.demo(o, 'BoD').dps,
    ];
    const key = `${sp},${crit.toFixed(2)}`;
    const expected = EXPECTED[key];
    if (!expected) {
      console.error(`No expected row for ${key}`);
      failures++;
      continue;
    }
    const labels = ['aff sac BoD', 'aff keep BoA', 'destro incin BoD', 'destro keep BoD', 'destro sb BoD', 'demo BoD'];
    for (let i = 0; i < expected.length; i++) {
      checked++;
      const diff = Math.abs(got[i] - expected[i]);
      if (diff > TOLERANCE) {
        console.error(`MISMATCH sp=${sp} crit=${crit} ${labels[i]}: got ${got[i].toFixed(3)} expected ${expected[i]} (diff ${diff.toFixed(3)})`);
        failures++;
      }
    }
    console.log(`sp=${sp} crit=${crit}: ` + got.map((v) => v.toFixed(1)).join(' '));
  }
}

if (failures > 0) {
  console.error(`\n${failures} mismatch(es) out of ${checked} checks.`);
  process.exit(1);
}
console.log(`\nAll ${checked} checks passed (tolerance ${TOLERANCE}).`);
