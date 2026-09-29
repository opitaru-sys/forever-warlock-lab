"""Leveling talent paths, the Demonic Knowledge crossover, and how much talents matter early (v8).

Run from the repo root: python analysis/leveling_paths.py
Every number is the best rotation from evaluate() (curse, finisher and Death Coil modifiers included), averaged over
mob HP x0.8 to x1.2 (HP_GRID), Voidwalker. Seconds per kill: fight + 8 s walk + rest, lower is better.
"""
import os
import sys
from multiprocessing import Pool

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "models"))

import character as model
from character import evaluate, valid, HP_GRID


def rep(*p):
    out = []
    for k, n in p:
        out += [k] * n
    return out


# The page planner: TAL_ORDER to 55 (the first 46 points here), then a respec to SOLO56 (src/page.src.html)
AFF_FIRST = rep(('ImprovedCorruption', 5), ('Suppression', 3), ('ImprovedDrains', 3), ('Malediction', 5), ('ImprovedBoA', 2), ('Pandemic', 2),
                ('SiphonLife', 1), ('SoulSiphon', 3), ('Nightfall', 2), ('ShadowMastery', 5), ('Wrack', 1), ('Pandemic', 1), ('FelConcentration', 3),
                ('ImprovedLifeTap', 2), ('DemonicEmbrace', 5), ('ImprovedVoidwalker', 3), ('FelVitality', 3), ('DemonicAegis', 2))
SOLO56 = rep(('ImprovedCorruption', 5), ('Suppression', 3), ('ImprovedDrains', 3), ('Malediction', 5), ('ImprovedBoA', 2), ('Pandemic', 2),
             ('SiphonLife', 1), ('SoulSiphon', 3), ('DemonicEmbrace', 5), ('UnholyPower', 5), ('DemonicAegis', 2), ('ImprovedVoidwalker', 3),
             ('FelVitality', 3), ('DemonicEnergies', 2), ('DemonicKnowledge', 3), ('Nightfall', 2), ('Pandemic', 1), ('ImprovedLifeTap', 1))
# v8 proposals (analysis/planner_order.py): one order for 10 to 55 (46 points; the last 5 here only extend it to 60
# for the Demonic Knowledge comparison) and the 56+ solo build, 28/23/0
PLANNER_V8 = rep(('ImprovedCorruption', 5), ('Suppression', 3), ('Malediction', 2), ('ImprovedBoA', 2), ('Malediction', 3), ('ImprovedLifeTap', 1),
                 ('Pandemic', 1), ('ImprovedDrains', 3), ('SoulSiphon', 3), ('ImprovedLifeTap', 1), ('SiphonLife', 1), ('ShadowMastery', 1),
                 ('AmplifyCurse', 1), ('ShadowMastery', 4), ('Pandemic', 2), ('Malevolence', 3), ('Bane', 1), ('Malevolence', 1), ('DemonicEmbrace', 2),
                 ('Malevolence', 1), ('UnholyPower', 5),
                 ('Bane', 1), ('Suppression', 2), ('SoulHarvesting', 2))
SOLO56_V8 = rep(('ImprovedCorruption', 5), ('Suppression', 3), ('Malediction', 5), ('ImprovedBoA', 2), ('Pandemic', 1), ('ImprovedDrains', 3),
                ('AmplifyCurse', 1), ('SoulSiphon', 3), ('SiphonLife', 1), ('DemonicEmbrace', 5), ('UnholyPower', 5), ('ImprovedVoidwalker', 3),
                ('DemonicAegis', 2), ('FelVitality', 3), ('DemonicEnergies', 2), ('DemonicKnowledge', 3), ('ImprovedLifeTap', 1), ('ShadowMastery', 3))
# Which orders page_build() follows: 'v8' (the proposals above) or 'v7' (AFF_FIRST to 55, then SOLO56)
PAGE_ORDERS = 'v8'
# Affliction core to Soul Siphon first (21 pts, level 30), then Demonology to Demonic Knowledge (23 pts, level 53), then back to Affliction
DK_PATH = rep(('ImprovedCorruption', 5), ('Suppression', 3), ('ImprovedDrains', 3), ('Malediction', 5), ('ImprovedBoA', 2), ('Pandemic', 2),
              ('SiphonLife', 1), ('SoulSiphon', 3),
              ('DemonicEmbrace', 5), ('UnholyPower', 5), ('FelVitality', 3), ('ImprovedVoidwalker', 3), ('DemonicSacrifice', 1), ('MasterSummoner', 2),
              ('FelDomination', 1), ('DemonicKnowledge', 3), ('Nightfall', 2), ('Pandemic', 1), ('ImprovedLifeTap', 1))
# Demonology first to Demonic Knowledge (levels 10-32), then Affliction
DK_FIRST = rep(('ImprovedCorruption', 5), ('DemonicEmbrace', 5), ('UnholyPower', 5), ('FelVitality', 3), ('ImprovedVoidwalker', 3), ('DemonicSacrifice', 1),
               ('MasterSummoner', 2), ('FelDomination', 1), ('DemonicKnowledge', 3),
               ('Suppression', 3), ('ImprovedDrains', 3), ('Malediction', 5), ('ImprovedBoA', 2), ('Pandemic', 3), ('SiphonLife', 1), ('SoulSiphon', 3),
               ('Nightfall', 2), ('ImprovedLifeTap', 1))
# The wowforeverbuilds drain tank (ORDER_WFB in src/builder.js)
WFB = rep(('ImprovedCorruption', 5), ('ImprovedLifeTap', 2), ('ImprovedDrains', 3), ('SoulHarvesting', 2), ('FelConcentration', 3), ('Suppression', 2),
          ('AmplifyCurse', 1), ('Nightfall', 2), ('SiphonLife', 1), ('DemonicEmbrace', 5), ('ImprovedVoidwalker', 3), ('SoulSiphon', 3),
          ('ImprovedBoA', 2), ('ShadowMastery', 5), ('Wrack', 1), ('Malediction', 5), ('CurseOfExhaustion', 1), ('Suppression', 3), ('FelVitality', 2))


def build(order, n):
    t = {}
    for k in order:
        if sum(t.values()) >= n:
            break
        t[k] = t.get(k, 0) + 1
        assert valid(t), (k, t)
    return t


def page_orders(which=None):
    """(order to 55, solo build from 56) for PAGE_ORDERS or the given 'v7' / 'v8'."""
    return (PLANNER_V8, SOLO56_V8) if (which or PAGE_ORDERS) == 'v8' else (AFF_FIRST, SOLO56)


def page_build(L, which=None):
    """The build the page planner shows at level L."""
    plan, solo = page_orders(which)
    return build(solo if L >= 56 else plan, L - 9)


def spk(L, t, sp=1.0, char_mult=None, char_set=None, full=False, **kw):
    """(seconds per kill, rotation) for a build, HP-averaged, modifiers included. char_mult / char_set scale or set
    Char fields after make_char (e.g. {'pet_dps': 0.5}); full=True returns the whole evaluate() result instead."""
    base = model.make_char

    def make(*a, **k):
        ch = base(*a, **k)
        for f, v in (char_mult or {}).items():
            setattr(ch, f, getattr(ch, f) * v)
        for f, v in (char_set or {}).items():
            setattr(ch, f, v)
        return ch
    model.make_char = make
    try:
        kw.setdefault('hp_mults', HP_GRID)
        n, s = evaluate(L, t, sp_per_level=sp, **kw)
    finally:
        model.make_char = base
    return (n, s) if full else (s['spk'], n)


def _job(args):
    L, t, sp, kw = args
    return spk(L, t, sp, **kw)


def spk_many(jobs, procs=None):
    """spk() for a list of (level, talents, sp, evaluate keywords), in a process pool."""
    with Pool(procs or max(1, (os.cpu_count() or 2) - 2)) as pool:
        return pool.map(_job, jobs, chunksize=2)


def paths_table():
    levels = (20, 25, 30, 35, 40, 45, 50, 55, 60)
    orders = (AFF_FIRST, PLANNER_V8, DK_PATH, DK_FIRST)
    res = spk_many([(L, build(o, L - 9), 1.0, {}) for L in levels for o in orders])
    print('### Talent paths without respecs, SP 1.0 x level\n')
    print('| L | page order v7 (AFF_FIRST) | page order v8 (PLANNER_V8) | Affliction to 21, then DK | DK first |')
    print('|---|---|---|---|---|')
    for i, L in enumerate(levels):
        r = res[len(orders) * i:len(orders) * (i + 1)]
        print(f'| {L} | ' + ' | '.join(f'{a:.2f} {b}' for a, b in r) + ' |')


def dk_crossover():
    """Demonic Knowledge 'pays off from about 56': staying on the leveling order vs the respec to the solo build,
    for the v7 and the v8 page orders, plus the v7 leveling path through Demonic Knowledge."""
    levels = list(range(46, 61))
    orders = (AFF_FIRST, SOLO56, DK_PATH, PLANNER_V8, SOLO56_V8)
    for sp in (1.0, 2.0, 3.0):
        res = spk_many([(L, build(o, L - 9), sp, {}) for L in levels for o in orders])
        print(f'\n### Demonic Knowledge crossover, SP {sp} x level\n')
        print('| L | v7 order, no respec | v7 respec to SOLO56 | v7 path through DK | v8 order, no respec | v8 respec to SOLO56_V8 |')
        print('|---|---|---|---|---|---|')
        for i, L in enumerate(levels):
            a, b, d, e, f = [x[0] for x in res[len(orders) * i:len(orders) * (i + 1)]]
            print(f'| {L} | {a:.2f} | {b:.2f} ({100 * (b / a - 1):+.1f}%) | {d:.2f} ({100 * (d / a - 1):+.1f}%) | '
                  f'{e:.2f} | {f:.2f} ({100 * (f / e - 1):+.1f}%) |')


def early_spread():
    """'Talents barely matter from 10 to 33': the gap between sensible builds and the best of them."""
    from destro_leveling import BABILON, COMMUNITY_34, SPEEDRUN
    builds = [('page v7', AFF_FIRST), ('page v8', PLANNER_V8), ('DK first', DK_FIRST), ('wowforeverbuilds', WFB),
              ('babilon', BABILON), ('17/0/34', COMMUNITY_34), ('speedrun-style', SPEEDRUN)]
    levels = list(range(10, 34))
    res = spk_many([(L, build(o, L - 9), 1.0, {}) for L in levels for _, o in builds])
    print('\n### Levels 10 to 33: every build vs the best of them, SP 1.0\n')
    print('| L | best | ' + ' | '.join(n for n, _ in builds) + ' |')
    print('|---|---|' + '---|' * len(builds))
    worst = {}
    for i, L in enumerate(levels):
        r = [x[0] for x in res[len(builds) * i:len(builds) * (i + 1)]]
        b = min(r)
        for (n, _), x in zip(builds, r):
            worst[n] = max(worst.get(n, 0.0), x / b - 1)
        print(f'| {L} | {b:.2f} | ' + ' | '.join(f'{100 * (x / b - 1):+.1f}%' for x in r) + ' |')
    print('\nLargest gap to the best, per build: ' + ', '.join(f'{n} {100 * w:.1f}%' for n, w in worst.items()))


def pet_table():
    """Pets for the page planner's build: seconds per kill / fight / rest."""
    levels, pets = (20, 30, 40, 50, 60), ('voidwalker', 'succubus', 'felhunter', 'imp')
    res = spk_many([(L, page_build(L), 1.0, dict(pet=p, full=True)) for L in levels for p in pets])
    print(f'\n### Pets, page planner build ({PAGE_ORDERS} orders), SP 1.0: seconds per kill / fight / rest\n')
    print('| L | ' + ' | '.join(pets) + ' |')
    print('|---|' + '---|' * len(pets))
    for i, L in enumerate(levels):
        r = [s for _, s in res[len(pets) * i:len(pets) * (i + 1)]]
        print(f'| {L} | ' + ' | '.join(f"{s['spk']:.2f} / {s['ttk']:.1f} / {s['rest']:.1f}" for s in r) + ' |')


def phases():
    """The page planner's best rotation at every level (for the phase texts)."""
    levels = list(range(10, 61))
    for which in ('v7', 'v8'):
        res = spk_many([(L, page_build(L, which), 1.0, {}) for L in levels])
        print(f'\n### Best rotation per level, page planner build ({which} orders), SP 1.0\n')
        print('| L | seconds per kill | rotation |')
        print('|---|---|---|')
        for L, (a, n) in zip(levels, res):
            print(f'| {L} | {a:.2f} | {n} |')


if __name__ == "__main__":
    paths_table()
    dk_crossover()
    early_spread()
    pet_table()
    phases()
