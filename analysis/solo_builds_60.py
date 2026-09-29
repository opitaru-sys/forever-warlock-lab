"""Level 60 solo builds: the Demonic Knowledge splash against deep Affliction and the drain tank (v8).

Run from the repo root: python analysis/solo_builds_60.py
Best rotation from evaluate() (modifiers included), averaged over mob HP x0.8 to x1.2, Voidwalker, at spell power
1, 2 and 3 x level, with full and halved pet damage.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "models"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from character import valid
from leveling_paths import SOLO56, SOLO56_V8, build, spk_many


def rep(*p):
    d = {}
    for k, n in p:
        d[k] = d.get(k, 0) + n
    return d


S = {
    'Deep Affliction 38/13/0': rep(('ImprovedCorruption', 5), ('ImprovedLifeTap', 2), ('Suppression', 3), ('Malediction', 5), ('ImprovedDrains', 3),
        ('ImprovedBoA', 2), ('FelConcentration', 3), ('Pandemic', 3), ('Nightfall', 2), ('SiphonLife', 1), ('SoulSiphon', 3), ('ShadowMastery', 5), ('Wrack', 1),
        ('DemonicEmbrace', 5), ('ImprovedVoidwalker', 3), ('FelVitality', 3), ('DemonicAegis', 2)),
    'Demonic Knowledge splash 28/23/0': rep(('ImprovedCorruption', 5), ('Suppression', 3), ('ImprovedLifeTap', 1), ('ImprovedDrains', 3), ('Malediction', 5),
        ('Pandemic', 3), ('ImprovedBoA', 2), ('Nightfall', 2), ('SiphonLife', 1), ('SoulSiphon', 3),
        ('DemonicEmbrace', 5), ('UnholyPower', 5), ('FelVitality', 3), ('ImprovedVoidwalker', 3), ('DemonicSacrifice', 1), ('MasterSummoner', 2), ('FelDomination', 1),
        ('DemonicKnowledge', 3)),
    'wowforeverbuilds drain tank (51)': rep(('ImprovedCorruption', 5), ('ImprovedLifeTap', 2), ('ImprovedDrains', 3), ('SoulHarvesting', 2), ('FelConcentration', 3),
        ('Suppression', 2), ('AmplifyCurse', 1), ('Nightfall', 2), ('SiphonLife', 1), ('DemonicEmbrace', 5), ('ImprovedVoidwalker', 3), ('SoulSiphon', 3), ('ImprovedBoA', 2),
        ('ShadowMastery', 5), ('Wrack', 1), ('Malediction', 5), ('CurseOfExhaustion', 1), ('Suppression', 3), ('FelVitality', 2)),
    'page solo spec (SOLO56)': build(SOLO56, 51),
    'proposed solo spec (SOLO56_V8)': build(SOLO56_V8, 51),
}

if __name__ == "__main__":
    for name, t in S.items():
        assert valid(t) and sum(t.values()) == 51, name
    names = list(S)
    ref = names.index('page solo spec (SOLO56)')
    cells = [(sp, pm) for sp in (1.0, 2.0, 3.0) for pm in (1.0, 0.5)]
    res = spk_many([(60, S[n], sp, dict(char_mult={'pet_dps': pm})) for sp, pm in cells for n in names])
    print('### Level 60 solo builds (seconds per kill; % = how much faster the page solo spec is)\n')
    print('| SP | pet | ' + ' | '.join(names) + ' |')
    print('|---|---|' + '---|' * len(names))
    for i, (sp, pm) in enumerate(cells):
        r = res[len(names) * i:len(names) * (i + 1)]
        dk = r[ref][0]
        print(f'| {sp} | x{pm} | ' + ' | '.join(f'{a:.2f} {b}' + ('' if j == ref else f' ({100 * (1 - dk / a):.1f}%)')
                                                for j, (a, b) in enumerate(r)) + ' |')
