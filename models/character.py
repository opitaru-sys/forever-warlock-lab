import time
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
DESTRO = {'DestructiveReach': (0, 2), 'ImprovedShadowBolt': (0, 5), 'Bane': (0, 5),
          'MoltenSkin': (1, 5), 'Cataclysm': (1, 3), 'Aftermath': (1, 5),
          'Ruin': (2, 5), 'Shadowburn': (2, 1),
          'Intensity': (3, 3), 'AgonizingFlames': (3, 3), 'Conflagrate': (3, 1),
          'Pyroclasm': (4, 2), 'BaneOfHavoc': (4, 1), 'FireAndBrimstone': (4, 3),
          'ShadowAndFlame': (5, 5), 'Incinerate': (6, 1)}
PREREQ = {'Wrack': ('SiphonLife', 1), 'SoulLink': ('DemonicSacrifice', 1), 'DemonicPact': ('SoulLink', 1),
          'FelDomination': ('MasterSummoner', 2), 'Pyroclasm': ('Intensity', 3),
          'FireAndBrimstone': ('Conflagrate', 1), 'Incinerate': ('BaneOfHavoc', 1)}
TREES = [AFF, DEMO, DESTRO]
# Unscored, with the reason. Demonic Energies: heals the pet and feeds it Life Tap mana; the model has no pet
# health or mana. Improved Voidwalker: stronger Torment, Sacrifice and Consume Shadows; no pet health or threat.
# Fel Concentration: pushback protection; no pushback modelled. Demonic Aegis: stronger armor spells; mob damage
# is a flat rate, not armor-based. Improved Health Funnel: no pet health. Improved Felhunter: debuffs, dispels and
# Spell Lock; leveling mobs are not casters in the model.


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
def make_char(L, tal, sp_per_level=1.0, pet='voidwalker', lt_base_mult=1.0, lash_share=0.4):
    """lash_share: the share of Succubus damage that is Lash of Pain (Improved Sayaad), unknown, assumed 0.4."""
    hp = 20 + 28 * L + 0.4 * L * L
    mana = 20 + 25 * L + 0.45 * L * L
    hp *= 1 + 0.02 * tal.get('DemonicEmbrace', 0) * 0.65    # stamina is ~65% of HP
    mana *= 1 + 0.05 * tal.get('FelVitality', 0) * 0.7         # Fel Vitality: +5%/rank max mana
    pet_base = {'voidwalker': 0.5, 'succubus': 1.1, 'imp': 0.8, 'felhunter': 0.8, 'none': 0.0}[pet]
    pet_dps = pet_base * L * (1 + .02 * tal.get('UnholyPower', 0))
    if pet == 'imp':
        pet_dps *= 1 + .10 * tal.get('ImprovedImp', 0)             # Imp damage is almost all Firebolt
    if pet == 'succubus':
        pet_dps *= 1 + .10 * tal.get('ImprovedSayaad', 0) * lash_share
    shadow = fire = 1.0
    fel_sac = vw_sac = False
    pact = tal.get('DemonicPact', 0)
    sac = tal.get('_sac')          # which demon was sacrificed ('imp', 'felhunter', ...)
    if sac and (pact or pet == 'none'):
        if sac == 'imp':
            shadow *= 1.15
        if sac == 'succubus':
            fire *= 1.15
        if sac == 'felhunter':
            fel_sac = True
        if sac == 'voidwalker':
            vw_sac = True
    if pet == 'succubus':
        shadow *= 1 + .02 * tal.get('MasterDemonologist', 0)
    if pet == 'imp':
        fire *= 1 + .02 * tal.get('MasterDemonologist', 0)          # assumed 2% Fire a point, like the Succubus
    if tal.get('SoulLink') and pet != 'none':
        shadow *= 1.03
        fire *= 1.03
        pet_dps *= 1.03
    taken = {'voidwalker': 0.10, 'succubus': 1.0, 'imp': 1.0, 'felhunter': 1.0, 'none': 1.0}[pet]
    ch = Char(level=L, sp=sp_per_level * L, crit=0.05, spirit=15 + 1.2 * L, max_hp=hp, max_mana=mana,
              wand_dps=0.9 * L + 3, pet_dps=pet_dps, talents=tal, shadow_mult=shadow, fire_mult=fire,
              mob_dps=0.035 * L * L, taken_frac=taken * taken_scale(tal, pet), felhunter_sac=fel_sac,
              voidwalker_sac=vw_sac)
    return ch


def taken_scale(tal, pet):
    """Soul Link sends 30% of your damage taken to the demon; Molten Skin takes 2% a point off the rest."""
    s = 0.70 if tal.get('SoulLink') and pet != 'none' else 1.0
    return s * (1 - .02 * tal.get('MoltenSkin', 0))


def mob_hp(L):
    return 18 * L + 0.62 * L * L


# Mob HP multiples the analysis scripts average over: kill time snaps to DoT ticks, so one mob HP is noisy.
HP_GRID = tuple(round(0.8 + 0.05 * i, 2) for i in range(9))


def _p(*prio):
    return dict(prio=list(prio))


# Base rotations, simplest first: on a tie the first name wins, so a build without Siphon Life reports
# 'Corr+Wand' rather than 'Corr+SL+Wand'. 'Imm' policies keep Immolate up and cast Conflagrate on cooldown
# when it is talented. evaluate() adds the curse, finisher and Death Coil modifiers on the best few.
POLICIES = {
    'Corr+Wand': _p('Corruption', 'Wand'),
    'Corr+DrainLife': _p('Corruption', 'DrainLife'),
    'Corr+SB': _p('Corruption', 'ShadowBolt'),
    'Corr+SP': _p('Corruption', 'SearingPain'),
    'Corr+BoA+Wand': _p('Corruption', 'BoA', 'Wand'),
    'Corr+BoA+DrainLife': _p('Corruption', 'BoA', 'DrainLife'),
    'Corr+BoA+SB': _p('Corruption', 'BoA', 'ShadowBolt'),
    'Corr+BoA+SP': _p('Corruption', 'BoA', 'SearingPain'),
    'Corr+SL+Wand': _p('Corruption', 'SiphonLife', 'Wand'),
    'Corr+SL+DrainLife': _p('Corruption', 'SiphonLife', 'DrainLife'),
    'Corr+SL+SB': _p('Corruption', 'SiphonLife', 'ShadowBolt'),
    'Corr+SL+SP': _p('Corruption', 'SiphonLife', 'SearingPain'),
    'DoTs+Wand': _p('Corruption', 'BoA', 'SiphonLife', 'Wand'),
    'DoTs+DrainLife': _p('Corruption', 'BoA', 'SiphonLife', 'DrainLife'),
    'DoTs+ShadowBolt': _p('Corruption', 'BoA', 'SiphonLife', 'ShadowBolt'),
    'DoTs+SP': _p('Corruption', 'BoA', 'SiphonLife', 'SearingPain'),
    'DoTs+Wrack+DL': _p('Corruption', 'BoA', 'SiphonLife', 'Wrack', 'DrainLife'),
    'Imm+Wand': _p('Immolate', 'Conflagrate', 'Wand'),
    'Imm+DrainLife': _p('Immolate', 'Conflagrate', 'DrainLife'),
    'Imm+SB': _p('Immolate', 'Conflagrate', 'ShadowBolt'),
    'Imm+SP': _p('Immolate', 'Conflagrate', 'SearingPain'),
    'Imm+Incin': _p('Immolate', 'Conflagrate', 'Incinerate'),
    'Corr+Imm+Wand': _p('Corruption', 'Immolate', 'Conflagrate', 'Wand'),
    'Corr+Imm+DrainLife': _p('Corruption', 'Immolate', 'Conflagrate', 'DrainLife'),
    'Corr+Imm+SB': _p('Corruption', 'Immolate', 'Conflagrate', 'ShadowBolt'),
    'Corr+Imm+SP': _p('Corruption', 'Immolate', 'Conflagrate', 'SearingPain'),
    'Corr+Imm+Incin': _p('Corruption', 'Immolate', 'Conflagrate', 'Incinerate'),
    'Corr+BoA+Imm+Wand': _p('Corruption', 'BoA', 'Immolate', 'Conflagrate', 'Wand'),
    'Corr+BoA+Imm+DrainLife': _p('Corruption', 'BoA', 'Immolate', 'Conflagrate', 'DrainLife'),
    'Corr+BoA+Imm+SB': _p('Corruption', 'BoA', 'Immolate', 'Conflagrate', 'ShadowBolt'),
    'Corr+BoA+Imm+SP': _p('Corruption', 'BoA', 'Immolate', 'Conflagrate', 'SearingPain'),
    'Corr+BoA+Imm+Incin': _p('Corruption', 'BoA', 'Immolate', 'Conflagrate', 'Incinerate'),
    'DoTs+Imm+Wand': _p('Corruption', 'BoA', 'SiphonLife', 'Immolate', 'Conflagrate', 'Wand'),
    'DoTs+Imm+DrainLife': _p('Corruption', 'BoA', 'SiphonLife', 'Immolate', 'Conflagrate', 'DrainLife'),
    'DoTs+Imm+SB': _p('Corruption', 'BoA', 'SiphonLife', 'Immolate', 'Conflagrate', 'ShadowBolt'),
    'DoTs+Imm+SP': _p('Corruption', 'BoA', 'SiphonLife', 'Immolate', 'Conflagrate', 'SearingPain'),
    'DoTs+Imm+Incin': _p('Corruption', 'BoA', 'SiphonLife', 'Immolate', 'Conflagrate', 'Incinerate'),
    'DoTs+Imm+Wrack+DL': _p('Corruption', 'BoA', 'SiphonLife', 'Immolate', 'Conflagrate', 'Wrack', 'DrainLife'),
}


def mod_options(L, tal):
    """Modifier groups for the best base rotations. Every combination is tried: each group off or one option."""
    fins = [('fin', 'DrainSoul', ' +Drain Soul finish')]
    if tal.get('Shadowburn') and L >= 20:
        fins.append(('fin', 'Shadowburn', ' +Shadowburn finish'))
    if tal.get('Decimation') and L >= 48:
        fins.append(('fin', 'SoulFire', ' +Soul Fire finish'))
    groups = [[('coe', True, ' +Curse of the Elements')]] if L >= 20 else []
    groups.append(fins)
    if L >= 42:
        groups.append([('dc', True, ' +Death Coil')])
    return groups


def search_mods(L, tal, name, pol, s, run):
    """Every combination of the modifier groups on one base rotation (a greedy group-by-group pass can keep the
    curse and then miss Death Coil without it). A spell with a cooldown longer than a kill is ready on a share of
    pulls, kill cycle / cooldown, taking the base rotation's kill cycle: Amplify Curse (3 min), Death Coil (2 min),
    Soul Fire (60 sec less Decimation's 45% a point)."""
    ref = s['spk']
    base = dict(pol)
    if tal.get('AmplifyCurse') and 'BoA' in pol['prio']:
        base['p_amp'] = min(1.0, ref / 180.0)
    combos = [(base, name)]
    for group in mod_options(L, tal):
        combos = combos + [(dict(p, **{key: val}), n + label) for p, n in combos for key, val, label in group]
    best = None
    for p, n in combos:
        if p.get('dc'):
            p['p_dc'] = min(1.0, ref / 120.0)
        if p.get('fin') == 'SoulFire':
            p['p_sf'] = min(1.0, ref / (60 * (1 - .45 * tal.get('Decimation', 0))))
        r = s if p == pol else run(p)
        if best is None or r['spk'] < best[1]['spk']:
            best = (n, r)
    return best


def evaluate(L, tal, pet='voidwalker', sp_per_level=1.0, policies=None, aggro=False, harvest_drink=False,
             dd_mode='base', supp_all=True, lash_share=0.4, top=3, mods=True, hp_mults=(1.0,), **kw):
    """Best rotation for a build: (name, seconds_per_kill result). Every base policy the build can cast runs once
    (policies with the same usable steps run once, the first name wins); the best `top` then get the modifier
    search. aggro: the pet holds the mob like a Voidwalker (a Demonic Brand scenario, not the default).
    hp_mults: average each rotation over mobs of these HP multiples. Kill time snaps to DoT and drain ticks, so one
    mob HP can hide a talent's value; the analysis scripts average over 0.8 to 1.2."""
    def char():
        ch = make_char(L, tal, sp_per_level, pet, lash_share=lash_share)
        if aggro and pet not in ('voidwalker', 'none'):
            ch.taken_frac = 0.10 * taken_scale(tal, pet)
        ch.dd_mode, ch.supp_all = dd_mode, supp_all
        return ch

    def run(pol):
        rs = [seconds_per_kill(char(), mob_hp(L) * m, pol, harvest_drink=harvest_drink, **kw) for m in hp_mults]
        if len(rs) == 1:
            return rs[0]
        out = dict(rs[0])
        for key in ('spk', 'ttk', 'rest', 'healed'):
            out[key] = sum(r[key] for r in rs) / len(rs)
        return out
    ch, seen, base = char(), set(), []
    for name, pol in (policies or POLICIES).items():
        sig = leveling_sim.usable_steps(pol['prio'], ch)
        if sig in seen:
            continue
        seen.add(sig)
        base.append((name, pol, run(pol)))
    best = None
    for name, pol, s in base:
        if best is None or s['spk'] < best[1]['spk']:
            best = (name, s)
    if mods:
        for name, pol, s in sorted(base, key=lambda b: b[2]['spk'])[:top]:
            cand = search_mods(L, tal, name, pol, s, run)
            if cand[1]['spk'] < best[1]['spk']:
                best = cand
    return best


if __name__ == '__main__':
    t0 = time.time()
    tal = dict(ImprovedCorruption=5, ImprovedDrains=3)
    print(evaluate(30, tal)[0], round(time.time() - t0, 2), 's')
