"""Does the leveling filler conclusion survive changes in the uncertain assumptions? (v8)

Run from the repo root: python analysis/filler_robustness.py
243 scenarios per level: wand damage x0.6/1/1.3, pet damage x0.5/1/2, mob health x0.7/1/1.3, rest speed x0.5/1/2,
spell power 0.5/1/2 x level. Each scenario takes the best rotation from evaluate() (modifiers included, averaged
over mob HP x0.8 to x1.2 around the scaled health) for the page planner's build, and counts its filler.
"""
import os
import sys
import itertools
from collections import Counter

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "models"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from character import HP_GRID
from filler_by_level import aff_build, filler_family, FAMILIES
from leveling_paths import spk_many

GRID = list(itertools.product((0.6, 1.0, 1.3), (0.5, 1.0, 2.0), (0.7, 1.0, 1.3), (0.5, 1.0, 2.0), (0.5, 1.0, 2.0)))


def job(L, wand_mult, pet_mult, hp_mult, rest_mult, sp):
    tal = aff_build(L)
    rr = (2.2 * L + 1.2 * L * (1 + .1 * tal.get('ImprovedLifeTap', 0))) * rest_mult
    return (L, tal, sp, dict(char_mult={'wand_dps': wand_mult, 'pet_dps': pet_mult},
                             hp_mults=tuple(hp_mult * m for m in HP_GRID), rest_rate=rr))


if __name__ == "__main__":
    levels = (20, 30, 40, 50, 60)
    res = spk_many([job(L, *g) for L in levels for g in GRID])
    print('| L | ' + ' | '.join(FAMILIES) + ' | of |')
    print('|---|' + '---|' * (len(FAMILIES) + 1))
    for i, L in enumerate(levels):
        cnt = Counter(filler_family(n) for _, n in res[i * len(GRID):(i + 1) * len(GRID)])
        print(f'| {L} | ' + ' | '.join(f'{cnt[f]} ({100 * cnt[f] / len(GRID):.0f}%)' for f in FAMILIES) + f' | {len(GRID)} |')
