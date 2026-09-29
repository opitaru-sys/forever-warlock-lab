"""Independent recompute for the adversarial review. Does NOT import raid.py / raid2.py.

Steady-state budget: time = periodic GCD/cast time + Nightfall SB GCDs + Life Tap GCDs + filler time = 1.
Mana = periodic mana + Nightfall SB mana + filler mana = Life Tap mana.
Nightfall procs are modelled as extra instant Shadow Bolts that consume a GCD and 380 mana.
"""
import itertools

GCD = 1.5


def ev(c, bonus):
    return 1 + c * bonus


def solve(periodic, filler, lt, nf=None, amp_frac=0.0, shadow_dot_names=()):
    """periodic: dict name -> (dmg per application, period s, time cost s, mana).
    filler: (dmg per cast, cast s, mana, ticks per second for Nightfall or 0).
    nf: None or (proc chance per tick, corruption ticks per s, SB dmg, SB mana).
    Returns (dps, parts, f)."""
    A = sum(t / T for (_, T, t, _) in periodic.values())
    M = sum(m / T for (_, T, _, m) in periodic.values())
    d_f, c_f, m_f, tps = filler
    r0 = r1 = 0.0
    sbd = sbm = 0.0
    if nf:
        p, corr_tps, sbd, sbm = nf
        r0 = p * corr_tps
        r1 = p * tps
    k = GCD / lt
    num = 1 - A - GCD * r0 - k * (M + sbm * r0)
    den = 1 + GCD * r1 + k * (sbm * r1 + m_f / c_f)
    f = num / den
    parts = {n: D / T for n, (D, T, _, _) in periodic.items()}
    shadow_dots = sum(v for n, v in parts.items() if n in shadow_dot_names)
    parts['filler'] = f * (d_f / c_f + amp_frac * shadow_dots)
    if nf:
        parts['Nightfall SB'] = (r0 + r1 * f) * sbd
    return sum(parts.values()), parts, f


# ------------------------------------------------------------------ Affliction 40/11/0
def aff(sp, c, lt=840, bane='BoD', fil='Wrack', sac_imp=True, immolate=False, nf_mode='fixed',
        drains=1.20 * 1.36):
    cs = c + 0.05
    sh = (1.15 if sac_imp else 1.0) * 1.05          # Imp sac, Shadow Mastery
    mal = 1.05
    dc = ev(cs, 1.0)                                  # Pandemic
    P = {}
    P['Corruption'] = ((438 + 1.2 * sp) * sh * mal * 1.10 * dc, 18, GCD, 340)
    if bane == 'BoA':
        P['BoA'] = ((552 + 1.596 * sp) * sh * mal * 1.10 * dc, 24, GCD, 215)
    else:
        P['BoD'] = ((1742 + 4.0 * sp) * sh * mal * dc, 60, GCD, 300)
    P['SiphonLife'] = ((420 + 0.5 * sp) * sh * mal * dc, 30, GCD, 365)
    if immolate:
        imm = (159 + 0.2 * sp) * ev(c, 0.5) + (280 + 0.65 * sp) * mal * ev(c, 0.5)
        P['Immolate'] = (imm, 15, 2.0, 380)
    sb = (268 + 0.857 * sp) * sh * ev(cs, 0.5)
    if fil == 'Wrack':
        F = ((222 + 0.858 * sp) * sh * mal * drains * dc, 6.0, 200, 1.0)
    elif fil == 'DrainLife':
        F = ((260 + 0.5 * sp) * sh * mal * drains * dc, 5.0, 300, 1.0)
    else:
        F = (sb, 3.0, 380, 0.0)
    if nf_mode == 'orig':          # Corruption-only proc source, as in raid.py
        F = (F[0], F[1], F[2], 0.0)
    nf = (0.04, 1 / 3, sb, 380)
    amp = 0.10 if fil == 'Wrack' else 0.0
    return solve(P, F, lt, nf, amp, ('Corruption', 'BoA', 'BoD', 'SiphonLife'))


# ------------------------------------------------------------------ Destruction 9/11/31
def destro(sp, c, lt=840 * 1.2, bane='BoD', version='incin', shadowburn=None, isb_mode='fixed',
           isb_dur=12.0, aftermath=False):
    """version 'sb' = Imp sac + Shadow Bolt; 'incin' = Succubus sac + Incinerate; 'keep' = Succubus out, no sac."""
    if shadowburn is None:
        shadowburn = version != 'sb'
    sac_shadow = 1.15 if version == 'sb' else 1.0
    sac_fire = 1.15 if version == 'incin' else 1.0
    sh = sac_shadow * 1.10                           # S&F from Conflagrate
    fi = sac_fire * (1.10 if shadowburn else 1.0)    # S&F from Shadowburn
    AF = 1.10
    mal = 1.02
    cat = 0.9
    dstr = ev(c, 1.0)       # Ruin on Destruction spells
    dotc = ev(c, 0.5)       # Corruption / Bane, no Pandemic

    def build(isb):
        P = {}
        P['Corruption'] = ((438 + 1.2 * sp) * sh * mal * dotc * isb, 18, 2.0, 340)
        if bane == 'BoA':
            P['BoA'] = ((552 + 1.596 * sp) * sh * mal * dotc * isb, 24, GCD, 215)
        else:
            P['BoD'] = ((1742 + 4.0 * sp) * sh * mal * dotc * isb, 60, GCD, 300)
        direct = (159 + 0.2 * sp) * (1.5 if aftermath else 1.0)
        imm = (direct + (280 + 0.65 * sp) * mal) * fi * AF * dstr
        P['Immolate'] = (imm, 15, 1.5, 380 * cat)
        P['Conflagrate'] = ((282 + 0.429 * sp) * fi * AF * dstr, 10, GCD, 255 * cat)
        if shadowburn:
            P['Shadowburn'] = ((266 + 0.429 * sp) * sh * AF * dstr * isb, 15, GCD, 365 * cat)
        if version == 'sb':
            F = ((268 + 0.857 * sp) * sh * AF * dstr * isb, 2.5, 380 * cat, 0.0)
        else:
            F = ((217 + 0.714 * sp) * 1.25 * fi * AF * dstr, 2.0, 325 * cat, 0.0)
        return P, F

    P, F = build(1.0)
    dps, parts, f = solve(P, F, lt)
    if version == 'sb':
        if isb_mode == 'orig':
            # raid.py: ISB only on Shadow Bolt, n = 3.6 SB per 12 s regardless of f
            u = 1 - (1 - c) ** 3.6
            P2, F2 = build(1.0)
            F2 = (F2[0] * (1 + 0.2 * u),) + F2[1:]
            return solve(P2, F2, lt)
        n = isb_dur * f / 2.5
        u = 1 - (1 - c) ** n
        P2, F2 = build(1 + 0.2 * u)
        return solve(P2, F2, lt)
    return dps, parts, f


# ------------------------------------------------------------------ Demonology 0/31/20 (Pact)
def demo(sp, c, lt=840, bane='BoD', immolate=False, isb_mode='fixed', hit_penalty=0.0):
    sp2 = sp + 60                       # Demonic Knowledge
    sh = 1.15 * 1.10                    # Imp sac + Master Demonologist (Succubus)
    allm = 1.03 * (1 - hit_penalty)     # Soul Link; optional missing-Suppression hit gap
    dstr = ev(c, 1.0)
    dotc = ev(c, 0.5)
    cat = 0.9

    def build(isb):
        P = {}
        P['Corruption'] = ((438 + 1.2 * sp2) * sh * allm * dotc * isb, 18, 2.0, 340)
        if bane == 'BoA':
            P['BoA'] = ((552 + 1.596 * sp2) * sh * allm * dotc * isb, 24, GCD, 215)
        else:
            P['BoD'] = ((1742 + 4.0 * sp2) * sh * allm * dotc * isb, 60, GCD, 300)
        if immolate:
            imm = ((159 + 0.2 * sp2) + (280 + 0.65 * sp2)) * allm * dstr
            P['Immolate'] = (imm, 15, 1.5, 380 * cat)
        F = ((268 + 0.857 * sp2) * sh * allm * dstr * isb, 2.5, 380 * cat, 0.0)
        return P, F

    P, F = build(1.0)
    _, _, f = solve(P, F, lt)
    if isb_mode == 'orig':
        u = 1 - (1 - c) ** 3.6
        P2, F2 = build(1.0)
        F2 = (F2[0] * (1 + 0.2 * u),) + F2[1:]
        return solve(P2, F2, lt)
    u = 1 - (1 - c) ** (12 * f / 2.5)
    return solve(*build(1 + 0.2 * u), lt)


# ------------------------------------------------------------------ discrete-event check of the budget algebra
def des_check(sp=500, c=0.10, horizon=20000.0):
    """Rotation sim for Destro Succubus-sac Incinerate BoA: refresh DoTs on expiry, CDs on ready,
    Life Tap when mana short, else Incinerate. Mana starts at 0 (steady state)."""
    P, F = None, None
    dps_a, parts_a, f_a = destro(sp, c, bane='BoA', version='incin')
    # rebuild the same numbers the analytic model used
    sh, fi, AF, mal, cat = 1.10, 1.15 * 1.10, 1.10, 1.02, 0.9
    dstr, dotc = ev(c, 1.0), ev(c, 0.5)
    acts = {
        'Immolate': ((159 + 0.2 * sp + (280 + 0.65 * sp) * mal) * fi * AF * dstr, 15, 1.5, 380 * cat),
        'Corruption': ((438 + 1.2 * sp) * sh * mal * dotc, 18, 2.0, 340),
        'BoA': ((552 + 1.596 * sp) * sh * mal * dotc, 24, 1.5, 215),
        'Conflagrate': ((282 + 0.429 * sp) * fi * AF * dstr, 10, 1.5, 255 * cat),
        'Shadowburn': ((266 + 0.429 * sp) * sh * AF * dstr, 15, 1.5, 365 * cat),
    }
    inc = ((217 + 0.714 * sp) * 1.25 * fi * AF * dstr, 2.0, 325 * cat)
    lt = 840 * 1.2
    t, mana, dmg = 0.0, 0.0, 0.0
    ready = {k: 0.0 for k in acts}
    filler_time = 0.0
    while t < horizon:
        did = False
        for k, (D, T, tc, m) in acts.items():
            if t >= ready[k] - 1e-9:
                if mana < m:
                    mana += lt; t += GCD; did = True; break
                mana -= m; t += tc; ready[k] = t + T - tc if k in ('Immolate', 'Corruption') else t - tc + T
                # DoT damage is credited in full (steady state, no clipping)
                dmg += D; did = True; break
        if did:
            continue
        if mana < inc[2]:
            mana += lt; t += GCD; continue
        mana -= inc[2]; t += inc[1]; dmg += inc[0]; filler_time += inc[1]
    return dmg / t, filler_time / t, dps_a, f_a


if __name__ == '__main__':
    SP, C = 500, 0.10
    print('=== budget-algebra check: discrete-event sim vs analytic (Destro incin BoA, SP500, 10% crit)')
    d_sim, f_sim, d_an, f_an = des_check()
    print(f'  sim {d_sim:.1f} dps (f={f_sim:.3f})   analytic {d_an:.1f} dps (f={f_an:.3f})')

    print('\n=== Claim 1: BoD vs BoA, steady state, per spec, SP 300..1200')
    for sp in (300, 500, 700, 1000, 1200):
        a = aff(sp, C, bane='BoD')[0] - aff(sp, C, bane='BoA')[0]
        a_sb = aff(sp, C, bane='BoD', fil='ShadowBolt')[0] - aff(sp, C, bane='BoA', fil='ShadowBolt')[0]
        d = destro(sp, C, bane='BoD')[0] - destro(sp, C, bane='BoA')[0]
        m = demo(sp, C, bane='BoD')[0] - demo(sp, C, bane='BoA')[0]
        # raw dmg/s of the Bane itself in Affliction (IBoA only on BoA)
        cs = C + .05
        boa_raw = (552 + 1.596 * sp) / 24 * 1.10
        bod_raw = (1742 + 4.0 * sp) / 60
        print(f'  SP{sp}: BoD-BoA  Aff(Wrack) {a:+.1f}  Aff(SB) {a_sb:+.1f}  Destro {d:+.1f}  Demo(lock only) {m:+.1f}'
              f'   | Aff bane raw/s BoA*1.1 {boa_raw:.1f} vs BoD {bod_raw:.1f}')
    print('  SP where IBoA makes BoA out-damage BoD per second (Affliction):',
          round((1742 / 60 - 1.1 * 552 / 24) / (1.1 * 1.596 / 24 - 4.0 / 60), 0))

    print('\n  finite fight, SP500 Affliction multipliers, bane damage only (no GCD value):')
    for T in (45, 60, 75, 90, 105, 119, 120, 150, 180, 240, 300):
        sh, mal, dc = 1.15 * 1.05, 1.05, ev(C + .05, 1.0)
        boa_s = (552 + 1.596 * SP) * sh * mal * 1.10 * dc / 24
        bod_hit = (1742 + 4.0 * SP) * sh * mal * dc
        pure_boa = boa_s * T
        pure_bod = (T // 60) * bod_hit
        hybrid = (T // 60) * bod_hit + (T - 60 * (T // 60)) * boa_s
        print(f'   T={T:3d}s  pure BoA {pure_boa:6.0f}  pure BoD {pure_bod:6.0f}  BoD-then-BoA {hybrid:6.0f}')

    print('\n=== Claim 2: Destruction 9/11/31, SP500 crit10%, LT 840*1.2')
    rows = [
        ('SB, Imp sac, ISB as in raid.py (SB only, n=3.6)', destro(SP, C, version='sb', isb_mode='orig')),
        ('SB, Imp sac, ISB on all Shadow dmg, n from f', destro(SP, C, version='sb')),
        ('SB, Imp sac, ISB fixed + Shadowburn on CD', destro(SP, C, version='sb', shadowburn=True)),
        ('SB, Imp sac, ISB 60s duration + Shadowburn', destro(SP, C, version='sb', shadowburn=True, isb_dur=60)),
        ('Incinerate, Succubus sac (as in raid2)', destro(SP, C, version='incin')),
        ('Incinerate, Succubus sac, ISB pts -> Aftermath 5/5', destro(SP, C, version='incin', aftermath=True)),
    ]
    for n, (d, p, f) in rows:
        print(f'  {d:6.1f}  f={f:.3f}  {n}')
    base_inc = rows[4][1][0]
    for i in range(4):
        print(f'  Incinerate advantage vs row {i}: {100 * (base_inc / rows[i][1][0] - 1):+.1f}%')
    print('  grid (BoD) incin vs SB+Shadowburn+fixed ISB:')
    for sp, c in itertools.product((300, 500, 700, 1000), (.05, .10, .15, .20)):
        a = destro(sp, c, version='incin')[0]
        b = destro(sp, c, version='sb', shadowburn=True)[0]
        print(f'   SP{sp} crit{int(c * 100):2d}%: incin {a:6.1f}  SB {b:6.1f}  {100 * (a / b - 1):+5.1f}%')

    print('\n=== Claim 3: Affliction filler (BoD), SP x crit x LT')
    for lt, sp, c in itertools.product((530, 840, 1e9), (300, 500, 700, 1000), (.05, .10, .20)):
        r = {fil: aff(sp, c, lt=lt, fil=fil)[0] for fil in ('Wrack', 'ShadowBolt', 'DrainLife')}
        order = ' > '.join(sorted(r, key=lambda k: -r[k]))
        lt_s = 'inf' if lt > 1e8 else lt
        print(f'   LT{lt_s} SP{sp} c{int(c * 100)}: ' + '  '.join(f'{k} {v:.0f}' for k, v in r.items()) + f'   [{order}]')
    print('  Nightfall proc-source fix, SP500 c10 LT840:')
    for fil in ('Wrack', 'ShadowBolt', 'DrainLife'):
        o = aff(SP, C, fil=fil, nf_mode='orig')[0]
        n = aff(SP, C, fil=fil)[0]
        print(f'   {fil:10s} Corruption-only NF {o:.1f}  -> with channel-tick NF {n:.1f}')
    print('  additive Improved Drains + Soul Siphon (1.56 instead of 1.632), SP500 c10 LT840:')
    for fil in ('Wrack', 'ShadowBolt', 'DrainLife'):
        print(f'   {fil:10s} {aff(SP, C, fil=fil, drains=1.56)[0]:.1f}')
    print('  + Immolate maintained in Affliction:')
    for fil in ('Wrack', 'ShadowBolt'):
        print(f'   {fil:10s} without {aff(SP, C, fil=fil)[0]:.1f}  with Immolate {aff(SP, C, fil=fil, immolate=True)[0]:.1f}')

    print('\n=== Claims 4/5: pet as ABSOLUTE dps P0 (same Succubus in every spec), Demo pet mult 1.156')
    DEMO_PM = 1.03 * 1.02 * 1.10
    for sp in (300, 500, 700):
        aff_sac = aff(sp, C)[0]
        aff_keep = aff(sp, C, sac_imp=False)[0]
        inc = destro(sp, C, version='incin')[0]
        keep = destro(sp, C, version='keep')[0]
        sbv = destro(sp, C, version='sb', shadowburn=True)[0]
        dm = demo(sp, C)[0]
        dm_imm = demo(sp, C, immolate=True)[0]
        dm_hit = demo(sp, C, hit_penalty=0.05)[0]
        print(f'  SP{sp}: Aff sac {aff_sac:.0f} | Aff keep(lock) {aff_keep:.0f} | Destro incin {inc:.0f} | Destro keep(lock) {keep:.0f}'
              f' | Destro SB+SBurn {sbv:.0f} | Demo(lock) {dm:.0f} (+Immolate {dm_imm:.0f}, -5% hit {dm_hit:.0f})')
        be_aff = aff_sac - aff_keep
        print(f'     Claim 4 Aff breakeven P0 = {be_aff:.0f} dps = {100 * be_aff / aff_sac:.1f}% of total, '
              f'{100 * be_aff / aff_keep:.1f}% of lock dmg')
        be_des = inc - keep
        print(f'     Claim 4 Destro keep-vs-Succ-sac breakeven P0 = {be_des:.0f} = {100 * be_des / inc:.1f}% of total')
        for label, dlock in (('Demo as modelled', dm), ('Demo +Immolate', dm_imm), ('Demo, 5% hit gap', dm_hit)):
            be = (max(inc, keep) - dlock) / DEMO_PM  # vs best Destro without pet first
            # Demo also has to beat Destro keep: dlock + pm*P > keep + P
            if DEMO_PM * 1 > 1:
                be2 = (keep - dlock) / (DEMO_PM - 1)
            p_needed = max(0.0, (inc - dlock) / DEMO_PM)
            beats_keep = 'always' if dlock >= keep else f'P0>{be2:.0f}'
            share = 100 * DEMO_PM * p_needed / (dlock + DEMO_PM * p_needed)
            print(f'     Claim 5 {label}: beats Destro Succ-sac once P0 >= {p_needed:.0f} '
                  f'(= {share:.1f}% of Demo total); vs Destro keep: {beats_keep}')
        print(f'     Claim 5 Aff last? Aff sac {aff_sac:.0f} + Immolate {aff(sp, C, immolate=True)[0]:.0f} vs worst other {min(inc, dm):.0f}')
