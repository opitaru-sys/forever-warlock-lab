import itertools
from raid import spec_dps, isb_uptime, BANE5

AFF_MODS = dict(malevolence=.05, shadow_mastery=1.05, malediction=1.05, imp_corr_dmg=1.10, imp_boa=1.10,
                drains=1.20 * 1.36, pandemic=True, instant_corr=True, nightfall=True, ilt=1.0)

def specs():
    S = {}
    # ---- Affliction 40/11/0 (wowforeverbuilds)
    for bane in ('BoA', 'BoD'):
        for fil in ('ShadowBolt', 'Wrack', 'DrainLife'):
            S[f'Aff 40/11/0 | Imp sac | {bane} | {fil}'] = dict(dots=['Corruption', 'SiphonLife'], bane=bane, filler=fil,
                                                               mods=dict(AFF_MODS, shadow=1.15))
    S['Aff 40/11/0 | KEEP Succubus | BoD | Wrack'] = dict(dots=['Corruption', 'SiphonLife'], bane='BoD', filler='Wrack',
                                                           pet='succubus', mods=dict(AFF_MODS, shadow=1.0))
    # ---- Demonology 0/31/20 (wowforeverbuilds): Pact, Imp sac + Succubus, MD +10% shadow, Soul Link, DK +60 SP
    for bane in ('BoA', 'BoD'):
        S[f'Demo 0/31/20 | Pact Imp sac + Succubus | {bane} | SB'] = dict(
            dots=['Corruption'], bane=bane, filler='ShadowBolt', pet='succubus', bonus_sp=60,
            mods=dict(shadow=1.15 * 1.10, all=1.03, ruin=True, isb=True, bane_cast=BANE5, pet_mult=1.03 * 1.02 * 1.10, cataclysm=0.9))
    # ---- Demonology 20/31/0 alternative: Affliction 20 (IC5, Supp5, Mal5, Pand3, IBoA2) instead of Destruction 20
    S['Demo 20/31/0 | Pact Imp sac + Succubus | BoD | SB'] = dict(
        dots=['Corruption'], bane='BoD', filler='ShadowBolt', pet='succubus', bonus_sp=60,
        mods=dict(shadow=1.15 * 1.10, all=1.03, malediction=1.05, imp_corr_dmg=1.10, imp_boa=1.10, pandemic=True,
                  instant_corr=True, pet_mult=1.03 * 1.02 * 1.10))
    # ---- Destruction 9/11/31 (wowforeverbuilds): shadow and fire versions
    base_d = dict(malediction=1.02, agonizing_flames=1.10, ruin=True, bane_cast=BANE5, ilt=1.2, cataclysm=0.9)
    for bane in ('BoA', 'BoD'):
        S[f'Destro 9/11/31 | Imp sac | {bane} | SB+Conflag'] = dict(
            dots=['Corruption', 'Immolate'], bane=bane, filler='ShadowBolt', cds=['Conflagrate'],
            mods=dict(base_d, shadow=1.15 * 1.10, isb=True))
        S[f'Destro 9/11/31 | Succubus sac | {bane} | Incinerate+Conflag+Shadowburn'] = dict(
            dots=['Corruption', 'Immolate'], bane=bane, filler='Incinerate', cds=['Conflagrate', 'Shadowburn'],
            mods=dict(base_d, fire=1.15 * 1.10, shadow=1.10))
        S[f'Destro 9/11/31 | KEEP Succubus | {bane} | Incinerate+Conflag+Shadowburn'] = dict(
            dots=['Corruption', 'Immolate'], bane=bane, filler='Incinerate', cds=['Conflagrate', 'Shadowburn'], pet='succubus',
            mods=dict(base_d, fire=1.10, shadow=1.10))
    return S

def evaluate(sp, crit, lt, pet_share):
    out = {}
    for name, spec in specs().items():
        spec = {**spec, 'mods': dict(spec['mods']), 'cds': spec.get('cds', [])}
        if spec['mods'].get('isb'):
            spec['mods']['isb'] = 1 + 0.20 * isb_uptime(crit, 3.6)
        out[name] = spec_dps(spec, sp, crit, lt, pet_share, verbose=True)
    return out

if __name__ == '__main__':
    print("BASELINE sp500 crit10% LifeTap840 succubus=25% of lock dmg")
    res = evaluate(500, .10, 840, .25)
    for name, (d, parts, f) in sorted(res.items(), key=lambda x: -x[1][0]):
        print(f"{d:6.0f}  {name:60s} f={f}  {parts}")
    print("\nSENSITIVITY: rank of top 5 across grid")
    wins = {}
    for sp, crit, lt, ps in itertools.product((300, 500, 700), (.05, .10, .15), (530, 840), (0, .15, .25, .33)):
        res = evaluate(sp, crit, lt, ps)
        top = sorted(res.items(), key=lambda x: -x[1][0])
        key = top[0][0]
        wins.setdefault(key, []).append((sp, crit, lt, ps))
    for k, v in wins.items():
        print(f"{len(v):3d} grid points won by: {k}")
        print("     e.g.", v[:4])
    print("\nWith pet_share=0 (pets die / don't scale), best per spec family:")
    for sp in (300, 500, 700):
        res = evaluate(sp, .10, 840, 0)
        fams = {}
        for n, (d, p, f) in res.items():
            fam = n.split('|')[0].strip()
            if fam not in fams or d > fams[fam][0]:
                fams[fam] = (round(d), n)
        print(sp, fams)
