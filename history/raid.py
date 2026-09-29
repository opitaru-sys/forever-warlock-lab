"""Steady-state single-target raid DPS for level-60 WoW: Forever Warlock specs.

Expected-value, per-second budget model:
  DPS = sum(maintained DoT / cooldown spell DPS) + filler DPS * f
  f   = share of time left for the filler after DoT casts, cooldown casts and Life Taps.
Mana is balanced exactly with Life Tap (raid healers refill the health).
Hit assumed capped (same for every spec). No external raid buffs (same for every spec).

Spell numbers: Wowhead Forever spell pages (base + SP coefficients), Incinerate R3 and
Bane of Doom coefficient from two beta datamines (ForeverChanges, ElliotWood sim).
"""
import itertools

SP_DEF = 500
GCD = 1.5


def spells(sp):
    return {
        'Corruption': dict(dmg=438 + 1.2 * sp, dur=18, mana=340, cast=2.0, school='shadow', kind='dot', tree='aff'),
        'BoA': dict(dmg=552 + 1.6 * sp, dur=24, mana=215, cast=0, school='shadow', kind='dot', tree='aff'),
        'BoD': dict(dmg=1742 + 4.0 * sp, dur=60, mana=300, cast=0, school='shadow', kind='dot', tree='aff'),
        'SiphonLife': dict(dmg=420 + 0.5 * sp, dur=30, mana=365, cast=0, school='shadow', kind='dot', tree='aff'),
        'Immolate': dict(dmg=159 + 0.2 * sp, dot=280 + 0.65 * sp, dur=15, mana=380, cast=2.0, school='fire', kind='dot', tree='destro'),
        'ShadowBolt': dict(dmg=268 + 0.857 * sp, mana=380, cast=3.0, school='shadow', kind='nuke', tree='destro'),
        'Incinerate': dict(dmg=(217 + 0.714 * sp) * 1.25, mana=325, cast=2.5, school='fire', kind='nuke', tree='destro'),
        'Conflagrate': dict(dmg=282 + 0.429 * sp, mana=255, cast=0, cd=10, school='fire', kind='cd', tree='destro'),
        'Shadowburn': dict(dmg=266 + 0.429 * sp, mana=365, cast=0, cd=15, school='shadow', kind='cd', tree='destro'),
        'DrainLife': dict(dmg=260 + 0.5 * sp, mana=300, cast=5.0, school='shadow', kind='drain', tree='aff'),
        'Wrack': dict(dmg=222 + 0.857 * sp, mana=200, cast=6.0, school='shadow', kind='drain', tree='aff'),
    }


def spec_dps(spec, sp=SP_DEF, crit=0.10, lt_mana=840 * 1.2, pet_share=0.25, verbose=False):
    """spec: dict with keys
       dots: list of maintained DoTs, bane: 'BoA'|'BoD'|None, filler: spell name,
       cds: list of cooldown spells, mods: dict of talent effects, pet: None|'succubus'."""
    S = spells(sp + spec.get('bonus_sp', 0))
    m = spec['mods']
    shadow = m.get('shadow', 1.0)          # school-wide multipliers (sacrifice, Master Demonologist, S&F)
    fire = m.get('fire', 1.0)
    allm = m.get('all', 1.0)               # Soul Link etc.
    crit_sh = crit + m.get('malevolence', 0)
    crit_fire = crit

    def mult(name):
        s = S[name]
        x = allm * (shadow if s['school'] == 'shadow' else fire)
        if s['school'] == 'shadow':
            x *= m.get('shadow_mastery', 1.0)
        if s['kind'] in ('dot', 'drain'):
            x *= m.get('malediction', 1.0)
        if s['tree'] == 'destro':
            x *= m.get('agonizing_flames', 1.0)
        if name == 'Corruption':
            x *= m.get('imp_corr_dmg', 1.0)
        if name == 'BoA':
            x *= m.get('imp_boa', 1.0)
        if s['kind'] == 'drain':
            x *= m.get('drains', 1.0)
        if name == 'ShadowBolt':
            x *= m.get('isb', 1.0)
        # crit EV
        c = crit_sh if s['school'] == 'shadow' else crit_fire
        if s['tree'] == 'destro':
            cm = 2.0 if m.get('ruin') else 1.5
        elif s['kind'] in ('dot', 'drain'):
            cm = 2.0 if m.get('pandemic') else 1.5
        else:
            cm = 1.5
        return x * (1 + c * (cm - 1))

    ct = lambda name: max(GCD, S[name]['cast'] - m.get('bane_cast', {}).get(name, 0)) if S[name]['cast'] else GCD
    if m.get('instant_corr'):
        S['Corruption']['cast'] = 0

    lt_mana = lt_mana * m.get('ilt', 1.0)
    for k in S:
        if S[k]['tree'] == 'destro':
            S[k]['mana'] *= m.get('cataclysm', 1.0)
    dps = 0.0
    time_used = 0.0
    mana_rate = 0.0
    parts = {}
    dots = list(spec['dots']) + ([spec['bane']] if spec.get('bane') else [])
    dot_dps_total = 0.0
    for d in dots:
        s = S[d]
        if d == 'Immolate':
            dmg = s['dmg'] * mult(d) + s['dot'] * mult(d)
        else:
            dmg = s['dmg'] * mult(d)
        per = s['dur']
        parts[d] = dmg / per
        dot_dps_total += dmg / per if d != 'Immolate' else s['dot'] * mult(d) / per
        time_used += ct(d) / per
        mana_rate += s['mana'] / per
    # Wrack amplification: +10% to other shadow DoTs during its channel
    for c in spec.get('cds', []):
        s = S[c]
        dmg = s['dmg'] * mult(c)
        parts[c] = dmg / s['cd']
        time_used += GCD / s['cd']
        mana_rate += s['mana'] / s['cd']
    fil = spec['filler']
    s = S[fil]
    fil_ct = ct(fil)
    fil_dmg = s['dmg'] * mult(fil)
    fil_dps = fil_dmg / fil_ct
    if fil == 'Wrack':
        shadow_dots = sum(v for k, v in parts.items() if k in ('Corruption', 'BoA', 'BoD', 'SiphonLife'))
        fil_dps += 0.10 * shadow_dots
    fil_mana = s['mana'] / fil_ct
    # Life Tap: each tap = GCD seconds for lt_mana mana
    # f = (1 - time_used - GCD*mana_rate/lt) / (1 + GCD*fil_mana/lt)
    f = (1 - time_used - GCD * mana_rate / lt_mana) / (1 + GCD * fil_mana / lt_mana)
    parts[fil] = fil_dps * f
    # Nightfall (Affliction): 4% per Corruption tick / drain tick -> instant Shadow Bolt; saves the SB cast
    if m.get('nightfall'):
        procs = 0.04 * (1 / 3)   # Corruption ticks
        sb = S['ShadowBolt']['dmg'] * mult('ShadowBolt')
        parts['Nightfall'] = procs * sb * (1 - GCD / ct('ShadowBolt'))  # net gain vs spending the same time on filler
    total = sum(parts.values())
    if spec.get('pet') == 'succubus':
        parts['Succubus'] = pet_share * total * m.get('pet_mult', 1.0)
        total += parts['Succubus']
    if verbose:
        return total, {k: round(v) for k, v in parts.items()}, round(f, 3)
    return total


# ---------------------------------------------------------------- the specs
BANE5 = {'ShadowBolt': 0.5, 'Immolate': 0.5, 'Incinerate': 0.5}

SPECS = {
    # wowforeverbuilds Affliction 40/11/0: Imp sacrificed (no pet), deep Affliction
    'Affliction 40/11/0 (Imp sac, SB filler)': dict(
        dots=['Corruption', 'SiphonLife'], bane='BoA', filler='ShadowBolt', cds=[],
        mods=dict(shadow=1.15, malevolence=.05, shadow_mastery=1.05, malediction=1.05, imp_corr_dmg=1.10,
                  imp_boa=1.10, drains=1.20 * 1.36, pandemic=True, instant_corr=True, nightfall=True)),
    'Affliction 40/11/0 (Imp sac, Wrack filler)': dict(
        dots=['Corruption', 'SiphonLife'], bane='BoA', filler='Wrack', cds=[],
        mods=dict(shadow=1.15, malevolence=.05, shadow_mastery=1.05, malediction=1.05, imp_corr_dmg=1.10,
                  imp_boa=1.10, drains=1.20 * 1.36, pandemic=True, instant_corr=True, nightfall=True)),
    'Affliction 40/11/0 (Imp sac, Drain Life filler)': dict(
        dots=['Corruption', 'SiphonLife'], bane='BoA', filler='DrainLife', cds=[],
        mods=dict(shadow=1.15, malevolence=.05, shadow_mastery=1.05, malediction=1.05, imp_corr_dmg=1.10,
                  imp_boa=1.10, drains=1.20 * 1.36, pandemic=True, instant_corr=True, nightfall=True)),
    'Affliction 40/11/0 + Bane of Doom': dict(
        dots=['Corruption', 'SiphonLife'], bane='BoD', filler='ShadowBolt', cds=[],
        mods=dict(shadow=1.15, malevolence=.05, shadow_mastery=1.05, malediction=1.05, imp_corr_dmg=1.10,
                  imp_boa=1.10, drains=1.20 * 1.36, pandemic=True, instant_corr=True, nightfall=True)),
    # wowforeverbuilds Demonology 0/31/20: Imp sacrificed + Succubus out (Pact), MD +10% shadow, Soul Link +3%, DK +60 SP
    'Demonology 0/31/20 (Pact: Imp sac + Succubus)': dict(
        dots=['Corruption'], bane='BoA', filler='ShadowBolt', cds=[], pet='succubus', bonus_sp=60,
        mods=dict(shadow=1.15 * 1.10, all=1.03, ruin=True, isb=None, bane_cast=BANE5, pet_mult=1.03 * 1.02)),
    # wowforeverbuilds Destruction 9/11/31, shadow version (Imp sac, SB + Conflagrate for Shadow and Flame)
    'Destruction 9/11/31 (Imp sac, Shadow Bolt)': dict(
        dots=['Corruption', 'Immolate'], bane='BoA', filler='ShadowBolt', cds=['Conflagrate'],
        mods=dict(shadow=1.15 * 1.10, malediction=1.02, agonizing_flames=1.10, ruin=True, isb=None, bane_cast=BANE5)),
    # same talents, fire version: Succubus sac (+15% Fire), Incinerate filler, Shadowburn for the Fire half of S&F
    'Destruction 9/11/31 (Succubus sac, Incinerate)': dict(
        dots=['Corruption', 'Immolate'], bane='BoA', filler='Incinerate', cds=['Conflagrate', 'Shadowburn'],
        mods=dict(fire=1.15 * 1.10, shadow=1.10, malediction=1.02, agonizing_flames=1.10, ruin=True, bane_cast=BANE5)),
}


def isb_uptime(crit, casts_per_12s):
    return 1 - (1 - crit) ** casts_per_12s


def run(sp=500, crit=0.10, lt=840 * 1.2, pet_share=0.25):
    out = {}
    for name, spec in SPECS.items():
        spec = {**spec, 'mods': dict(spec['mods'])}
        if 'isb' in spec['mods']:
            # SB every ~2.5s while filling ~75% of the time -> ~3.6 SB per 12s window
            up = isb_uptime(crit, 3.6)
            spec['mods']['isb'] = 1 + 0.20 * up
        out[name] = spec_dps(spec, sp, crit, lt, pet_share, verbose=True)
    return out


if __name__ == '__main__':
    for name, (dps, parts, f) in run().items():
        print(f"{dps:6.0f}  {name}   filler-time {f}  {parts}")
