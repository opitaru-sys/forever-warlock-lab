"""Generate expected leveling results from the Python model for tests/leveling_parity_test.js.
Run from the repo root: python tests/make_leveling_fixtures.py
"""
import sys, io, json, contextlib
sys.path.insert(0, 'models'); sys.path.insert(0, 'analysis')
from character import valid, evaluate
with contextlib.redirect_stdout(io.StringIO()):
    from leveling_paths import build, AFF_FIRST, DK_PATH, PLANNER_V8, SOLO56_V8
    from destro_leveling import BABILON, COMMUNITY_34, SPEEDRUN

def rep(*p):
    d = {}
    for k, n in p: d[k] = d.get(k, 0) + n
    return d
FIVE31 = rep(('ImprovedCorruption',5),('DemonicEmbrace',5),('UnholyPower',5),('FelVitality',3),('ImprovedVoidwalker',2),
    ('DemonicSacrifice',1),('MasterSummoner',2),('ImprovedSayaad',2),('FelDomination',1),('DemonicBrand',1),
    ('SoulLink',1),('DemonicKnowledge',3),('MasterDemonologist',4),('DemonicPact',1))
# Incinerate, Fire and Brimstone and Decimation (Soul Fire) are only reached by these two
FULL_DESTRO = rep(('Suppression',5),('ImprovedCorruption',5),('Bane',5),('Cataclysm',3),('Aftermath',2),('Ruin',5),('Shadowburn',1),
    ('Conflagrate',1),('AgonizingFlames',3),('Intensity',1),('FireAndBrimstone',3),('BaneOfHavoc',1),('ShadowAndFlame',5),('Incinerate',1),
    ('ImprovedShadowBolt',5),('MoltenSkin',5))
DECIMATION = rep(('ImprovedImp',3),('DemonicEmbrace',5),('UnholyPower',2),('FelVitality',3),('DemonicAegis',2),('DemonicSacrifice',1),
    ('MasterSummoner',2),('Decimation',2),('Bane',5),('Cataclysm',3),('Aftermath',2),('Ruin',5),('Shadowburn',1),('ImprovedShadowBolt',5),
    ('AgonizingFlames',3),('Conflagrate',1))

def case(L, bname, tal, pet, sp, aggro=False, **opts):
    n, s = evaluate(L, tal, pet, sp, aggro=aggro, **opts)
    return dict(level=L, build=bname, talents=tal, pet=pet, sp=sp, aggro=aggro, opts=opts,
                policy=n, spk=s['spk'], ttk=s['ttk'], rest=s['rest'], healed=s['healed'])

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
                    cases.append(case(L, bname, tal, pet, sp, aggro))
# v8: Destruction and curse cases (the reader builds of analysis/destro_leveling.py)
for L in (12, 20, 24, 28, 32, 38, 42, 48, 52, 60):
    n = L - 9
    for bname, order in (('babilon', BABILON), ('community-17-0-34', COMMUNITY_34), ('speedrun', SPEEDRUN)):
        tal = build(order, n)
        for pet in ('voidwalker', 'imp', 'succubus'):
            for sp in (1.0, 2.0):
                cases.append(case(L, bname, tal, pet, sp))
for L in (48, 52, 60):
    for bname, tal in (('full-destro', FULL_DESTRO), ('decimation', DECIMATION), ('succubus-sac', dict(DECIMATION, _sac='succubus'))):
        assert valid({k: v for k, v in tal.items() if not k.startswith('_')}) and sum(v for k, v in tal.items() if k[0] != '_') <= 51, bname
        for pet in ('voidwalker', 'imp', 'none'):
            for sp in (1.0, 2.0):
                cases.append(case(L, bname, tal, pet, sp))
# the switches: level scaling of direct damage, Suppression on Affliction spells only, Soul Harvest and drinking
for L in (20, 30, 40, 50, 60):
    for bname, tal in (('aff-path', build(AFF_FIRST, L - 9)), ('community-17-0-34', build(COMMUNITY_34, L - 9)),
                       ('speedrun', build(SPEEDRUN, L - 9))):
        for opts in (dict(dd_mode='scaled'), dict(dd_mode='wowhead'), dict(supp_all=False), dict(harvest_drink=True),
                     dict(lash_share=1.0), dict(hp_mults=[0.8, 0.9, 1.0, 1.1, 1.2])):
            cases.append(case(L, bname, tal, 'voidwalker' if 'lash_share' not in opts else 'succubus', 1.0, **opts))
# the v8 page orders proposed by analysis/planner_order.py (to 55, then the solo build from 56)
for L in (15, 20, 25, 30, 35, 40, 45, 50, 55, 56, 58, 60):
    tal = build(SOLO56_V8 if L >= 56 else PLANNER_V8, L - 9)
    for pet in ('voidwalker', 'succubus'):
        for sp in (1.0, 2.0):
            cases.append(case(L, 'page-v8', tal, pet, sp))
json.dump(cases, open('tests/leveling_fixtures.json', 'w'), indent=0)
print(len(cases), 'cases written')
