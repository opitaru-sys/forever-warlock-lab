"""Regenerate the raid parity data from models/raid_model.py, the reference.

1. Rewrites the EXPECTED table in tests/parity_test.js (54 cases: SP 300/500/800 x crit 5/10/20%, no options).
2. Writes tests/raid_options_fixtures.json: every spec function and rank() (totals, order, viability, deep
   Demonology's execute plan) under the v8 options, the deep Demonology spec, and v8.4's trainer ranks
   (trainerRanks: Shadow Bolt 9, Corruption 6, Immolate 7 instead of the Ruins of Ahn'Qiraj book ranks).

Run from the repo root: python tests/make_raid_fixtures.py
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'models'))
import raid_model as R  # noqa: E402

SPECS = R.SPEC_IDS

# Each case: JS option overrides on top of tests' base options (race none, Life Tap 840, ISB 12 s, BoD x4).
CASES = [
    {'sp': 500, 'crit': 0.10},
    {'sp': 500, 'crit': 0.10, 'gearHit': 0.14},
    {'sp': 300, 'crit': 0.10, 'fireImmune': True},
    {'sp': 500, 'crit': 0.10, 'fireImmune': True},
    {'sp': 800, 'crit': 0.20, 'fireImmune': True},
    {'sp': 300, 'crit': 0.05, 'execute': True},
    {'sp': 500, 'crit': 0.10, 'execute': True},
    {'sp': 800, 'crit': 0.20, 'execute': True},
    {'sp': 500, 'crit': 0.10, 'execute': 0.5, 'impDps': 30},
    {'sp': 500, 'crit': 0.10, 'execute': True, 'impDps': 90},
    {'sp': 500, 'crit': 0.10, 'coe': True},
    {'sp': 800, 'crit': 0.05, 'coe': True, 'execute': True},
    {'sp': 500, 'crit': 0.10, 'mp5': 50},
    {'sp': 500, 'crit': 0.10, 'mp5': 150},
    {'sp': 300, 'crit': 0.20, 'mp5': 1000},
    {'sp': 300, 'crit': 0.10, 'targets': 2},
    {'sp': 500, 'crit': 0.10, 'targets': 2},
    {'sp': 800, 'crit': 0.20, 'targets': 2},
    {'sp': 500, 'crit': 0.10, 'targets': 2, 'coe': True, 'mp5': 80, 'execute': True},
    {'sp': 500, 'crit': 0.10, 'targets': 2, 'fireImmune': True, 'execute': True},
    {'sp': 500, 'crit': 0.10, 'petDps': 100, 'coe': True, 'fireImmune': True, 'mp5': 60},
    {'sp': 500, 'crit': 0.10, 'petDps': 0, 'execute': True},
    {'sp': 500, 'crit': 0.10, 'petDps': 0, 'impDps': 0, 'execute': True, 'targets': 2},
    {'sp': 500, 'crit': 0.10, 'shadowburn': False},
    {'sp': 800, 'crit': 0.20, 'shadowburn': False, 'targets': 2, 'coe': True},
    {'sp': 300, 'crit': 0.10, 'shadowburn': False, 'fireImmune': True},
    {'sp': 500, 'crit': 0.10, 'brandHits': 0},
    {'sp': 500, 'crit': 0.10, 'brandHits': 0, 'execute': True},
    {'sp': 500, 'crit': 0.10, 'brandHits': 3, 'execute': True},
    {'sp': 300, 'crit': 0.05, 'brandScaling': 'pet'},
    {'sp': 800, 'crit': 0.10, 'brandHits': 3, 'brandScaling': 'pet', 'execute': True, 'impDps': 60},
    {'sp': 500, 'crit': 0.10, 'lifeTapMode': 'spirit', 'spirit': 100},
    {'sp': 500, 'crit': 0.10, 'lifeTapMode': 'spirit', 'spirit': 100, 'shadowburn': False, 'brandHits': 3},
    {'sp': 800, 'crit': 0.10, 'lifeTapMode': 'spirit', 'spirit': 250, 'mp5': 100, 'execute': True, 'targets': 2},
    {'sp': 500, 'crit': 0.10, 'consumables': True},
    {'sp': 300, 'crit': 0.20, 'consumables': True, 'mp5': 1000},
    {'sp': 500, 'crit': 0.10, 'lifeTapMode': 'spirit', 'spirit': 100, 'consumables': True, 'brandHits': 3},
    {'sp': 500, 'crit': 0.10, 'lifeTapMode': 'spirit', 'spirit': 100, 'consumables': True, 'mp5': 40, 'coe': True, 'brandHits': 0},
    {'sp': 800, 'crit': 0.10, 'lifeTapMode': 'spirit', 'spirit': 100, 'consumables': True, 'fireImmune': True,
     'execute': True, 'targets': 2},
    {'sp': 500, 'crit': 0.10, 'execute': True, 'impDps': 150},
    {'sp': 300, 'crit': 0.10, 'execute': 0.5, 'petDps': 10, 'brandHits': 0},
    {'sp': 500, 'crit': 0.10, 'lifeTapMode': 'spirit', 'spirit': 100, 'consumables': True, 'brandHits': 3, 'execute': True},
    {'sp': 500, 'crit': 0.10, 'lifeTapMode': 'spirit', 'spirit': 100, 'consumables': True, 'brandHits': 3, 'execute': True,
     'fireImmune': True},
    # v8.4: the trainer's level-60 ranks, which the page uses unless the books box is ticked
    {'sp': 500, 'crit': 0.10, 'trainerRanks': True},
    {'sp': 500, 'crit': 0.10, 'lifeTapMode': 'spirit', 'spirit': 100, 'consumables': True, 'brandHits': 3, 'execute': True, 'trainerRanks': True},
    {'sp': 500, 'crit': 0.10, 'lifeTapMode': 'spirit', 'spirit': 100, 'consumables': True, 'brandHits': 0, 'execute': True, 'trainerRanks': True},
    {'sp': 500, 'crit': 0.10, 'lifeTapMode': 'spirit', 'spirit': 100, 'consumables': True, 'brandHits': 6, 'execute': True, 'trainerRanks': True},
    {'sp': 500, 'crit': 0.10, 'lifeTapMode': 'spirit', 'spirit': 100, 'consumables': True, 'brandHits': 3, 'execute': True, 'fireImmune': True,
     'trainerRanks': True},
    {'sp': 800, 'crit': 0.20, 'targets': 2, 'coe': True, 'mp5': 80, 'execute': True, 'trainerRanks': True},
    {'sp': 300, 'crit': 0.05, 'lifeTapMode': 'spirit', 'spirit': 100, 'consumables': True, 'brandHits': 3, 'shadowburn': False, 'trainerRanks': True},
]


def py_opts(case):
    """JS option names to raid_model keyword arguments."""
    opts = {}
    if case.get('fireImmune'):
        opts['fire_immune'] = True
    if case.get('coe'):
        opts['coe'] = True
    if case.get('consumables'):
        opts['consumables'] = True
    if 'mp5' in case:
        opts['mp5'] = case['mp5']
    if 'targets' in case:
        opts['targets'] = case['targets']
    if case.get('lifeTapMode') == 'spirit':
        opts['life_tap'] = 430 + case['spirit']      # race none: no Human Spirit bonus
    if 'shadowburn' in case:
        opts['shadowburn'] = case['shadowburn']
    if 'brandHits' in case:
        opts['brand_hits'] = case['brandHits']
    if 'brandScaling' in case:
        opts['brand_scaling'] = case['brandScaling']
    if case.get('trainerRanks'):
        opts['trainer_ranks'] = R.TRAINER_SPELLS
    return opts


def case_values(case):
    sp, c = case['sp'], case['crit']
    gear_hit = case.get('gearHit', 0.11)
    execute = case.get('execute', 0.0)
    opts = py_opts(case)
    pet, imp = case.get('petDps', 50.0), case.get('impDps')
    funcs = {f'{s}|{b}': round(R.spec_lock(s, sp, c, b, gear_hit, execute, pet, imp, **opts), 4)
             for s in SPECS for b in ('BoA', 'BoD')}
    ranked = R.rank(sp, c, pet, imp, gear_hit, execute, **opts)
    return {'opts': case, 'funcs': funcs,
            'rank': [{'id': r['id'], 'viable': r['viable'], 'total': round(r['total'], 4), 'execPlan': r['exec_plan']}
                     for r in ranked]}


def parity_table():
    rows = []
    for sp in (300, 500, 800):
        for c in (0.05, 0.10, 0.20):
            v = [R.aff(sp, c, bane='BoD', immolate=True)[0],
                 R.aff(sp, c, bane='BoA', sac_imp=False, immolate=True)[0],
                 R.destro(sp, c, version='incin', aftermath=True)[0],
                 R.destro(sp, c, version='keep', aftermath=True)[0],
                 R.destro(sp, c, version='sb', shadowburn=True)[0],
                 R.demo(sp, c, immolate=True)[0]]      # Pact 5/31/15: Suppression caps hit at 11% gear
            rows.append(f"  '{sp},{c:.2f}': [" + ', '.join(f'{x:.1f}' for x in v) + '],')
    return '\n'.join(rows)


def main():
    path = os.path.join(HERE, 'parity_test.js')
    with open(path, newline='') as fh:
        src = fh.read()
    eol = '\r\n' if '\r\n' in src else '\n'
    table = parity_table().replace('\n', eol)
    new, n = re.subn(r'(const EXPECTED = \{' + re.escape(eol) + r').*?(' + re.escape(eol) + r'\};)',
                     lambda m: m.group(1) + table + m.group(2), src, flags=re.S)
    if n != 1:
        raise SystemExit('EXPECTED block not found in parity_test.js')
    with open(path, 'w', newline='') as fh:
        fh.write(new)
    fixtures = {'generated_by': 'tests/make_raid_fixtures.py', 'cases': [case_values(c) for c in CASES]}
    with open(os.path.join(HERE, 'raid_options_fixtures.json'), 'w', newline='\r\n') as fh:
        json.dump(fixtures, fh, indent=1)
        fh.write('\n')
    print(parity_table())
    print(f'wrote {len(CASES)} option cases')


if __name__ == '__main__':
    main()
