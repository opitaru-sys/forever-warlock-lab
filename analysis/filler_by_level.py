"""Which filler wins, level by level, for the page planner's build (v8).

Run from the repo root: python analysis/filler_by_level.py
For each filler (wand, Drain Life, Shadow Bolt, Searing Pain) the best rotation that uses it, with the curse,
finisher and Death Coil modifiers, averaged over mob HP x0.8 to x1.2. Voidwalker. Lower is better.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "models"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from character import POLICIES
from leveling_paths import page_build, spk_many

FILLER_NAMES = {'Wand': 'wand', 'DrainLife': 'Drain Life', 'ShadowBolt': 'Shadow Bolt', 'SearingPain': 'Searing Pain',
                'Incinerate': 'Incinerate'}
FAMILIES = ('wand', 'Drain Life', 'Shadow Bolt', 'Searing Pain')


def filler_family(name):
    """The filler of a rotation name from evaluate(), e.g. 'DoTs+Imm+Wrack+DL +Death Coil' -> 'Drain Life'."""
    return FILLER_NAMES[POLICIES[name.split(' +')[0]]['prio'][-1]]


def family_policies(fam):
    return {k: v for k, v in POLICIES.items() if filler_family(k) == fam}


def aff_build(L):
    """The page planner's build at level L (kept under this name for filler_robustness.py)."""
    return page_build(L)


if __name__ == "__main__":
    levels = (20, 30, 40, 50, 60)
    for sp in (0.5, 1.0, 2.0):
        jobs = [(L, aff_build(L), sp, dict(policies=family_policies(f))) for L in levels for f in FAMILIES]
        res = spk_many(jobs)
        print(f'\n### Best rotation per filler, SP {sp} x level (seconds per kill)\n')
        print('| L | ' + ' | '.join(FAMILIES) + ' | winner |')
        print('|---|' + '---|' * (len(FAMILIES) + 1))
        for i, L in enumerate(levels):
            r = res[len(FAMILIES) * i:len(FAMILIES) * (i + 1)]
            w = min(range(len(r)), key=lambda j: r[j][0])
            print(f'| {L} | ' + ' | '.join(f'{a:.2f} {b}' for a, b in r) + f' | {FAMILIES[w]} |')
