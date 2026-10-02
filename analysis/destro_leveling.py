"""Destruction and curse leveling builds against the page plan (v8).

Run from the repo root: python analysis/destro_leveling.py [section ...]   (about 30 minutes on 16 cores for all
sections; the respec search is most of it). Sections: builds sbscan sbgap coe sensitivity isb60 pets harvest rest respec.
Prints markdown tables: reader builds vs the page plan, a respec talent search at 20/30/40/50/60, Curse of the
Elements on and off, Shadow Bolt wins, and the sensitivity to level scaling, Suppression, Soul Harvest and pets.
Seconds per kill (lower is better) = fight + 8 s walking + rest, Voidwalker unless noted.
"""
import os
import sys
from multiprocessing import Pool

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "models"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import character as c
import leveling_sim as ls
from character import valid, evaluate, AFF, DEMO, DESTRO, PREREQ
from leveling_paths import AFF_FIRST


def rep(*p):
    out = []
    for k, n in p:
        out += [k] * n
    return out


# babilonibetyar: Improved Corruption 5, Bane 5, Aftermath 5 (his order), then our Destruction core order with Immolate
# as the centerpiece: Shadowburn and Ruin to open row 3, Conflagrate as early as it unlocks (30), Agonizing Flames,
# Cataclysm, Fire and Brimstone, Shadow and Flame, Bane of Havoc and Incinerate (47), then Suppression, Improved Life
# Tap, Malediction and a point of Molten Skin.
BABILON = rep(('ImprovedCorruption', 5), ('Bane', 5), ('Aftermath', 5), ('Shadowburn', 1), ('Ruin', 4), ('Conflagrate', 1),
              ('Ruin', 1), ('AgonizingFlames', 3), ('Cataclysm', 3), ('FireAndBrimstone', 3), ('ShadowAndFlame', 5),
              ('BaneOfHavoc', 1), ('Incinerate', 1), ('Suppression', 5), ('ImprovedLifeTap', 2), ('Malediction', 5),
              ('MoltenSkin', 1))
# The community 17/0/34 "Shadow Bolt nuke" leveling build (wowforeverbuilds, docs/warlock-community.md 1d). Its stated
# order puts Shadow and Flame at 40-44, which row gating forbids (23 points in rows 1-5, 25 needed), so Agonizing
# Flames moves to 40-42, Shadow and Flame to 43-47 and Intensity to 48-50. Same final 17/0/34.
COMMUNITY_34 = rep(('ImprovedCorruption', 5), ('ImprovedShadowBolt', 5), ('Bane', 5), ('ImprovedLifeTap', 2), ('MoltenSkin', 3),
                   ('Ruin', 5), ('Shadowburn', 1), ('Cataclysm', 3), ('Conflagrate', 1), ('AgonizingFlames', 3),
                   ('ShadowAndFlame', 5), ('Intensity', 3), ('Suppression', 5), ('Malediction', 3), ('Nightfall', 2))
# Speedrun-style: Destruction to Shadowburn (Bane 5, Cataclysm 3 and Aftermath 2 open row 3, Shadowburn at 20), then
# Improved Corruption 5 and Soul Harvesting 2 for Drain Soul finishes (27), then the page plan's Affliction order.
SPEEDRUN = rep(('Bane', 5), ('Cataclysm', 3), ('Aftermath', 2), ('Shadowburn', 1), ('ImprovedCorruption', 5), ('SoulHarvesting', 2),
               ('Suppression', 3), ('ImprovedDrains', 3), ('Malediction', 5), ('ImprovedBoA', 2), ('Pandemic', 2), ('SiphonLife', 1),
               ('SoulSiphon', 3), ('Nightfall', 2), ('ShadowMastery', 5), ('Wrack', 1), ('Pandemic', 1), ('FelConcentration', 3),
               ('ImprovedLifeTap', 2))
BUILDS = [('plan', AFF_FIRST), ('babilon', BABILON), ('community 17/0/34', COMMUNITY_34), ('speedrun-style', SPEEDRUN)]
# The page's own order from level 56 (the Demonic Knowledge splash, SOLO56 in src/page.src.html); AFF_FIRST before 56
SOLO56 = rep(('ImprovedCorruption', 5), ('Suppression', 3), ('ImprovedDrains', 3), ('Malediction', 5), ('ImprovedBoA', 2),
             ('Pandemic', 2), ('SiphonLife', 1), ('SoulSiphon', 3), ('DemonicEmbrace', 5), ('UnholyPower', 5), ('DemonicAegis', 2),
             ('ImprovedVoidwalker', 3), ('FelVitality', 3), ('DemonicEnergies', 2), ('DemonicKnowledge', 3), ('Nightfall', 2),
             ('Pandemic', 1), ('ImprovedLifeTap', 1))
HP9 = tuple(round(0.8 + 0.05 * i, 2) for i in range(9))   # every result is averaged over mob HP x0.8 to x1.2
HP5 = (0.8, 0.9, 1.0, 1.1, 1.2)                             # inside the talent search, for speed
# no effect on seconds per kill with a Voidwalker in the model: never a search target, only an unlock filler
NO_VALUE = {'DestructiveReach', 'Intensity', 'Pyroclasm', 'BaneOfHavoc', 'FelConcentration', 'CurseOfExhaustion',
            'ImprovedHealthFunnel', 'ImprovedImp', 'DemonicAegis', 'ImprovedVoidwalker', 'DemonicEnergies', 'ImprovedSayaad',
            'MasterSummoner', 'FelDomination', 'DemonicBrand', 'ImprovedFelhunter', 'DemonicSacrifice', 'MasterDemonologist',
            'DemonicPact'}
SEARCH = dict(top=1, hp_mults=HP5)
ALL = {k: (i, r, m) for i, tree in enumerate((AFF, DEMO, DESTRO)) for k, (r, m) in tree.items()}

for _name, _order in BUILDS:
    assert len(_order) == 51, _name
    _t = {}
    for _k in _order:
        _t[_k] = _t.get(_k, 0) + 1
        assert valid(_t), (_name, _k, sum(_t.values()))


def take(order, n):
    t = {}
    for k in order[:n]:
        t[k] = t.get(k, 0) + 1
    return t


def is_sb(name):
    return '+SB' in name or 'ShadowBolt' in name


def short(tal):
    trees = [sum(v for k, v in tal.items() if ALL[k][0] == i) for i in range(3)]
    body = ', '.join(f'{k} {v}' for k, v in sorted(tal.items(), key=lambda kv: (ALL[kv[0]][0], ALL[kv[0]][1])))
    return '%d/%d/%d: %s' % (trees[0], trees[1], trees[2], body)


# ---------------------------------------------------------------- pool workers
ORIG_MOD_OPTIONS = c.mod_options


def no_coe_groups(L, tal):
    return [g for g in ORIG_MOD_OPTIONS(L, tal) if g[0][0] != 'coe']


def run_eval(args):
    """(level, talents, sp, pet, evaluate options[, 'nocoe' | 'sbonly']) -> (policy, spk, ttk, rest)."""
    L, tal, sp, pet, opts = args[:5]
    mode = args[5] if len(args) > 5 else ''
    opts = dict(dict(hp_mults=HP9), **opts)
    c.mod_options = no_coe_groups if mode == 'nocoe' else ORIG_MOD_OPTIONS
    ls.ISB_DUR = 60.0 if mode == 'isb60' else 12.0
    if mode == 'sbonly':
        opts = dict(opts, policies={k: v for k, v in c.POLICIES.items() if is_sb(k)})
    n, s = evaluate(L, tal, pet, sp, **opts)
    return n, s['spk'], s['ttk'], s['rest']


def pmap(pool, jobs):
    return pool.map(run_eval, jobs, chunksize=4)


# ---------------------------------------------------------------- respec search
def addable(t, k):
    return t.get(k, 0) < ALL[k][2] and valid(dict(t, **{k: t.get(k, 0) + 1}))


def unlock(t, k, pref, left):
    """Points that make talent k takeable: its prerequisite, then the best-valued takeable points in lower rows of
    its tree (zero-value fillers allowed), then k. None if it cannot be reached with `left` points."""
    t, steps = dict(t), []
    while len(steps) < left:
        if addable(t, k):
            return steps + [k]
        req = PREREQ.get(k)
        if req and t.get(req[0], 0) < req[1] and addable(t, req[0]):
            nxt = req[0]
        else:
            tree, row = ALL[k][0], ALL[k][1]
            opts = [j for j in ALL if ALL[j][0] == tree and ALL[j][1] < row and addable(t, j)]
            if not opts:
                return None
            nxt = max(opts, key=lambda j: (pref.get(j, 0.0), -ALL[j][1]))
        t[nxt] = t.get(nxt, 0) + 1
        steps.append(nxt)
    return None


def moves(t, left, pref):
    singles = [(k,) for k in ALL if addable(t, k)]
    packs = []
    for k in ALL:
        if k not in NO_VALUE and t.get(k, 0) < ALL[k][2] and not addable(t, k):
            p = unlock(t, k, pref, left)
            if p and tuple(p) not in packs:
                packs.append(tuple(p))
    return singles, packs


def plus(t, steps):
    t = dict(t)
    for k in steps:
        t[k] = t.get(k, 0) + 1
    return t


def greedy(pool, L, sp):
    """Greedy fill with tier-gating lookahead: each step takes the single point or unlock package with the best
    seconds-per-kill gain per point spent."""
    n, t = L - 9, {}
    cur = pmap(pool, [(L, t, sp, 'voidwalker', SEARCH)])[0][1]
    while sum(t.values()) < n:
        left = n - sum(t.values())
        singles = [(k,) for k in ALL if addable(t, k)]
        res = pmap(pool, [(L, plus(t, m), sp, 'voidwalker', SEARCH) for m in singles])
        pref = {m[0]: cur - r[1] for m, r in zip(singles, res)}
        _, packs = moves(t, left, pref)
        res2 = pmap(pool, [(L, plus(t, m), sp, 'voidwalker', SEARCH) for m in packs])
        scored = [((cur - r[1]) / len(m), m, r[1]) for m, r in zip(singles + packs, res + res2)]
        rate, m, spk = max(scored, key=lambda x: x[0])
        t, cur = plus(t, m), spk
    return t


def polish(pool, L, sp, t, rounds=8):
    """Move one point at a time (remove one, add one) while that lowers seconds per kill."""
    cur = pmap(pool, [(L, t, sp, 'voidwalker', SEARCH)])[0][1]
    for _ in range(rounds):
        cands = []
        for a in list(t):
            less = dict(t, **{a: t[a] - 1})
            if not less[a]:
                del less[a]
            if not valid(less):
                continue
            cands += [plus(less, [b]) for b in ALL if b != a and b not in NO_VALUE and addable(less, b)]
        res = pmap(pool, [(L, x, sp, 'voidwalker', SEARCH) for x in cands])
        i = min(range(len(res)), key=lambda j: res[j][1])
        if res[i][1] >= cur - 1e-9:
            break
        t, cur = cands[i], res[i][1]
    return t


def respec(pool, L, sp):
    """Best build found at level L among the greedy fill and the best fixed build (reader builds and both page
    orders), each as found and polished. The search scores with 5 mob HPs and one modifier pass for speed, so the
    final pick re-scores every candidate the full way (9 HPs, top 3)."""
    fixed = [take(o, L - 9) for o in [o for _, o in BUILDS] + [SOLO56]]
    res = pmap(pool, [(L, t, sp, 'voidwalker', {}) for t in fixed])
    seed = fixed[min(range(len(res)), key=lambda j: res[j][1])]
    g = greedy(pool, L, sp)
    found = [g, polish(pool, L, sp, g), seed, polish(pool, L, sp, seed)]
    res = pmap(pool, [(L, t, sp, 'voidwalker', {}) for t in found])
    j = min(range(len(res)), key=lambda i: res[i][1])
    return found[j], res[j]


# ---------------------------------------------------------------- reports
def table_builds(pool, levels, sp, opts=None, pet='voidwalker'):
    opts = opts or {}
    jobs = [(L, take(o, L - 9), sp, pet, opts) for L in levels for _, o in BUILDS]
    res = pmap(pool, jobs)
    rows = {}
    for i, L in enumerate(levels):
        rows[L] = res[i * len(BUILDS):(i + 1) * len(BUILDS)]
    return rows


def print_builds(rows, title):
    print(f'\n### {title}\n')
    print('| L | ' + ' | '.join(n for n, _ in BUILDS) + ' |')
    print('|---' * (len(BUILDS) + 1) + '|')
    for L, r in rows.items():
        ref = r[0][1]
        cells = [fmt(r[0][0], r[0][1])] + [fmt(x[0], x[1], ref) for x in r[1:]]
        print(f'| {L} | ' + ' | '.join(cells) + ' |')


def fmt(n, spk, ref=None):
    d = '' if ref is None else f' ({100 * (spk / ref - 1):+.1f}%)'
    return f'{spk:.2f}{d} {n}'


def verdicts(rows):
    """Per level: the fastest build, and whether a Shadow Bolt filler won anywhere."""
    win = {L: min(range(len(r)), key=lambda i: r[i][1]) for L, r in rows.items()}
    sb = [(L, BUILDS[i][0], x[0]) for L, r in rows.items() for i, x in enumerate(r) if is_sb(x[0])]
    return win, sb


def main(sections):
    levels = list(range(10, 61, 2))
    with Pool(max(1, (os.cpu_count() or 2) - 2)) as pool:
        base = {}
        if {'builds', 'sensitivity'} & sections:
            base = {sp: table_builds(pool, levels, sp) for sp in (1.0, 2.0)}
        if 'builds' in sections:
            for sp in (1.0, 2.0):
                print_builds(base[sp], f'Reader builds vs the page plan, SP {sp} x level (% vs plan)')
        steps = [('sbscan', report_sb_scans), ('sbgap', report_margin_sb), ('coe', lambda p: report_coe(p, levels)),
                 ('sensitivity', lambda p: report_sensitivity(p, levels, base)), ('isb60', report_isb60),
                 ('pets', report_pets), ('harvest', report_harvest), ('rest', report_rest), ('respec', report_respec)]
        for name, fn in steps:
            if name in sections:
                fn(pool)
                sys.stdout.flush()


def report_sb_scans(pool):
    """The published claim: Shadow Bolt never wins. Every level 10 to 60, three SP levels, four builds, three data modes."""
    meta = [(L, sp, name, m) for L in range(10, 61) for sp in (0.5, 1.0, 2.0) for name, _ in BUILDS
            for m in ('base', 'scaled', 'wowhead')]
    orders = dict(BUILDS)
    res = pmap(pool, [(L, take(orders[name], L - 9), sp, 'voidwalker', dict(dd_mode=m)) for L, sp, name, m in meta])
    wins = [x + (r[0],) for x, r in zip(meta, res) if is_sb(r[0])]
    print(f'\n### Shadow Bolt as the best filler: {len(wins)} of {len(meta)} scans '
          '(level 10 to 60 x SP 0.5/1/2 x 4 builds x 3 direct damage modes)\n')
    for name, _ in BUILDS:
        mine = [w for w in wins if w[2] == name]
        print(f'- {name}: {len(mine)} of {len(meta) // len(BUILDS)}' + (': ' + '; '.join(
            f'L{w[0]} SP {w[1]} {w[3]} {w[4]}' for w in mine) if mine else ''))


def report_isb60(pool):
    """Improved Shadow Bolt at 60 sec (the community guide's number) instead of the client's 12."""
    print('\n### Improved Shadow Bolt lasting 60 sec instead of 12, community 17/0/34, SP 1.0\n')
    print('| L | plan | 17/0/34, ISB 12 sec | 17/0/34, ISB 60 sec |')
    print('|---|---|---|---|')
    lv = (20, 30, 40, 50, 60)
    res = pmap(pool, [(L, take(o, L - 9), 1.0, 'voidwalker', {}, m) for L in lv
                      for o, m in ((AFF_FIRST, ''), (COMMUNITY_34, ''), (COMMUNITY_34, 'isb60'))])
    for i, L in enumerate(lv):
        a, b, d = res[3 * i:3 * i + 3]
        print(f'| {L} | {a[1]:.2f} {a[0]} | {b[1]:.2f} ({100 * (b[1] / a[1] - 1):+.1f}%) {b[0]} | '
              f'{d[1]:.2f} ({100 * (d[1] / a[1] - 1):+.1f}%) {d[0]} |')


def report_margin_sb(pool):
    """How far the best Shadow Bolt rotation trails the best rotation, per build."""
    levels = (20, 30, 40, 50, 60)
    jobs, meta = [], []
    for L in levels:
        for name, o in BUILDS:
            for mode in ('', 'sbonly'):
                jobs.append((L, take(o, L - 9), 1.0, 'voidwalker', {}, mode))
                meta.append((L, name, mode))
    res = pmap(pool, jobs)
    print('\n### Best Shadow Bolt rotation vs the best rotation, same build, SP 1.0\n')
    print('| L | build | best | best with Shadow Bolt filler | gap |')
    print('|---|---|---|---|---|')
    for i in range(0, len(res), 2):
        L, name, _ = meta[i]
        a, b = res[i], res[i + 1]
        print(f'| {L} | {name} | {a[1]:.2f} {a[0]} | {b[1]:.2f} {b[0]} | {100 * (b[1] / a[1] - 1):+.1f}% |')


def report_coe(pool, levels):
    lv = [L for L in levels if L >= 20]
    for sp in (1.0, 2.0):
        jobs = [(L, take(AFF_FIRST, L - 9), sp, 'voidwalker', {}, m) for L in lv for m in ('', 'nocoe')]
        res = pmap(pool, jobs)
        print(f'\n### Curse of the Elements for the page plan, SP {sp}\n')
        print('| L | with the curse allowed | curse never cast | gain |')
        print('|---|---|---|---|')
        for i, L in enumerate(lv):
            a, b = res[2 * i], res[2 * i + 1]
            print(f'| {L} | {a[1]:.2f} {a[0]} | {b[1]:.2f} {b[0]} | {100 * (1 - a[1] / b[1]):.1f}% |')


def report_sensitivity(pool, levels, base):
    for opts, label in ((dict(dd_mode='wowhead'), "Wowhead's direct damage (level scaling at MaxLevel)"),
                        (dict(dd_mode='scaled'), 'in-game level scaling of direct damage and Life Tap'),
                        (dict(supp_all=False), 'Suppression on Affliction spells only (the Classic reading)')):
        rows = table_builds(pool, levels, 1.0, opts)
        print_builds(rows, f'Sensitivity, {label}, SP 1.0')
        w0, _ = verdicts(base[1.0])
        w1, sb = verdicts(rows)
        flips = [(L, BUILDS[w0[L]][0], BUILDS[w1[L]][0]) for L in levels if w0[L] != w1[L]]
        print(f'\nFastest build changes at {len(flips)} of {len(levels)} levels: {flips}; Shadow Bolt filler wins: {sb}')


def report_pets(pool):
    pets = ('voidwalker', 'imp', 'succubus', 'felhunter', 'none')
    print('\n### Pet choice, SP 1.0 (seconds per kill)\n')
    print('| L | build | ' + ' | '.join(pets) + ' |')
    print('|---|---|' + '---|' * len(pets))
    for L in (20, 30, 40, 50, 60):
        jobs = [(L, take(o, L - 9), 1.0, p, {}) for _, o in BUILDS for p in pets]
        res = pmap(pool, jobs)
        for i, (name, _) in enumerate(BUILDS):
            r = res[i * len(pets):(i + 1) * len(pets)]
            print(f'| {L} | {name} | ' + ' | '.join(f'{x[1]:.2f}' for x in r) + ' |')


def report_harvest(pool):
    print('\n### Soul Harvest: does harvest_drink matter? speedrun-style build, SP 1.0\n')
    print('| L | best (drink not boosted) | best if Soul Harvest also boosts drinking | Drain Soul finish forced, not boosted | forced, boosted |')
    print('|---|---|---|---|---|')
    forced = {'DS': dict(policies={k + '|ds': dict(v, fin='DrainSoul') for k, v in c.POLICIES.items()}, mods=False)}
    for L in (28, 30, 40, 50, 60):
        t = take(SPEEDRUN, L - 9)
        jobs = [(L, t, 1.0, 'voidwalker', dict(harvest_drink=h)) for h in (False, True)]
        jobs += [(L, t, 1.0, 'voidwalker', dict(forced['DS'], harvest_drink=h)) for h in (False, True)]
        r = pmap(pool, jobs)
        print(f'| {L} | ' + ' | '.join(f'{x[1]:.2f} {x[0]}' for x in r) + ' |')


def report_rest(pool):
    """Destruction builds fight faster and rest longer, so the verdict leans on the model's rest rate."""
    print('\n### Rest rate x0.5 and x2 (food and water), SP 1.0 (% vs plan)\n')
    print('| L | rest rate | ' + ' | '.join(n for n, _ in BUILDS) + ' |')
    print('|---|---|' + '---|' * len(BUILDS))
    for L in (30, 40, 50, 60):
        for mult in (0.5, 1.0, 2.0):
            ts = [take(o, L - 9) for _, o in BUILDS]
            rr = [mult * (2.2 * L + 1.2 * L * (1 + .1 * t.get('ImprovedLifeTap', 0))) for t in ts]
            res = pmap(pool, [(L, t, 1.0, 'voidwalker', dict(rest_rate=r)) for t, r in zip(ts, rr)])
            ref = res[0][1]
            print(f'| {L} | x{mult} | {ref:.2f} | ' + ' | '.join(f'{x[1]:.2f} ({100 * (x[1] / ref - 1):+.1f}%)' for x in res[1:]) + ' |')


def report_respec(pool):
    for sp in (1.0, 2.0):
        print(f'\n### Respec search, SP {sp} x level (greedy fill with unlock lookahead, then one-point moves)\n')
        print('| L | page plan (SOLO56 order at 56+) | best build found | faster by | its build |')
        print('|---|---|---|---|---|')
        for L in (20, 30, 40, 50, 60):
            t, r = respec(pool, L, sp)
            p = pmap(pool, [(L, take(SOLO56 if L >= 56 else AFF_FIRST, L - 9), sp, 'voidwalker', {})])[0]
            print(f'| {L} | {p[1]:.2f} {p[0]} | {r[1]:.2f} {r[0]} | {100 * (1 - r[1] / p[1]):.1f}% | {short(t)} |')


SECTIONS = {'builds', 'sbscan', 'sbgap', 'coe', 'sensitivity', 'isb60', 'pets', 'harvest', 'rest', 'respec'}

if __name__ == '__main__':
    main(set(sys.argv[1:]) or SECTIONS)
