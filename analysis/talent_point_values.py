"""What one talent point is worth in seconds per kill, for the page planner's builds (v8).

Run from the repo root: python analysis/talent_point_values.py
For a talent in the build: take all its points out (if the build stays legal) and report how much slower each point
leaves you. For a talent not in the build: add its points on top (a what-if, ignoring the level's point budget).
Best rotation from evaluate() (modifiers included), averaged over mob HP x0.8 to x1.2, Voidwalker, SP 1.0.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "models"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from character import valid, AFF, DEMO, DESTRO
from leveling_paths import page_build, spk_many

MAX = {k: m for tree in (AFF, DEMO, DESTRO) for k, (r, m) in tree.items()}
PROBE = ['Malediction', 'ShadowMastery', 'Pandemic', 'Malevolence', 'ImprovedBoA', 'Nightfall', 'SoulSiphon', 'ImprovedDrains',
         'UnholyPower', 'DemonicKnowledge', 'SiphonLife', 'SoulHarvesting', 'ImprovedLifeTap', 'Suppression', 'AmplifyCurse',
         'DemonicEmbrace', 'FelVitality', 'Wrack', 'Bane', 'Cataclysm', 'Aftermath', 'MoltenSkin']


def variants(base):
    out = []
    for k in PROBE:
        if base.get(k):
            t = {j: v for j, v in base.items() if j != k}
            if valid(t):
                out.append((k, t, -base[k]))
        else:
            t = dict(base, **{k: MAX[k]})
            if valid(t):
                out.append((k, t, MAX[k]))
    return out


if __name__ == "__main__":
    for L in (30, 45, 60):
        base = page_build(L)
        vs = variants(base)
        res = spk_many([(L, base, 1.0, {})] + [(L, t, 1.0, {}) for _, t, _ in vs])
        b = res[0][0]
        rows = []
        for (k, _, n), (a, rot) in zip(vs, res[1:]):
            per = (b / a - 1) * 100 / n if n > 0 else (a / b - 1) * 100 / -n
            rows.append((per, k, n, a, rot))
        print(f'\n### Level {L}, page planner build ({b:.2f} s per kill, {res[0][1]}): % faster per point\n')
        print('| talent | points | seconds per kill | % per point | rotation |')
        print('|---|---|---|---|---|')
        for per, k, n, a, rot in sorted(rows, reverse=True):
            print(f"| {k} | {'+' if n > 0 else ''}{n} | {a:.2f} | {per:+.2f}% | {rot} |")
