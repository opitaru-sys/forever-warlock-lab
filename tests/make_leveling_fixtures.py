"""Generate expected leveling results from the Python model for tests/leveling_parity_test.js.
Run from the repo root: python tests/make_leveling_fixtures.py
"""
import sys, io, json, contextlib
sys.path.insert(0, 'models'); sys.path.insert(0, 'analysis')
from character import make_char, mob_hp, POLICIES, valid
import leveling_sim as ls
with contextlib.redirect_stdout(io.StringIO()):
    from leveling_paths import build, AFF_FIRST, DK_PATH

def rep(*p):
    d = {}
    for k, n in p: d[k] = d.get(k, 0) + n
    return d
FIVE31 = rep(('ImprovedCorruption',5),('DemonicEmbrace',5),('UnholyPower',5),('FelVitality',3),('ImprovedVoidwalker',2),
    ('DemonicSacrifice',1),('MasterSummoner',2),('ImprovedSayaad',2),('FelDomination',1),('DemonicBrand',1),
    ('SoulLink',1),('DemonicKnowledge',3),('MasterDemonologist',4),('DemonicPact',1))

def evaluate(L, tal, pet, sp, aggro=False):
    best = None
    for name, pol in POLICIES.items():
        ch = make_char(L, tal, sp, pet)
        if aggro and pet not in ('voidwalker', 'none'):
            ch.taken_frac = 0.10 * (0.70 if tal.get('SoulLink') else 1.0)
        s = ls.seconds_per_kill(ch, mob_hp(L), dict(pol, amp=False))
        if best is None or s['spk'] < best[1]['spk']:
            best = (name, s)
    n, s = best
    return dict(policy=n, spk=s['spk'], ttk=s['ttk'], rest=s['rest'], healed=s['healed'])

cases = []
for L in (10, 16, 20, 25, 30, 34, 40, 45, 50, 56, 60):
    n = L - 9
    builds = [('aff-path', build(AFF_FIRST, n)), ('dk-path', build(DK_PATH, n)), ('empty', {})]
    if n >= 36:
        builds.append(('5-31-0 imp sac', dict(FIVE31, _sac='imp')))
    for bname, tal in builds:
        assert valid({k: v for k, v in tal.items() if not k.startswith('_')}), (bname, L)
        for pet in ('voidwalker', 'succubus', 'felhunter', 'none'):
            for sp in (1.0, 2.0):
                for aggro in ((False, True) if pet in ('succubus', 'felhunter') else (False,)):
                    r = evaluate(L, tal, pet, sp, aggro)
                    cases.append(dict(level=L, build=bname, talents=tal, pet=pet, sp=sp, aggro=aggro, **r))
json.dump(cases, open('tests/leveling_fixtures.json', 'w'), indent=0)
print(len(cases), 'cases written')
