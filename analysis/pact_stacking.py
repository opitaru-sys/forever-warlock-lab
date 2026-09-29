"""Demonic Pact builds: the 5/31/0 Succubus leveling build, and stacked sacrifices at 60 (v8).

Run from the repo root: python analysis/pact_stacking.py
Best rotation from evaluate() (modifiers included), averaged over mob HP x0.8 to x1.2, SP 1.0 x level.
aggro: the pet holds the mob like a Voidwalker (the Demonic Brand scenario).
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "models"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from character import valid
from leveling_paths import page_build, build, rep, spk_many, SOLO56

# The page's 5/31/0 preset (ORDER_531 in src/builder.js), Imp sacrificed through Demonic Pact
ORDER_531 = rep(('ImprovedCorruption', 5), ('DemonicEmbrace', 5), ('UnholyPower', 5), ('FelVitality', 3), ('ImprovedVoidwalker', 2),
                ('DemonicSacrifice', 1), ('MasterSummoner', 2), ('ImprovedSayaad', 2), ('FelDomination', 1), ('DemonicBrand', 1),
                ('SoulLink', 1), ('DemonicKnowledge', 3), ('MasterDemonologist', 4), ('DemonicPact', 1),
                ('Suppression', 3), ('ImprovedDrains', 3), ('Malediction', 5), ('Pandemic', 3), ('ImprovedBoA', 2))
PACT = dict(build(ORDER_531, 51), _sac='imp')


def succubus_531():
    levels = (45, 48, 50, 52, 55, 58, 60)
    cols = [('page plan, Voidwalker', 'plan', 'voidwalker', False), ('5/31/0, Succubus', '531', 'succubus', False),
            ('5/31/0, Succubus holds aggro', '531', 'succubus', True), ('5/31/0, Voidwalker', '531', 'voidwalker', False),
            ('5/31/0, Felhunter', '531', 'felhunter', False)]
    jobs = []
    for L in levels:
        for _, b, pet, aggro in cols:
            t = page_build(L) if b == 'plan' else dict(build(ORDER_531, L - 9), _sac='imp')
            jobs.append((L, t, 1.0, dict(pet=pet, aggro=aggro)))
    res = spk_many(jobs)
    print('### 5/31/0 with the Imp sacrificed (Demonic Pact), SP 1.0 (% vs the page plan)\n')
    print('| L | ' + ' | '.join(c[0] for c in cols) + ' |')
    print('|---|' + '---|' * len(cols))
    for i, L in enumerate(levels):
        r = res[len(cols) * i:len(cols) * (i + 1)]
        ref = r[0][0]
        print(f'| {L} | {ref:.2f} {r[0][1]} | ' + ' | '.join(f'{a:.2f} ({100 * (a / ref - 1):+.1f}%)' for a, _ in r[1:]) + ' |')


def stacking():
    """If a second sacrifice adds a buff instead of replacing the first: Imp, Felhunter and Voidwalker sacrificed,
    Succubus out. 'free': Soul Link's 30% redirect costs nothing. 'paid back': you heal the Succubus for it with
    your own health, the same as taking the hits yourself."""
    t = PACT
    rows = [('page solo spec (SOLO56), Voidwalker', build(SOLO56, 51), 'voidwalker', {}),
            ('Pact, Imp sacrifice only, Succubus', t, 'succubus', {}),
            ('Pact, sacrifices stack, Succubus, redirect free', t, 'succubus', {'felhunter_sac': True, 'voidwalker_sac': True}),
            ('Pact, sacrifices stack, Succubus, redirect paid back', t, 'succubus',
             {'felhunter_sac': True, 'voidwalker_sac': True, 'taken_frac': 1.0})]
    res = spk_many([(60, b, 1.0, dict(pet=pet, char_set=cs)) for _, b, pet, cs in rows])
    ref = res[0][0]
    print('\n### Stacked sacrifices at 60, SP 1.0 (% vs the page solo spec)\n')
    print('| build | seconds per kill | vs solo spec |')
    print('|---|---|---|')
    for (name, *_), (a, n) in zip(rows, res):
        print(f'| {name} | {a:.2f} {n} | {100 * (a / ref - 1):+.1f}% |')


if __name__ == "__main__":
    assert valid({k: v for k, v in PACT.items() if k != '_sac'})
    succubus_531()
    stacking()
