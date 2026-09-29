import random, time
import leveling_sim
from leveling_sim import Char, seconds_per_kill

AFF = {'ImprovedLifeTap': (0, 2), 'Suppression': (0, 5), 'ImprovedCorruption': (0, 5),
       'Malediction': (1, 5), 'SoulHarvesting': (1, 2), 'ImprovedDrains': (1, 3),
       'ImprovedBoA': (2, 2), 'FelConcentration': (2, 3), 'AmplifyCurse': (2, 1), 'Pandemic': (2, 3),
       'Malevolence': (3, 5), 'Nightfall': (3, 2), 'CurseOfExhaustion': (3, 1),
       'SiphonLife': (4, 1), 'SoulSiphon': (4, 3), 'ShadowMastery': (5, 5), 'Wrack': (6, 1)}
DEMO = {'ImprovedHealthFunnel': (0, 2), 'ImprovedImp': (0, 3), 'DemonicEmbrace': (0, 5), 'UnholyPower': (0, 5),
        'DemonicAegis': (1, 2), 'ImprovedVoidwalker': (1, 3), 'FelVitality': (1, 3), 'DemonicEnergies': (1, 2),
        'ImprovedSayaad': (2, 3), 'DemonicSacrifice': (2, 1), 'MasterSummoner': (2, 2),
        'Decimation': (3, 2), 'FelDomination': (3, 1), 'DemonicBrand': (3, 3),
        'ImprovedFelhunter': (4, 3), 'SoulLink': (4, 1), 'DemonicKnowledge': (4, 3),
        'MasterDemonologist': (5, 5), 'DemonicPact': (6, 1)}
PREREQ = {'Wrack': ('SiphonLife', 1), 'SoulLink': ('DemonicSacrifice', 1), 'DemonicPact': ('SoulLink', 1),
          'FelDomination': ('MasterSummoner', 2)}
TREES = [AFF, DEMO]


def valid(tal):
    for tree in TREES:
        rows = [0] * 7
        for k, (r, mx) in tree.items():
            p = tal.get(k, 0)
            if p < 0 or p > mx:
                return False
            rows[r] += p
        for r in range(7):
            if rows[r] and sum(rows[:r]) < 5 * r:
                return False
    for k, (req, n) in PREREQ.items():
        if tal.get(k, 0) and tal.get(req, 0) < n:
            return False
    return True


# ---------------------------------------------------------------- character assumptions
def make_char(L, tal, sp_per_level=1.0, pet='voidwalker', lt_base_mult=1.0):
    hp = 20 + 28 * L + 0.4 * L * L
    mana = 20 + 25 * L + 0.45 * L * L
    hp *= 1 + 0.02 * tal.get('DemonicEmbrace', 0) * 0.65    # stamina is ~65% of HP
    mana *= 1 + 0.05 * tal.get('FelVitality', 0) * 0.7         # Fel Vitality: +5%/rank max mana
    pet_base = {'voidwalker': 0.5, 'succubus': 1.1, 'imp': 0.8, 'felhunter': 0.8, 'none': 0.0}[pet]
    pet_dps = pet_base * L * (1 + .02 * tal.get('UnholyPower', 0))
    shadow = 1.0
    fel_sac = vw_sac = False
    pact = tal.get('DemonicPact', 0)
    sac = tal.get('_sac')          # which demon was sacrificed ('imp', 'felhunter', ...)
    if sac and (pact or pet == 'none'):
        if sac == 'imp':
            shadow *= 1.15
        if sac == 'felhunter':
            fel_sac = True
        if sac == 'voidwalker':
            vw_sac = True
    if pet == 'succubus':
        shadow *= 1 + .02 * tal.get('MasterDemonologist', 0)
    if tal.get('SoulLink') and pet != 'none':
        shadow *= 1.03
        pet_dps *= 1.03
    taken = {'voidwalker': 0.10, 'succubus': 1.0, 'imp': 1.0, 'felhunter': 1.0, 'none': 1.0}[pet]
    if tal.get('SoulLink') and pet != 'none':
        taken *= 0.70
    ch = Char(level=L, sp=sp_per_level * L, crit=0.05, spirit=15 + 1.2 * L, max_hp=hp, max_mana=mana,
              wand_dps=0.9 * L + 3, pet_dps=pet_dps, talents=tal, shadow_mult=shadow,
              mob_dps=0.035 * L * L, taken_frac=taken, felhunter_sac=fel_sac, voidwalker_sac=vw_sac)
    return ch


def mob_hp(L):
    return 18 * L + 0.62 * L * L


POLICIES = {
    'DoTs+DrainLife': dict(prio=['Corruption', 'BoA', 'SiphonLife', 'DrainLife']),
    'DoTs+Wrack+DL': dict(prio=['Corruption', 'BoA', 'SiphonLife', 'Wrack', 'DrainLife']),
    'DoTs+ShadowBolt': dict(prio=['Corruption', 'BoA', 'SiphonLife', 'ShadowBolt']),
    'DoTs+Wand': dict(prio=['Corruption', 'BoA', 'SiphonLife', 'Wand']),
    'Corr+SL+DrainLife': dict(prio=['Corruption', 'SiphonLife', 'DrainLife']),
    'Corr+SL+Wand': dict(prio=['Corruption', 'SiphonLife', 'Wand']),
    'Corr+SL+SB': dict(prio=['Corruption', 'SiphonLife', 'ShadowBolt']),
    'Corr+BoA+DrainLife': dict(prio=['Corruption', 'BoA', 'DrainLife']),
    'Corr+BoA+Wand': dict(prio=['Corruption', 'BoA', 'Wand']),
    'Corr+DrainLife': dict(prio=['Corruption', 'DrainLife']),
    'Corr+Wand': dict(prio=['Corruption', 'Wand']),
}


def evaluate(L, tal, pet='voidwalker', sp_per_level=1.0, policies=None, **kw):
    best = None
    for name, pol in (policies or POLICIES).items():
        pol = dict(pol, amp=False)
        s = seconds_per_kill(make_char(L, tal, sp_per_level, pet), mob_hp(L), pol, **kw)
        if best is None or s['spk'] < best[1]['spk']:
            best = (name, s)
    return best


if __name__ == '__main__':
    t0 = time.time()
    tal = dict(ImprovedCorruption=5, ImprovedDrains=3)
    print(evaluate(30, tal)[0], round(time.time() - t0, 2), 's for 7 policies')
