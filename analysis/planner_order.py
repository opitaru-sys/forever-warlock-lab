"""One leveling order for the page planner, levels 10 to 55 with no respecs, and the 56+ solo build (v8).

Run from the repo root: python analysis/planner_order.py   (about 20 minutes on 16 cores)
Objective: mean seconds per kill over levels 10 to 55 (Voidwalker, SP 1.0), each level using the first
(level - 9) points of the order. Improved Corruption 5 comes first by rule: instant Corruption lets you cast
while moving, which the model does not value.
Method: a greedy fill (each step the single point or unlock package with the best gain per point), then moves
of one point or one run of points to another place in the order while the mean improves, seeded from both the
greedy fill and the page's TAL_ORDER; then swaps of single points (from level 40 on) for other talents, each
followed by more moves. The search scores with
5 mob HPs and one modifier pass; the reported numbers use 9 HPs and the full modifier search.
Reads the page's TAL_ORDER and SOLO56 from src/page.src.html and the display names from src/builder.js.
"""
import os
import re
import sys
from multiprocessing import Pool

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, '..')
sys.path.insert(0, os.path.join(ROOT, 'models'))
sys.path.insert(0, HERE)

from character import valid, evaluate, HP_GRID
from destro_leveling import ALL, NO_VALUE, addable, unlock

HP5 = (0.8, 0.9, 1.0, 1.1, 1.2)
LEVELS = range(10, 56)
LOCK = 5          # Improved Corruption 5 first, fixed


def names():
    """Display name -> key, from src/builder.js."""
    src = open(os.path.join(ROOT, 'src', 'builder.js'), encoding='utf-8').read()
    return {n: k for k, n in re.findall(r"\{ k: '(\w+)', n: '([^']+)'", src)}


def page_order(const):
    src = open(os.path.join(ROOT, 'src', 'page.src.html'), encoding='utf-8').read()
    body = re.search(r'const %s = seq\(\[(.*?)\]\);' % const, src, re.S).group(1)
    key = names()
    out = []
    for n, c in re.findall(r"\['([^']+)', (\d+)\]", body):
        out += [key[n]] * int(c)
    return out


def page_format(order):
    key = names()
    disp = {k: n for n, k in key.items()}
    runs = []
    for k in order:
        if runs and runs[-1][0] == k:
            runs[-1][1] += 1
        else:
            runs.append([k, 1])
    return 'seq([' + ', '.join("['%s', %d]" % (disp[k], n) for k, n in runs) + '])'


def counts(order):
    t = {}
    for k in order:
        t[k] = t.get(k, 0) + 1
    return t


def legal(order):
    t = {}
    for k in order:
        t[k] = t.get(k, 0) + 1
        if not valid(t):
            return False
    return True


# ---------------------------------------------------------------- cached, pooled scoring
def score_job(args):
    L, items, sp, hp, top = args
    return evaluate(L, dict(items), 'voidwalker', sp, top=top, hp_mults=hp)[1]['spk']


class Scorer:
    def __init__(self, pool, sp, hp=HP5, top=1):
        self.pool, self.sp, self.hp, self.top, self.cache = pool, sp, hp, top, {}

    def key(self, L, t):
        return (L, tuple(sorted((k, v) for k, v in t.items() if v)))

    def run(self, pairs):
        """Score (level, talents) pairs, fetching only what is not cached."""
        keys = [self.key(L, t) for L, t in pairs]
        todo = sorted({k for k in keys if k not in self.cache})
        res = self.pool.map(score_job, [(L, it, self.sp, self.hp, self.top) for L, it in todo], chunksize=4)
        self.cache.update(zip(todo, res))
        return [self.cache[k] for k in keys]

    def mean(self, order, levels=LEVELS):
        return sum(self.run([(L, counts(order[:L - 9])) for L in levels])) / len(levels)


# ---------------------------------------------------------------- greedy fill
def greedy(sc, n=46):
    order = ['ImprovedCorruption'] * LOCK
    while len(order) < n:
        t, L, left = counts(order), len(order) + 10, n - len(order)
        singles = [(k,) for k in ALL if k not in NO_VALUE and addable(t, k)]
        base = sc.run([(L, t)])[0]
        gains = sc.run([(L, counts(order + list(m))) for m in singles])
        pref = {m[0]: base - g for m, g in zip(singles, gains)}
        packs = []
        for k in ALL:
            if k not in NO_VALUE and t.get(k, 0) < ALL[k][2] and not addable(t, k):
                p = unlock(t, k, pref, left)
                if p and tuple(p) not in packs:
                    packs.append(tuple(p))
        scored = [(pref[m[0]], m) for m in singles]
        for m in packs:
            lv = [L + i for i in range(len(m))]
            before = sc.run([(x, t) for x in lv])
            after = sc.run([(x, counts(order + list(m[:i + 1]))) for i, x in enumerate(lv)])
            scored.append((sum(b - a for b, a in zip(before, after)) / len(m), m))
        rate, m = max(scored, key=lambda x: x[0])
        order += list(m[:left])
    return order


# ---------------------------------------------------------------- polish: move points or runs
def runs_of(order):
    out, i = [], LOCK
    while i < len(order):
        j = i
        while j < len(order) and order[j] == order[i]:
            j += 1
        out.append((i, j))
        i = j
    return out


def candidates(order, reach=8):
    seen, out = set(), []
    for i, j in runs_of(order):
        for a, b in ((i, j), (i, i + 1), (j - 1, j)):
            block, rest = order[a:b], order[:a] + order[b:]
            for pos in range(max(LOCK, a - reach), min(len(rest), a + reach) + 1):
                new = rest[:pos] + block + rest[pos:]
                key = tuple(new)
                if new != order and key not in seen and legal(new):
                    seen.add(key)
                    out.append(new)
    return out


def polish(sc, order, rounds=12):
    cur = sc.mean(order)
    for _ in range(rounds):
        cands = candidates(order)
        sc.run([(L, counts(o[:L - 9])) for o in cands for L in LEVELS])
        best = min(cands, key=sc.mean)
        val = sc.mean(best)
        if val >= cur - 1e-6:
            break
        order, cur = best, val
    return order


def substitutes(order, start):
    """Orders with one point from position `start` on swapped for a different talent (legal at every level)."""
    out = []
    for p in range(max(LOCK, start), len(order)):
        for b in ALL:
            if b != order[p] and b not in NO_VALUE:
                new = order[:p] + [b] + order[p + 1:]
                if legal(new):
                    out.append(new)
    return out


def improve(sc, order, start=30, rounds=10):
    """Alternate point swaps (from `start` on, where the page's order spends its low-value points) and moves."""
    cur = sc.mean(order)
    for _ in range(rounds):
        cands = substitutes(order, start)
        sc.run([(L, counts(o[:L - 9])) for o in cands for L in LEVELS if L - 9 > start])
        best = min(cands, key=sc.mean)
        if sc.mean(best) >= cur - 1e-6:
            break
        order = polish(sc, best, rounds=4)
        cur = sc.mean(order)
    return order


# ---------------------------------------------------------------- the solo build from 56
def solo_build(sc60, start, rounds=8):
    """One-point moves at level 60 (Improved Corruption kept at 5), then the last 4 points ordered by removal."""
    t, cur = dict(start), sc60.run([(60, start)])[0]
    for _ in range(rounds):
        cands = []
        for a in list(t):
            if a == 'ImprovedCorruption':
                continue
            less = dict(t, **{a: t[a] - 1})
            if not less[a]:
                del less[a]
            if valid(less):
                cands += [dict(less, **{b: less.get(b, 0) + 1}) for b in ALL if b != a and b not in NO_VALUE and addable(less, b)]
        res = sc60.run([(60, x) for x in cands])
        i = min(range(len(res)), key=lambda j: res[j])
        if res[i] >= cur - 1e-9:
            break
        t, cur = cands[i], res[i]
    return t


def solo_order(sc60, t, planner):
    """Order a 51-point build: the last 4 points are the ones that cost least at 59, 58, 57 and 56 (dropped one at
    a time); the first 47 go tree by tree (Affliction first), in planner order within a tree where legal."""
    t, tail = dict(t), []
    for L in (59, 58, 57, 56):
        opts = []
        for a in t:
            less = dict(t, **{a: t[a] - 1})
            if not less[a]:
                del less[a]
            if a != 'ImprovedCorruption' and valid(less):
                opts.append((a, less))
        res = sc60.run([(L, less) for _, less in opts])
        a, less = opts[min(range(len(opts)), key=lambda j: res[j])]
        tail.insert(0, a)
        t = less
    rank = {k: i for i, k in enumerate(dict.fromkeys(planner))}
    pref = sorted(ALL, key=lambda k: (ALL[k][0], rank.get(k, 99), ALL[k][1]))
    head, have = [], {}
    while len(head) < sum(t.values()):
        k = next(k for k in pref if have.get(k, 0) < t.get(k, 0) and valid(dict(have, **{k: have.get(k, 0) + 1})))
        have[k] = have.get(k, 0) + 1
        head.append(k)
    return head + tail


def table(scorers, orders, levels):
    """Seconds per kill per level for each (label, order), full scoring, SP 1.0 and 2.0."""
    labels = [lab for lab, _ in orders]
    for sp, sc in scorers.items():
        print(f'\n#### SP {sp} x level\n')
        print('| L | ' + ' | '.join(labels) + ' | change |')
        print('|---|' + '---|' * (len(labels) + 1))
        vals = {lab: sc.run([(L, counts(o[:L - 9])) for L in levels]) for lab, o in orders}
        for i, L in enumerate(levels):
            a, b = vals[labels[0]][i], vals[labels[-1]][i]
            print(f'| {L} | ' + ' | '.join(f'{vals[lab][i]:.2f}' for lab in labels) + f' | {100 * (b / a - 1):+.1f}% |')
        m = {lab: sum(v) / len(v) for lab, v in vals.items()}
        a, b = m[labels[0]], m[labels[-1]]
        print('| mean | ' + ' | '.join(f'{m[lab]:.2f}' for lab in labels) + f' | {100 * (b / a - 1):+.1f}% |')


def main():
    tal_order, solo56 = page_order('TAL_ORDER'), page_order('SOLO56')
    assert len(tal_order) == 46 and len(solo56) == 51 and legal(tal_order) and legal(solo56)
    with Pool(max(1, (os.cpu_count() or 2) - 2)) as pool:
        sc = Scorer(pool, 1.0)
        g = greedy(sc)
        print('greedy fill:', page_format(g), f'mean {sc.mean(g):.3f} (HP5, one modifier pass)')
        seeds = [polish(sc, g), polish(sc, tal_order)]
        for s in seeds:
            print('polished:', page_format(s), f'mean {sc.mean(s):.3f}')
        best = improve(sc, min(seeds, key=sc.mean))
        print('after point swaps:', page_format(best), f'mean {sc.mean(best):.3f}')
        full = {sp: Scorer(pool, sp, HP_GRID, 3) for sp in (1.0, 2.0)}
        print('\n### Planner order, levels 10 to 55: TAL_ORDER vs the new order')
        table(full, [('TAL_ORDER', tal_order), ('new order', best)], list(LEVELS))
        print('\nNew TAL_ORDER:\n\n    const TAL_ORDER = ' + page_format(best) + ';')

        sc60 = Scorer(pool, 1.0)
        b60 = solo_build(sc60, counts(solo56))
        new56 = solo_order(sc60, b60, best)
        assert legal(new56) and len(new56) == 51
        print('\n### Solo build from 56: SOLO56 vs the new one')
        table(full, [('SOLO56', solo56), ('new SOLO56', new56)], list(range(56, 61)))
        print('\nNew SOLO56:\n\n    const SOLO56 = ' + page_format(new56) + ';')


if __name__ == '__main__':
    main()
