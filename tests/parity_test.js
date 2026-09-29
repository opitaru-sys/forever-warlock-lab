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
  '300,0.05': [332.5, 285.7, 402.1, 368.0, 373.8, 350.9],
  '300,0.10': [346.1, 297.2, 418.8, 383.1, 392.6, 371.6],
  '300,0.20': [373.3, 320.3, 452.1, 413.1, 430.6, 412.5],
  '500,0.05': [430.0, 371.0, 511.8, 468.4, 475.5, 447.2],
  '500,0.10': [447.6, 386.1, 533.0, 487.5, 499.4, 473.7],
  '500,0.20': [482.8, 416.2, 575.3, 525.7, 547.8, 526.0],
  '800,0.05': [576.2, 499.0, 676.3, 618.8, 628.1, 591.7],
  '800,0.10': [599.9, 519.3, 704.3, 644.0, 659.7, 626.7],
  '800,0.20': [647.2, 559.9, 760.1, 694.4, 723.7, 696.2],
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
