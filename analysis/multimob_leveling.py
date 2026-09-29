"""Multi-mob leveling (v8, phase 3): does fighting several mobs at once beat killing them one at a time?

Run from the repo root: python analysis/multimob_leveling.py [section ...]
Sections: calib main builds pets sens sensdemo (default: all; about 8 minutes on 16 cores). Prints markdown tables.
Model: models/multimob.py, a separate expected-value model with its own labelled assumptions (M1 to M17, see the
Setup class and the constants there). The single-mob reference is character.evaluate, the v8 sim with every
modifier. Both average mob health over x0.8 to x1.2 in 5 steps, and a pull size only counts when you survive it at
every one of them. Seconds per kill = (fight + pull travel + rest) / n, lower is better. Percent is against the
single-mob best of the same build and pet unless a column says otherwise.
"""
import os
import sys
from dataclasses import replace
from multiprocessing import Pool

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'models'))
sys.path.insert(0, HERE)

import character as c
import leveling_sim as ls
import multimob as mm
from character import evaluate, valid, POLICIES as SINGLE_POLICIES
from leveling_paths import AFF_FIRST
from destro_leveling import BABILON, SOLO56

INF = float('inf')
LEVELS = tuple(range(10, 61, 5))
NS = (1, 2, 3, 4, 5)
HP5 = (0.8, 0.9, 1.0, 1.1, 1.2)
SP = 1.0


def rep(*p):
    out = []
    for k, n in p:
        out += [k] * n
    return out


# Mine, untested in game: a Demonology build for Voidwalker-tanked AoE. Your health and the Voidwalker's first
# (Demonic Embrace, Fel Vitality, Demonic Energies heals it from your spell damage, Soul Link, Master Demonologist's
# physical reduction), then Destruction for Rain of Fire and Hellfire (Cataclysm, Molten Skin, Ruin, Agonizing Flames).
AOE_DEMO = rep(('DemonicEmbrace', 5), ('FelVitality', 3), ('DemonicEnergies', 2), ('ImprovedVoidwalker', 3),
               ('UnholyPower', 5), ('DemonicSacrifice', 1), ('MasterSummoner', 2), ('FelDomination', 1), ('SoulLink', 1),
               ('DemonicKnowledge', 3), ('MasterDemonologist', 5), ('DemonicPact', 1), ('Bane', 5), ('Cataclysm', 3),
               ('MoltenSkin', 5), ('Ruin', 2), ('AgonizingFlames', 3), ('Ruin', 1))
ORDERS = {'plan': None, 'babilon': BABILON, 'aoe-demo': AOE_DEMO}


def talents(bname, L):
    """The build at level L (L - 9 points). 'plan' is the page's order: AFF_FIRST, then SOLO56 from 56."""
    order = ORDERS[bname] or (AFF_FIRST if L < 56 else SOLO56)
    t = {}
    for k in order[:max(0, L - 9)]:
        t[k] = t.get(k, 0) + 1
    return t


for _b in ORDERS:
    for _L in range(10, 61):
        assert valid(talents(_b, _L)), (_b, _L)

# ---------------------------------------------------------------- policies
AB = dict(Corruption='Corr', BoA='BoA', SiphonLife='SL', Immolate='Imm', CoE='CoE', Havoc='Havoc', Fear='Fear',
          RoF='RoF', Hellfire='HF', DrainLife='DL', ShadowBolt='SB', Wand='Wand')
CAREFUL = dict(lt_hp_floor=0.6, drain_below=0.5)   # no Life Tap under 60% health, Drain Life first under 50%
FILLS = ('Wand', 'DrainLife', 'ShadowBolt')
SPREAD_SETS = [('Corruption',), ('Corruption', 'BoA'), ('Corruption', 'BoA', 'SiphonLife'), ('Corruption', 'CoE'),
               ('Immolate',), ('Corruption', 'Immolate'), ('Corruption', 'BoA', 'Immolate'),
               ('Corruption', 'CoE', 'Immolate'), ('Corruption', 'BoA', 'SiphonLife', 'Immolate')]
KITE_SETS = [('Corruption',), ('Corruption', 'BoA'), ('Corruption', 'BoA', 'SiphonLife'), ('Corruption', 'Immolate'),
             ('Corruption', 'BoA', 'Immolate'), ('Corruption', 'CoE', 'Immolate')]
AOE_SETS = [('RoF',), ('Corruption', 'RoF'), ('Corruption', 'BoA', 'RoF'), ('Hellfire', 'RoF'),
            ('Corruption', 'Hellfire', 'RoF'), ('Hellfire',), ('Corruption', 'Hellfire'),
            ('Corruption', 'BoA', 'Hellfire', 'RoF'), ('Corruption', 'BoA', 'SiphonLife', 'RoF'),
            ('Corruption', 'BoA', 'SiphonLife', 'Hellfire', 'RoF')]
HF_BANDS = ((0.6, 0.35), (0.9, 0.6))                # Hellfire: start above, stop under this share of your health


def policy(steps, spread, care, tag='', **kw):
    name = '+'.join(AB[s] for s in steps) + tag + (' careful' if care else '')
    return name, dict(prio=list(steps), spread=spread, **(CAREFUL if care else {}), **kw)


def multidot_policies():
    """Strategy 1. Simplest first: equal castable steps run once and the first name wins."""
    out = {}
    for fear in (False, True):
        for havoc in (False, True):
            for s in SPREAD_SETS:
                for f in FILLS:
                    for care in (False, True):
                        steps = ['Fear'] * fear + ['Havoc'] * havoc + list(s) + [f]
                        out.update([policy(steps, True, care)])
    return out


def aoe_policies():
    """Strategy 2. After the pull is down to one mob the area spells stop and the filler finishes it."""
    out = {}
    for havoc in (False, True):
        for s in AOE_SETS:
            for f in ('DrainLife', 'Wand'):
                for care in (False, True):
                    steps = ['Havoc'] * havoc + list(s) + [f]
                    bands = HF_BANDS if 'Hellfire' in s else HF_BANDS[:1]
                    for hs, he in bands:
                        tag = ' HF %d-%d%%' % (100 * hs, 100 * he) if 'Hellfire' in s else ''
                        out.update([policy(steps, True, care, tag, hf_start=hs, hf_stop=he)])
    return out


def kite_policies():
    """Strategy 3. DoTs only on the mob you are killing; one untouched mob kept feared."""
    out = {}
    for s in KITE_SETS:
        for f in FILLS:
            for care in (False, True):
                out.update([policy(['Fear'] + list(s) + [f], False, care)])
    return out


STRATS = {'multidot': ('Multi-DoT', multidot_policies(), 'one'),
          'aoe': ('Voidwalker AoE', aoe_policies(), 'suffering'),
          'kite': ('Fear-kite', kite_policies(), 'one')}


# ---------------------------------------------------------------- workers
def solve(job):
    """(strategy, build, pet, level, n, setup, sp) -> the fastest safe pull as a plain dict (spk inf: none safe)."""
    strat, bname, pet, L, n, su, sp = job
    key = dict(strat=strat, build=bname, pet=pet, L=L, n=n)
    if strat == 'aoe' and L < mm.ROF[0][0]:
        return dict(key, name='n/a', spk=INF, why='no Rain of Fire before 20')
    ch = c.make_char(L, talents(bname, L), sp, pet)
    pols = STRATS[strat][1]
    if su.hold == 'suffering' and pet == 'voidwalker' and n > 1 and L >= mm.SUFFERING[0]:
        ns, rs = mm.best_pull(ch, pet, n, HP5, pols, su)
        no, ro = mm.best_pull(ch, pet, n, HP5, pols, replace(su, hold='one'))
        spk, m = mm.suffering_mix(rs['cycle'] if ns else INF, ro['cycle'] if no else INF, n)
        if spk == INF:
            return dict(key, name=None, spk=INF, why=why(rs))
        if m < 0:
            return pack(key, no + ' (Torment only)', ro, spk)
        if m > 0:
            label = ' (Suffering, then %d Torment-only pull%s: %s)' % (m, 's' * (m > 1), no)
        else:
            label = ' (Suffering, waits for its cooldown)' if rs['cycle'] < mm.SUFFERING[1] else ' (Suffering)'
        return pack(key, ns + label, rs, spk)
    name, r = mm.best_pull(ch, pet, n, HP5, pols, su)
    if name is None:
        return dict(key, name=None, spk=INF, why=why(r))
    return pack(key, name, r, r['spk'])


def why(r):
    if r['died']:
        return 'Voidwalker died, then you' if r['pet_died'] else 'you died'
    return 'stalled' if r['stalled'] else 'under the health margin'


def pack(key, name, r, spk):
    return dict(key, name=name, spk=spk, ttk=r['ttk'], rest=r['rest'], cycle=r['cycle'], travel=r['travel'],
                min_hp=r['min_hp'], pet_died=r['pet_died'], vw_min=r['vw_min'])


ORIG_SPK, ORIG_MAKE = c.seconds_per_kill, c.make_char


def single(job):
    """(build, pet, level, sp, rest mode, mob damage multiple) -> character.evaluate's best, the v8 single-mob sim."""
    bname, pet, L, sp, rest, mob_dps = job

    def spk_eat(ch, hp, pol, travel=8.0, **kw):
        s = ORIG_SPK(ch, hp, pol, travel=travel, **kw)
        floor = mm.eat_floor(ch, s['net_hp'], travel)
        if floor > s['rest']:
            s['rest'], s['spk'] = floor, s['ttk'] + travel + floor
        return s

    def make(*a, **kw):
        ch = ORIG_MAKE(*a, **kw)
        ch.mob_dps *= mob_dps
        return ch
    c.seconds_per_kill = spk_eat if rest == 'eat' else ORIG_SPK
    c.make_char = make if mob_dps != 1.0 else ORIG_MAKE
    try:
        name, s = evaluate(L, talents(bname, L), pet, sp, hp_mults=HP5)
    finally:
        c.seconds_per_kill, c.make_char = ORIG_SPK, ORIG_MAKE
    return dict(build=bname, pet=pet, L=L, name=name, spk=s['spk'], ttk=s['ttk'], rest=s['rest'])


def calib(job):
    """n = 1 in the multi-mob engine vs seconds_per_kill on the same base rotation (no modifiers)."""
    L, pet = job
    ch = c.make_char(L, talents('plan', L), SP, pet)
    hp = c.mob_hp(L)
    out, seen = [], set()
    for name, pol in SINGLE_POLICIES.items():
        sig = ls.usable_steps(pol['prio'], ch)
        if sig in seen or set(sig) & {'Conflagrate', 'Wrack', 'Incinerate'}:     # not in the multi-mob engine
            continue
        seen.add(sig)
        a = ls.seconds_per_kill(ch, hp, pol)['spk']
        b = mm.pull(ch, pet, 1, hp, dict(pol, spread=True))['spk']
        out.append((L, pet, name, a, b))
    return out


# ---------------------------------------------------------------- formatting
def pct(x, ref):
    return '%+.1f%%' % (100 * (x / ref - 1))


def cell(r, ref):
    if r is None or r['spk'] == INF:
        return 'dies' if r and r.get('name') is None else 'n/a'
    return '%.1f (%s)' % (r['spk'], pct(r['spk'], ref))


def best_n(rows):
    ok = [r for r in rows if r['spk'] < INF]
    return min(ok, key=lambda r: r['spk']) if ok else None


def largest_safe(rows):
    ok = [r['n'] for r in rows if r['spk'] < INF]
    return max(ok) if ok else 0


def strategy_table(res, ref, strat, bname, pet):
    print('\n**%s**, %s, %s\n' % (STRATS[strat][0], bname, pet))
    print('| L | single best | ' + ' | '.join('n=%d' % n for n in NS) + ' | largest safe n | fastest pull |')
    print('|---|---|' + '---|' * len(NS) + '---|---|')
    for L in LEVELS:
        rows = [res[(strat, bname, pet, L, n)] for n in NS]
        r0 = ref[(bname, pet, L)]
        b = best_n(rows)
        tail = 'n=%d %s' % (b['n'], b['name']) if b else '-'
        print('| %d | %.2f %s | %s | %d | %s |' % (L, r0['spk'], r0['name'], ' | '.join(cell(r, r0['spk']) for r in rows),
                                                   largest_safe(rows), tail))


def time_table(res, strat, bname, pet, levels):
    print('\nWhere the time goes, %s (%s, %s), the fastest safe pull size:\n' % (STRATS[strat][0], bname, pet))
    print('| L | n | fight | travel | rest | pull cycle | seconds per kill | lowest health | Voidwalker lowest |')
    print('|---|---|---|---|---|---|---|---|---|')
    for L in levels:
        b = best_n([res[(strat, bname, pet, L, n)] for n in NS])
        if b is None:
            continue
        vw = '-' if b['vw_min'] is None else ('dies' if b['pet_died'] else '%d%%' % (100 * b['vw_min']))
        wait = ' (%.1f with the Suffering wait)' % (b['spk'] * b['n']) if b['spk'] * b['n'] > b['cycle'] + 0.05 else ''
        print('| %d | %d | %.1f | %.1f | %.1f | %.1f%s | %.2f | %d%% | %s |' % (
            L, b['n'], b['ttk'], b['travel'], b['rest'], b['cycle'], wait, b['spk'], 100 * b['min_hp'], vw))


# ---------------------------------------------------------------- sections
def run_grid(pool, combos, su_for, sp=SP):
    jobs = [(s, b, p, L, n, su_for(s), sp) for s, b, p in combos for L in LEVELS for n in NS]
    return {(r['strat'], r['build'], r['pet'], r['L'], r['n']): r for r in pool.map(solve, jobs, chunksize=1)}


def run_single(pool, pairs, sp=SP, rest='pooled', mob_dps=1.0):
    jobs = [(b, p, L, sp, rest, mob_dps) for b, p in pairs for L in LEVELS]
    return {(r['build'], r['pet'], r['L']): r for r in pool.map(single, jobs, chunksize=1)}


def default_su(strat):
    return mm.Setup(hold=STRATS[strat][2])


def report_calib(pool):
    rows = [x for part in pool.map(calib, [(L, p) for L in LEVELS for p in ('voidwalker', 'succubus')]) for x in part]
    gaps = sorted(rows, key=lambda r: -abs(r[4] / r[3] - 1))
    print('\n## Calibration: n = 1 in the multi-mob engine vs the single-mob sim, same base rotation\n')
    print('%d rotation x level x pet checks. Largest gaps:\n' % len(rows))
    print('| L | pet | rotation | single-mob sim | multi-mob engine | gap |')
    print('|---|---|---|---|---|---|')
    for L, pet, name, a, b in gaps[:5]:
        print('| %d | %s | %s | %.3f | %.3f | %s |' % (L, pet, name, a, b, pct(b, a)))
    within = sum(1 for r in rows if abs(r[4] / r[3] - 1) < 0.001)
    print('\n%d of %d within 0.1%%.' % (within, len(rows)))


def report_main(pool):
    combos = [(s, 'plan', 'voidwalker') for s in STRATS]
    res = run_grid(pool, combos, default_su)
    ref = run_single(pool, [('plan', 'voidwalker')])
    print('\n## Page plan with the Voidwalker, every strategy and pull size\n')
    for s in STRATS:
        strategy_table(res, ref, s, 'plan', 'voidwalker')
    for s in STRATS:
        time_table(res, s, 'plan', 'voidwalker', LEVELS)
    return res, ref


def summary_row(res, ref, strat, bname, pet, L, base):
    """The fastest safe pull of 2 or more: its n, seconds per kill, vs the build's own single best, vs the plan's."""
    r = res[(strat, bname, pet, L, 1)]
    if r.get('name') == 'n/a':
        return 'n/a'
    b = best_n([res[(strat, bname, pet, L, n)] for n in NS[1:]])
    if b is None:
        return 'dies at 2+'
    return 'n=%d %.1f (%s; %s vs plan)' % (b['n'], b['spk'], pct(b['spk'], ref[(bname, pet, L)]['spk']), pct(b['spk'], base))


def report_builds(pool, main_ref):
    builds = ('plan', 'babilon', 'aoe-demo')
    combos = [(s, b, 'voidwalker') for s in STRATS for b in builds[1:]]
    res = run_grid(pool, combos, default_su)
    ref = {**main_ref, **run_single(pool, [(b, 'voidwalker') for b in builds[1:]])}
    print('\n## Builds (Voidwalker): best pull size above 1, vs the same build one at a time and vs the page plan\n')
    for s in STRATS:
        print('\n**%s**\n' % STRATS[s][0])
        print('| L | plan single | babilon single | aoe-demo single | babilon | aoe-demo |')
        print('|---|---|---|---|---|---|')
        for L in LEVELS:
            base = main_ref[('plan', 'voidwalker', L)]['spk']
            print('| %d | %.2f | %.2f | %.2f | %s | %s |' % (
                L, base, ref[('babilon', 'voidwalker', L)]['spk'], ref[('aoe-demo', 'voidwalker', L)]['spk'],
                summary_row(res, ref, s, 'babilon', 'voidwalker', L, base),
                summary_row(res, ref, s, 'aoe-demo', 'voidwalker', L, base)))
    for b in builds[1:]:
        for s in ('aoe', 'multidot'):
            strategy_table(res, ref, s, b, 'voidwalker')
    return res


def report_pets(pool, main_ref):
    combos = [(s, 'plan', 'succubus') for s in ('multidot', 'kite')]
    res = run_grid(pool, combos, default_su)
    ref = {**main_ref, **run_single(pool, [('plan', 'succubus')])}
    print('\n## Succubus (page plan): no pet holds a mob, every mob hits you\n')
    for s in ('multidot', 'kite'):
        strategy_table(res, ref, s, 'plan', 'succubus')
    print('\n| L | Voidwalker single | Succubus single |')
    print('|---|---|---|')
    for L in LEVELS:
        print('| %d | %.2f | %.2f |' % (L, main_ref[('plan', 'voidwalker', L)]['spk'], ref[('plan', 'succubus', L)]['spk']))


SENS = [
    ('default', {}, {}),
    ('pull travel 8 + 3 s a mob', dict(travel_per=3.0), {}),
    ('pull travel 8 + 10 s a mob', dict(travel_per=10.0), {}),
    ('M1: Voidwalker holds every mob, always', dict(hold='all'), {}),
    ('M1: Suffering in every strategy', dict(hold='suffering'), {}),
    ('M1: no Suffering (Torment only)', dict(hold='one'), {}),
    ('M3: Fear lasts half as long', dict(fear_mult=0.5), {}),
    ('M4: Voidwalker health x0.5', dict(vw_hp=0.5), {}),
    ('M4: Voidwalker health x2', dict(vw_hp=2.0), {}),
    ('M4: Voidwalker never dies', dict(vw_hp=0.0), {}),
    ('M5: mobs hit the Voidwalker as hard as you', dict(vw_taken=1.0), {}),
    ('M6: mob damage x0.7', dict(mob_dps=0.7), dict(mob_dps=0.7)),
    ('M6: mob damage x1.3', dict(mob_dps=1.3), dict(mob_dps=1.3)),
    ('M7: health comes back only by eating', dict(rest='eat'), dict(rest='eat')),
    ('M8: keep 20% health', dict(margin=0.2), {}),
    ('M9: area spells never crit', dict(aoe_crit=False), {}),
    ('gear: spell power 2 x level', {}, dict(sp=2.0)),
]
SENS_LEVELS = (20, 30, 40, 50, 60)


def report_sens(pool):
    print('\n## Sensitivity (page plan, Voidwalker): fastest pull over all strategies and n >= 2 vs one at a time\n')
    print('| assumption | ' + ' | '.join('L%d' % L for L in SENS_LEVELS) + ' |')
    print('|---|' + '---|' * len(SENS_LEVELS))
    for label, su_kw, ref_kw in SENS:
        sp = ref_kw.get('sp', SP)

        def su_for(s, kw=su_kw):
            return replace(default_su(s), **kw)
        jobs = [(s, 'plan', 'voidwalker', L, n, su_for(s), sp) for s in STRATS for L in SENS_LEVELS for n in NS[1:]]
        res = pool.map(solve, jobs, chunksize=1)
        refs = {r['L']: r for r in pool.map(single, [('plan', 'voidwalker', L, sp, ref_kw.get('rest', 'pooled'),
                                                      ref_kw.get('mob_dps', 1.0)) for L in SENS_LEVELS])}
        cells = []
        for L in SENS_LEVELS:
            b = best_n([r for r in res if r['L'] == L])
            if b is None:
                cells.append('all die')
                continue
            safe = {s: max([r['n'] for r in res if r['L'] == L and r['strat'] == s and r['spk'] < INF] or [1])
                    for s in STRATS}
            cells.append('%s %s n=%d (safe n %d/%d/%d)' % (pct(b['spk'], refs[L]['spk']), short(b['strat']), b['n'],
                                                           safe['multidot'], safe['aoe'], safe['kite']))
        print('| %s | %s |' % (label, ' | '.join(cells)))
    print('\nCells: best pull vs the single-mob best under the same assumption, its strategy (DoT = multi-DoT, AoE, '
          'Kite) and n, then the largest safe n for multi-DoT/AoE/Fear-kite (1: no pull of 2 or more survives).')


def short(strat):
    return dict(multidot='DoT', aoe='AoE', kite='Kite')[strat]


DEMO_LEVELS = (30, 35, 40, 45, 50, 55, 60)


def report_sens_demo(pool):
    """The case that wins in the default run: Voidwalker AoE with the aoe-demo build, against the page plan's best
    single-mob option with either pet (the Succubus is faster at 30 to 40)."""
    print('\n## Sensitivity of the one winner: Voidwalker AoE, aoe-demo build, vs the page plan one at a time '
          '(best of Voidwalker and Succubus)\n')
    print('| assumption | ' + ' | '.join('L%d' % L for L in DEMO_LEVELS) + ' |')
    print('|---|' + '---|' * len(DEMO_LEVELS))
    skip = ('M1: Suffering in every strategy', 'M3: Fear lasts half as long')    # the AoE default / no Fear in AoE
    default_rows = None
    for label, su_kw, ref_kw in (x for x in SENS if x[0] not in skip):
        sp, rest, mob = ref_kw.get('sp', SP), ref_kw.get('rest', 'pooled'), ref_kw.get('mob_dps', 1.0)
        su = replace(default_su('aoe'), **su_kw)
        res = pool.map(solve, [('aoe', 'aoe-demo', 'voidwalker', L, n, su, sp) for L in DEMO_LEVELS for n in NS[1:]],
                       chunksize=1)
        refs = pool.map(single, [('plan', p, L, sp, rest, mob) for p in ('voidwalker', 'succubus') for L in DEMO_LEVELS])
        cells = []
        for L in DEMO_LEVELS:
            ref = min(r['spk'] for r in refs if r['L'] == L)
            b = best_n([r for r in res if r['L'] == L])
            cells.append('dies' if b is None else '%s n=%d' % (pct(b['spk'], ref), b['n']))
        print('| %s | %s |' % (label, ' | '.join(cells)))
        if default_rows is None:
            default_rows = res
    print('\nWhere the time goes, default assumptions:\n')
    print('| L | n | fight | travel | rest | pull cycle | seconds per kill | lowest health | Voidwalker lowest | pull |')
    print('|---|---|---|---|---|---|---|---|---|---|')
    for L in DEMO_LEVELS:
        b = best_n([r for r in default_rows if r['L'] == L])
        if b is None:
            continue
        vw = 'dies' if b['pet_died'] else '%d%%' % (100 * b['vw_min'])
        print('| %d | %d | %.1f | %.1f | %.1f | %.1f | %.2f | %d%% | %s | %s |' % (
            L, b['n'], b['ttk'], b['travel'], b['rest'], b['cycle'], b['spk'], 100 * b['min_hp'], vw, b['name']))


def main(sections):
    with Pool(max(1, (os.cpu_count() or 2) - 2)) as pool:
        if 'calib' in sections:
            report_calib(pool)
        main_ref = None
        if {'main', 'builds', 'pets'} & set(sections):
            _res, main_ref = report_main(pool) if 'main' in sections else (None, run_single(pool, [('plan', 'voidwalker')]))
        if 'builds' in sections:
            report_builds(pool, main_ref)
        if 'pets' in sections:
            report_pets(pool, main_ref)
        if 'sens' in sections:
            report_sens(pool)
        if 'sensdemo' in sections:
            report_sens_demo(pool)


if __name__ == '__main__':
    main(sys.argv[1:] or ['calib', 'main', 'builds', 'pets', 'sens', 'sensdemo'])
