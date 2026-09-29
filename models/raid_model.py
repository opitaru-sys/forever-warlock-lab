"""Forever Warlock raid model: level 60, steady state, expected values.

Started as the independent recompute for the adversarial review (docs/review.md). It is now the reference
that model.js ports: tests/parity_test.js and tests/raid_options_fixtures.json hold values generated here
(tests/make_raid_fixtures.py).

Steady-state budget: time = periodic GCD/cast time + Nightfall SB GCDs + Life Tap GCDs + filler time = 1.
Mana = periodic mana + Nightfall SB mana + filler mana = Life Tap mana + regen (mp5 / 5).
Nightfall procs are modelled as extra instant Shadow Bolts that consume a GCD and 380 mana.

Options, all off by default so the reviewed numbers are unchanged:
  fire_immune  for bosses immune to Fire: Fire spells are dropped, and the two Fire Destruction specs
               (destro 'incin' and 'keep') return (0, {}, 0) because they are not viable.
  coe          Curse of the Elements on the main target: +10% magic damage taken.
  mp5          mana per 5 seconds from gear and buffs; it cuts Life Tap time.
  consumables  a Major Mana Potion and a Demonic or Dark Rune on cooldown from the pull, spread over the
               fight as extra mana per second (30, the same as 150 mp5); stacks with mp5.
  targets      1 or 2. On 2 targets each spec takes its best second-target plan: a spread of its DoTs and
               a Bane, or (Destruction) Bane of Havoc. Parts on the second target end in ' (2nd)'.
  execute      share of the fight with the boss under 35% health (True = 0.35). Only the Decimation
               specs (demo, demo_deep) change.
  shadowburn   destro(): False never casts Shadowburn (each cast costs a Soul Shard); that also drops
               Shadow and Flame's +10% Fire. spec_lock()/rank() default True.
  brand_attacks, brand_scaling   demo_deep(): branded pet attacks per Demonic Brand (0 = no damage,
               3 = Wowhead tooltip, 6 = client rank text) and whether the brand scales with the
               warlock's spell power ('lock') or the demon's (Demonic Knowledge, 'pet').
"""
import itertools

GCD = 1.5

# ---------------------------------------------------------------- spell data
# Beta client 1.60.1.69893, SpellEffect table, max rank: (base damage, spell power coefficient), summed over
# every tick for periodic spells. Tick counts from the Wowhead Forever tooltip durations.
CORRUPTION = (438, 1.2)        # 25311: 73 per 3 s tick x 6, 0.2 per tick
AGONY = (552, 1.596)           # 11713: 46 per 2 s tick x 12 (ramp average), 0.133 per tick
DOOM = (1742, 4.0)             # 603: one hit after 60 s
SIPHON_LIFE = (410, 0.5)       # 18881: 41 per 3 s tick x 10, 0.05 per tick
IMMOLATE_HIT = (158, 0.2)      # 25309 effect 1
IMMOLATE_DOT = (275, 0.65)     # 25309 effect 0: 55 per 3 s tick x 5, 0.13 per tick
SHADOW_BOLT = (268, 0.857)     # 25307
WRACK = (216, 0.858)           # 1316697: 36 per 1 s tick x 6, 0.143 per tick
DRAIN_LIFE = (255, 0.5)        # 11700: 51 per 1 s tick x 5, 0.1 per tick
CONFLAGRATE = (282, 0.429)     # 18932
SHADOWBURN = (266, 0.429)      # 18871
INCINERATE = (217, 0.714)      # 1293813, +25% on a target with Immolate
SOUL_FIRE = (431, 1.0)         # 17924
SEARING_PAIN = (114, 0.429)    # 17923
DEATH_COIL = (454, 0.214)      # 17926
BRAND_HIT = (66.5, 0.078)      # Demonic Brand, per branded pet attack at level 60 (Wowhead tooltip formula)

# ---------------------------------------------------------------- option constants
EXEC_SHARE = 0.35              # the boss is under 35% health for the last 35% of the fight (linear health)
COE = 1.10                     # Curse of the Elements rank 4: +10% magic damage taken
LASH_SHARE = 0.10              # Lash of Pain share of an untalented Succubus: 43 + 0.429 x pet spell power per 12 s
                               # (11779) is 3.6 to 5.7 dps, 7 to 11% of 50 dps. Shadow; the rest is Physical melee
HAVOC_COPY = 0.15              # Bane of Havoc copies 15% of your damage to other targets onto its target
HAVOC = (0.0, 300.0, GCD, 65)  # 5 min Bane, one GCD, 5% of base mana (base mana about 1,300, assumed)
DECIMATION = 1.06              # Decimation 2/2: Shadow Bolt and Searing Pain +6% on a target under 35%
SOUL_FIRE_EXEC = (2.4, 6.0)    # Soul Fire under Decimation: cast (6 s - 2 s Bane) x 0.6, cooldown 60 s x 0.1
BRAND_ATTACKS = 6              # Demonic Brand 3/3: branded pet attacks per Searing Pain (client rank text)
BRAND_S = 10.0                 # brand duration
SUCC_RATE = 0.5 + 1 / 12       # Succubus attacks per second: melee every 2.0 s (assumed) and Lash of Pain
SUCC_FULL = 50.0               # Succubus dps that means she is on the boss all fight (the page's placeholder); below
                               # it her attack rate, and so her brand damage, scales down (assumption)
PET_HIT = 0.86                 # pet attacks that land on a raid boss: about 14% miss or dodge (assumed, Classic pets);
                               # a missed attack still uses a brand charge
IMP_RATE = 0.5                 # Imp Firebolt, 2 s cast
PET_SP = 60                    # demon spell power: Demonic Knowledge 3/3 gives it 100% of your level
IMP_BASE = (47 + 0.571 * PET_SP) / 2   # Imp dps before talents: Firebolt 11763 (45 to 50, 0.571), 2 s cast
FIGHT_S = 300.0                # fight length: the one-off pet swap in deep Demonology, and consumables
POTION_MANA = (1350 + 2250) / 2   # Major Mana Potion (13444), 2 min cooldown
RUNE_MANA = (900 + 1500) / 2      # Demonic Rune / Dark Rune (12662 / 20520), own 2 min cooldown; the 600 to
                                  # 1000 life is treated like Life Tap's health: healed by the raid, no cost
CONSUMABLE_REGEN = (FIGHT_S // 120 + 1) * (POTION_MANA + RUNE_MANA) / FIGHT_S   # 3 of each: 30 mana per s
SWAP = (3.0, 570)              # Fel Domination summon + Soul Link recast: two GCDs, 24% + 20% of base mana
# Succubus talents as (Soul Link x Unholy Power, Master Demonologist, Improved Sayaad). Master Demonologist is
# +10% Shadow and Improved Sayaad +30% Lash of Pain, so both reach only her Lash of Pain share.
SUCC_PLAIN = (1.0, 1.0, 1.0)                # Destruction 9/11/31 and Affliction 40/11/0: no demon talents
SUCC_PACT = (1.03 * 1.02, 1.10, 1.30)       # Pact 0/31/20: Unholy Power 1/5, Improved Sayaad 3/3
SUCC_DEEP = (1.03 * 1.10, 1.10, 1.30)       # deep 0/35/16: Unholy Power 5/5, Improved Sayaad 3/3
DEEP_IMP_PET = 1.03 * 1.10 * 1.10 * 1.30    # Soul Link, Unholy Power 5/5, Master Demonologist (Imp), Improved Imp
BRAND_PET = 1.03 * 1.10 * 1.10              # brand damage: Soul Link, Unholy Power, Master Demonologist (its school)
SECOND = ' (2nd)'


def _regen(mp5, consumables):
    """Mana per second from outside Life Tap: mp5 plus potion and rune on cooldown. Items are off the GCD."""
    return mp5 / 5 + (CONSUMABLE_REGEN if consumables else 0.0)


def ev(c, bonus):
    return 1 + c * bonus


def dmg(spell, sp):
    return spell[0] + spell[1] * sp


def exec_share(execute):
    if execute is True:
        return EXEC_SHARE
    return min(1.0, max(0.0, float(execute or 0.0)))


def solve(periodic, filler, lt, nf=None, amp_frac=0.0, shadow_dot_names=(), regen=0.0):
    """periodic: dict name -> (dmg per application, period s, time cost s, mana).
    filler: (dmg per cast, cast s, mana, ticks per second for Nightfall or 0).
    nf: None or (proc chance per tick, corruption ticks per s, SB dmg, SB mana).
    regen: mana per second from outside Life Tap.
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
    num = 1 - A - GCD * r0 - k * (M + sbm * r0 - regen)
    den = 1 + GCD * r1 + k * (sbm * r1 + m_f / c_f)
    f = num / den
    taps = (M + sbm * (r0 + r1 * f) + f * m_f / c_f - regen) / lt
    if taps < 0:        # regen pays for everything: no Life Tap, the spare mana is wasted
        f = (1 - A - GCD * r0) / (1 + GCD * r1)
    parts = {n: D / T for n, (D, T, _, _) in periodic.items()}
    shadow_dots = sum(v for n, v in parts.items() if n in shadow_dot_names)
    parts['filler'] = f * (d_f / c_f + amp_frac * shadow_dots)
    if nf:
        parts['Nightfall SB'] = (r0 + r1 * f) * sbd
    return sum(parts.values()), parts, f


def _finish(res, coe=False, copy=0.0):
    """Curse of the Elements on the main target, then the Bane of Havoc copy of main-target damage."""
    if not coe and not copy:
        return res
    dps, parts, f = res
    parts = {n: v * COE if coe and not n.endswith(SECOND) else v for n, v in parts.items()}
    if copy:
        parts['Havoc copy'] = copy * sum(v for n, v in parts.items() if not n.endswith(SECOND))
    return sum(parts.values()), parts, f


def _blend(r1, r2, x):
    """Time-weighted mix of two phases: r1 for (1 - x) of the fight, r2 for x."""
    if x <= 0:
        return r1
    (d1, p1, f1), (d2, p2, f2) = r1, r2
    names = list(p1) + [n for n in p2 if n not in p1]
    parts = {n: (1 - x) * p1.get(n, 0.0) + x * p2.get(n, 0.0) for n in names}
    return (1 - x) * d1 + x * d2, parts, (1 - x) * f1 + x * f2


def _plans(targets, optional, banes):
    """Second-target plans to try: every subset of the optional DoTs with each Bane choice (None = no Bane).
    One target: a single empty plan."""
    if targets != 2:
        return [()]
    out = []
    for bane in banes:
        for mask in range(2 ** len(optional)):
            plan = tuple(n for i, n in enumerate(optional) if mask >> i & 1)
            out.append(plan + ((bane,) if bane else ()))
    return out


def succ_mult(talents, coe=False):
    """Multiplier on the Succubus slider: melee takes Soul Link and Unholy Power; Lash of Pain also takes Master
    Demonologist, Improved Sayaad and Curse of the Elements (it is Shadow, her melee is Physical)."""
    all_dmg, md, sayaad = talents
    return all_dmg * ((1 - LASH_SHARE) + LASH_SHARE * md * sayaad * (COE if coe else 1.0))


def _best(results):
    """Highest damage among feasible rotations: None marks an infeasible option, and a negative filler share
    means the rotation needs more than 100% of the time. Falls back to the best of all only if none fits."""
    results = [r for r in results if r is not None]
    pool = [r for r in results if r[2] >= 0] or results
    best = None
    for r in pool:
        if best is None or r[0] > best[0]:
            best = r
    return best


# ------------------------------------------------------------------ Affliction 40/11/0
def aff(sp, c, lt=840, bane='BoD', fil='Wrack', sac_imp=True, immolate=False, nf_mode='fixed',
        drains=1.20 * 1.36, fire_immune=False, coe=False, mp5=0.0, targets=1, extra=(), consumables=False):
    """extra: 'SoulFire' and/or 'DeathCoil' cast on cooldown (analysis only). fil 'SearingPain' is analysis only."""
    cs = c + 0.05
    sh = (1.15 if sac_imp else 1.0) * 1.05          # Imp sac, Shadow Mastery
    mal = 1.05
    dc = ev(cs, 1.0)                                  # Pandemic
    imm = immolate and not fire_immune

    def dot(n):
        if n == 'Corruption':
            return (dmg(CORRUPTION, sp) * sh * mal * 1.10 * dc, 18, GCD, 340)
        if n == 'BoA':
            return (dmg(AGONY, sp) * sh * mal * 1.10 * dc, 24, GCD, 215)
        if n == 'BoD':
            return (dmg(DOOM, sp) * sh * mal * dc, 60, GCD, 300)
        if n == 'SiphonLife':
            return (dmg(SIPHON_LIFE, sp) * sh * mal * dc, 30, GCD, 365)
        return (dmg(IMMOLATE_HIT, sp) * ev(c, 0.5) + dmg(IMMOLATE_DOT, sp) * mal * ev(c, 0.5), 15, 2.0, 380)

    sb = dmg(SHADOW_BOLT, sp) * sh * ev(cs, 0.5)
    if fil == 'Wrack':
        F = (dmg(WRACK, sp) * sh * mal * drains * dc, 6.0, 200, 1.0)
    elif fil == 'DrainLife':
        F = (dmg(DRAIN_LIFE, sp) * sh * mal * drains * dc, 5.0, 300, 1.0)
    elif fil == 'SearingPain':
        F = (0.0 if fire_immune else dmg(SEARING_PAIN, sp) * ev(c, 0.5), 1.5, 168, 0.0)
    else:
        F = (sb, 3.0, 380, 0.0)
    if nf_mode == 'orig':          # Corruption-only proc source, as in raid.py
        F = (F[0], F[1], F[2], 0.0)
    amp = 0.10 if fil == 'Wrack' else 0.0
    xtra = {'SoulFire': (dmg(SOUL_FIRE, sp) * ev(c, 0.5), 60, 6.0, 335),
            'DeathCoil': (dmg(DEATH_COIL, sp) * sh * ev(cs, 0.5), 120, GCD, 600)}
    main = ['Corruption', bane, 'SiphonLife'] + (['Immolate'] if imm else [])

    def evaluate(plan):
        P = {n: dot(n) for n in main}
        P.update({n + SECOND: dot(n) for n in plan})
        P.update({n: xtra[n] for n in extra if not (fire_immune and n == 'SoulFire')})
        nf = (0.04, (1 + ('Corruption' in plan)) / 3, sb, 380)
        # Wrack's +10% reaches Corruption and Bane of Agony only (client class mask 0x402), on its own target
        return _finish(solve(P, F, lt, nf, amp, ('Corruption', 'BoA'), _regen(mp5, consumables)), coe)

    optional = ('Corruption', 'SiphonLife') + (('Immolate',) if imm else ())
    return _best(evaluate(p) for p in _plans(targets, optional, (None, 'BoA', 'BoD')))


# ------------------------------------------------------------------ Destruction 9/11/31
def destro(sp, c, lt=840 * 1.2, bane='BoD', version='incin', shadowburn=None, isb_mode='fixed',
           isb_dur=12.0, aftermath=False, fire_immune=False, coe=False, mp5=0.0, targets=1,
           imp_sac=True, havoc_keeps_main_bane=True, extra=(), fil=None, consumables=False):
    """version 'sb' = Imp sac + Shadow Bolt; 'incin' = Succubus sac + Incinerate; 'keep' = Succubus out, no sac.
    imp_sac False: the 'sb' version keeps the Imp out instead. A Fire version on a Fire-immune boss is not
    viable and returns (0, {}, 0). havoc_keeps_main_bane False: Havoc on the second target also costs the main
    target its Bane (the brief's reading; the tooltip says one Bane per Warlock per target)."""
    if fire_immune and version != 'sb':
        return 0.0, {}, 0.0
    if shadowburn is None:
        shadowburn = version != 'sb'
    fire_ok = not fire_immune
    sac_shadow = 1.15 if version == 'sb' and imp_sac else 1.0
    sac_fire = 1.15 if version == 'incin' else 1.0
    sh = sac_shadow * (1.10 if fire_ok else 1.0)     # S&F from Conflagrate, which needs Immolate
    fi = sac_fire * (1.10 if shadowburn else 1.0)    # S&F from Shadowburn
    AF = 1.10
    mal = 1.02
    cat = 0.9
    dstr = ev(c, 1.0)       # Ruin on Destruction spells
    dotc = ev(c, 0.5)       # Corruption / Bane, no Pandemic
    fil = fil or ('ShadowBolt' if version == 'sb' else 'Incinerate')
    direct = dmg(IMMOLATE_HIT, sp) * (1.5 if aftermath else 1.0)

    def dot(n, isb):
        if n == 'Corruption':
            return (dmg(CORRUPTION, sp) * sh * mal * dotc * isb, 18, 2.0, 340)
        if n == 'BoA':
            return (dmg(AGONY, sp) * sh * mal * dotc * isb, 24, GCD, 215)
        if n == 'BoD':
            return (dmg(DOOM, sp) * sh * mal * dotc * isb, 60, GCD, 300)
        if n == 'Havoc':
            return HAVOC
        return ((direct + dmg(IMMOLATE_DOT, sp) * mal) * fi * AF * dstr, 15, 1.5, 380 * cat)

    def build(isb, plan):
        P = {'Corruption': dot('Corruption', isb)}
        if havoc_keeps_main_bane or 'Havoc' not in plan:
            P[bane] = dot(bane, isb)
        if fire_ok:
            P['Immolate'] = dot('Immolate', 1.0)
            P['Conflagrate'] = (dmg(CONFLAGRATE, sp) * fi * AF * dstr, 10, GCD, 255 * cat)
        if shadowburn:
            P['Shadowburn'] = (dmg(SHADOWBURN, sp) * sh * AF * dstr * isb, 15, GCD, 365 * cat)
        P.update({n + SECOND: dot(n, 1.0) for n in plan})
        if 'SoulFire' in extra and fire_ok:
            P['SoulFire'] = (dmg(SOUL_FIRE, sp) * fi * AF * dstr, 60, 4.0, 335 * cat)
        if 'DeathCoil' in extra:
            P['DeathCoil'] = (dmg(DEATH_COIL, sp) * sh * ev(c, 0.5) * isb, 120, GCD, 600)
        if fil == 'ShadowBolt':
            F = (dmg(SHADOW_BOLT, sp) * sh * AF * dstr * isb, 2.5, 380 * cat, 0.0)
        elif fil == 'SearingPain':    # Agonizing Flames 3/3 also adds 10% crit to Searing Pain
            F = (dmg(SEARING_PAIN, sp) * fi * AF * ev(c + 0.10, 1.0) if fire_ok else 0.0, 1.5, 168 * cat, 0.0)
        else:
            F = (dmg(INCINERATE, sp) * 1.25 * fi * AF * dstr, 2.0, 325 * cat, 0.0)
        return P, F

    def evaluate(plan):
        copy = HAVOC_COPY if 'Havoc' in plan else 0.0
        P, F = build(1.0, plan)
        res = solve(P, F, lt, regen=_regen(mp5, consumables))
        if version == 'sb' and fil == 'ShadowBolt':
            if isb_mode == 'orig':
                # raid.py: ISB only on Shadow Bolt, n = 3.6 SB per 12 s regardless of f
                u = 1 - (1 - c) ** 3.6
                return _finish(solve(P, (F[0] * (1 + 0.2 * u),) + F[1:], lt, regen=_regen(mp5, consumables)), coe, copy)
            u = 1 - (1 - c) ** (isb_dur * res[2] / 2.5)
            P, F = build(1 + 0.2 * u, plan)
            res = solve(P, F, lt, regen=_regen(mp5, consumables))
        return _finish(res, coe, copy)

    optional = ('Corruption',) + (('Immolate',) if fire_ok else ())
    return _best(evaluate(p) for p in _plans(targets, optional, (None, 'BoA', 'BoD', 'Havoc')))


# ------------------------------------------------------------------ Demonology
def _demo_phase(sp2, c, lt, bane, allm, sh, fire, cat, immolate, regen, targets, isb_dur,
                decim=1.0, fil='SB', soul_fire=None, brand=None, fixed=None, extra=(), coe=False, fil_brand=None):
    """One phase of a Demonology rotation, Improved Shadow Bolt on the main target when the filler is Shadow
    Bolt. sh / fire: school multipliers. soul_fire: (cast s, cooldown s). brand: (period s, bonus damage per
    brand) for a Searing Pain woven in to keep Demonic Brand up. Soul Fire and the brand weave are cast only
    when they raise damage and the rotation fits in the time. Under Decimation (decim > 1) Soul Fire also needs
    a Shadow Bolt or Searing Pain at least every 10 s to keep its fast free cast. fixed: periodic entries that
    are always there (the pet swap). fil_brand: (charges, attacks per s, damage per branded attack) when the
    Searing Pain filler itself brands the target: branded attacks per second are min(charges x casts per s,
    attack rate, attack rate x 10 s x casts per s)."""
    dstr, dotc = ev(c, 1.0), ev(c, 0.5)
    spain = dmg(SEARING_PAIN, sp2) * fire * allm * dstr * decim

    def dot(n, isb):
        if n == 'Corruption':
            return (dmg(CORRUPTION, sp2) * sh * allm * dotc * isb, 18, 2.0, 340)
        if n == 'BoA':
            return (dmg(AGONY, sp2) * sh * allm * dotc * isb, 24, GCD, 215)
        if n == 'BoD':
            return (dmg(DOOM, sp2) * sh * allm * dotc * isb, 60, GCD, 300)
        return ((dmg(IMMOLATE_HIT, sp2) + dmg(IMMOLATE_DOT, sp2)) * fire * allm * dstr, 15, 1.5, 380 * cat)

    def build(isb, plan, sf, br):
        P = {'Corruption': dot('Corruption', isb), bane: dot(bane, isb)}
        if immolate:
            P['Immolate'] = dot('Immolate', 1.0)
        P.update({n + SECOND: dot(n, 1.0) for n in plan})
        if sf:
            P['Soul Fire'] = (dmg(SOUL_FIRE, sp2) * fire * allm * dstr, sf[1], sf[0], 335 * cat)
        if br:
            P['Searing Pain (Brand)'] = (spain + br[1], br[0], GCD, 168 * cat)
        if 'DeathCoil' in extra:
            P['DeathCoil'] = (dmg(DEATH_COIL, sp2) * sh * allm * ev(c, 0.5) * isb, 120, GCD, 600)
        P.update(fixed or {})
        if fil == 'SB':
            F = (dmg(SHADOW_BOLT, sp2) * sh * allm * dstr * isb * decim, 2.5, 380 * cat, 0.0)
        else:
            F = (spain, 1.5, 168 * cat, 0.0)
        return P, F

    def evaluate(plan, sf, br):
        P, F = build(1.0, plan, sf, br)
        res = solve(P, F, lt, regen=regen)
        f = res[2]
        if f < 0:
            return None
        casts = f / F[1]
        if sf and decim > 1 and casts + (1 / br[0] if br else 0.0) < 1 / BRAND_S:
            return None          # Decimation lapses: Soul Fire would be slow and cost a shard
        if fil == 'SB':
            u = 1 - (1 - c) ** (isb_dur * f / 2.5)
            res = solve(*build(1 + 0.2 * u, plan, sf, br), lt, regen=regen)
        if fil_brand:
            charges, rate, per_attack = fil_brand
            branded = min(charges * casts, rate, rate * BRAND_S * casts)
            parts = dict(res[1], **{'Demonic Brand (Imp)': branded * per_attack})
            res = (sum(parts.values()), parts, res[2])
        return _finish(res, coe)

    opts = [(sf, br) for sf in ((None, soul_fire) if soul_fire else (None,))
            for br in ((None, brand) if brand else (None,))]
    plans = _plans(targets, ('Corruption',) + (('Immolate',) if immolate else ()), (None, 'BoA', 'BoD'))
    return _best(evaluate(p, sf, br) for p in plans for sf, br in opts)


def demo(sp, c, lt=840, bane='BoD', immolate=False, isb_mode='fixed', hit_penalty=0.0, isb_dur=12.0,
         fire_immune=False, coe=False, mp5=0.0, targets=1, execute=0.0, extra=(), soul_fire=None,
         consumables=False):
    """Demonology 0/31/20 (Pact): Imp sacrificed, Succubus out, Shadow Bolt. The build has Decimation 2/2, so
    under 35% health Shadow Bolt deals 6% more and a free 2.4 s Soul Fire comes every 6 s (cast if it pays).
    soul_fire: (cast s, cooldown s) outside execute, which costs a Soul Shard each (analysis only)."""
    sp2 = sp + 60                       # Demonic Knowledge
    sh = 1.15 * 1.10                    # Imp sac + Master Demonologist (Succubus)
    allm = 1.03 * (1 - hit_penalty)     # Soul Link; optional missing-Suppression hit gap
    if isb_mode == 'orig':              # raid.py: ISB only on Shadow Bolt, n = 3.6 SB per 12 s
        dstr, dotc = ev(c, 1.0), ev(c, 0.5)
        P = {'Corruption': (dmg(CORRUPTION, sp2) * sh * allm * dotc, 18, 2.0, 340),
             bane: (dmg(DOOM if bane == 'BoD' else AGONY, sp2) * sh * allm * dotc,
                    60 if bane == 'BoD' else 24, GCD, 300 if bane == 'BoD' else 215)}
        if immolate:
            P['Immolate'] = ((dmg(IMMOLATE_HIT, sp2) + dmg(IMMOLATE_DOT, sp2)) * allm * dstr, 15, 1.5, 380 * 0.9)
        u = 1 - (1 - c) ** 3.6
        return solve(P, (dmg(SHADOW_BOLT, sp2) * sh * allm * dstr * (1 + 0.2 * u), 2.5, 380 * 0.9, 0.0), lt)
    args = (sp2, c, lt, bane, allm, sh, 1.0, 0.9, immolate and not fire_immune, _regen(mp5, consumables), targets, isb_dur)
    p1 = _demo_phase(*args, soul_fire=soul_fire, extra=extra, coe=coe)
    x = exec_share(execute)
    if not x:
        return p1
    sf = None if fire_immune else SOUL_FIRE_EXEC
    return _blend(p1, _demo_phase(*args, decim=DECIMATION, soul_fire=sf, extra=extra, coe=coe), x)


def _brand(attacks, rate, per_hit):
    """Searing Pain every period keeps the brand up: (period s, bonus damage per brand)."""
    period = min(BRAND_S, attacks / rate)
    return period, period * rate * per_hit


def demo_deep_run(sp, c, lt=840, bane='BoD', immolate=True, hit_penalty=0.0, isb_dur=12.0, fire_immune=False,
                  coe=False, mp5=0.0, targets=1, execute=0.0, brand_attacks=BRAND_ATTACKS, weave=True,
                  exec_plan='best', pet_dps=50.0, imp_dps=None, brand_scaling='lock', consumables=False):
    """Deep Demonology 0/35/16, a reader's build (talents and results in the raid v8 notes).
    Above 35%: Imp sacrificed, Succubus out, Shadow Bolt, and a Searing Pain every 10 s for Demonic Brand
    when it pays (weave). Under 35% there are two plans:
      'imp' (the reader's): Fel Domination Imp, Soul Link recast, Searing Pain filler (brands the Imp's
            attacks as often as it is cast) and Decimation Soul Fire. Summoning the Imp cancels the Imp sacrifice (Demonic Pact
            tooltip) and Master Demonologist turns to +10% Fire.
      'succubus': keep her out, Shadow Bolt, the brand weave and Decimation Soul Fire when they pay.
    exec_plan 'best' (default) takes whichever plan does more damage in the execute phase, demons included
    (pet_dps: the Succubus, imp_dps: the Imp, default IMP_BASE). A demon with 0 damage has nothing to brand.
    Returns ((dps, parts, f), plan); plan is None when there is no execute phase. Warlock and brand damage
    only; the demons themselves are in deep_pet()."""
    imp = IMP_BASE if imp_dps is None else imp_dps
    sp2 = sp + 60
    hit = 1 - hit_penalty
    allm = 1.03 * hit
    sh = 1.15 * 1.10
    tail = (0.97, immolate and not fire_immune, _regen(mp5, consumables), targets, isb_dur)     # Cataclysm 1/3
    # the brand needs your Searing Pain to land (hit) and the pet's attack to land (PET_HIT)
    per_hit = dmg(BRAND_HIT, sp2 if brand_scaling == 'lock' else PET_SP) * hit * PET_HIT * BRAND_PET
    branding = brand_attacks > 0 and not fire_immune       # 0 attacks: Demonic Brand is threat only
    succ_rate = SUCC_RATE * min(1.0, max(0.0, pet_dps) / SUCC_FULL)     # her time on the boss
    imp_rate = IMP_RATE * min(1.0, max(0.0, imp) / IMP_BASE)
    succ = _brand(brand_attacks, succ_rate, per_hit) if weave and succ_rate > 0 and branding else None
    p1 = _demo_phase(sp2, c, lt, bane, allm, sh, 1.0, *tail, brand=succ, coe=coe)
    x = exec_share(execute)
    if not x:
        return p1, None
    keep = _demo_phase(sp2, c, lt, bane, allm, sh, 1.0, *tail, decim=DECIMATION, brand=succ,
                       soul_fire=None if fire_immune else SOUL_FIRE_EXEC, coe=coe)
    if fire_immune or exec_plan == 'succubus':      # on a Fire-immune boss nothing in the swap plan lands
        return _blend(p1, keep, x), 'succubus'
    fixed = {'Pet swap': (0.0, x * FIGHT_S, SWAP[0], SWAP[1])}
    fil_brand = (brand_attacks, imp_rate, per_hit) if branding and imp_rate > 0 else None
    swap = _demo_phase(sp2, c, lt, bane, allm, 1.0, 1.10, *tail, decim=DECIMATION, fil='SearingPain',
                       soul_fire=SOUL_FIRE_EXEC, fixed=fixed, coe=coe, fil_brand=fil_brand)
    if exec_plan == 'best':
        imp_total = swap[0] + _deep_exec_pet('imp', pet_dps, imp, coe)
        keep_total = keep[0] + _deep_exec_pet('succubus', pet_dps, imp, coe)
        if keep_total >= imp_total:
            return _blend(p1, keep, x), 'succubus'
    return _blend(p1, swap, x), 'imp'


def demo_deep(sp, c, **kw):
    """demo_deep_run() without the plan: (dps, parts, f)."""
    return demo_deep_run(sp, c, **kw)[0]


def _deep_exec_pet(plan, pet_dps, imp_dps, coe):
    """Demon damage during the execute phase: the Imp for 'imp', else the Succubus."""
    if plan == 'imp':
        return DEEP_IMP_PET * imp_dps * (COE if coe else 1.0)
    return succ_mult(SUCC_DEEP, coe) * pet_dps


def deep_pet(pet_dps, imp_dps=None, execute=0.0, coe=False, fire_immune=False, exec_plan='imp'):
    """Demon damage for demo_deep: the Succubus above 35%; below it, the demon of the plan in use."""
    succ = _deep_exec_pet('succubus', pet_dps, 0.0, coe)
    x = exec_share(execute)
    if not x or exec_plan != 'imp' or fire_immune:
        return succ
    return (1 - x) * succ + x * _deep_exec_pet('imp', pet_dps, IMP_BASE if imp_dps is None else imp_dps, coe)


# ------------------------------------------------------------------ the page's seven specs, as model.js ranks them
SPEC_IDS = ('destro-fire', 'destro-keep', 'destro-shadow', 'demo-pact', 'demo-deep', 'aff-sac', 'aff-keep')
FIRE_SPECS = ('destro-fire', 'destro-keep')
SUCC_TALENTS = {'destro-keep': SUCC_PLAIN, 'demo-pact': SUCC_PACT, 'aff-keep': SUCC_PLAIN}
OPTION_KEYS = ('fire_immune', 'coe', 'mp5', 'targets', 'consumables')


def spec_run(spec, sp, c, bane, gear_hit=0.11, execute=0.0, pet_dps=50.0, imp_dps=None, life_tap=840,
             shadowburn=True, brand_hits=BRAND_ATTACKS, brand_scaling='lock', **opts):
    """Warlock damage of one page spec with one main-target Bane, and deep Demonology's execute plan (None
    for every other spec): race none, ISB 12 s. life_tap: mana per tap before Improved Life Tap (840 flat, or
    430 + Spirit). pet_dps / imp_dps matter only to demo-deep (Demonic Brand, the execute plan choice)."""
    o = {k: opts[k] for k in OPTION_KEYS if k in opts}
    supp = 1 - max(0.0, 0.16 - gear_hit - 0.05)          # Affliction and Destruction have Suppression 5/5
    pen = max(0.0, 0.16 - gear_hit)                       # the Demonology builds have none
    if spec == 'aff-sac':
        return aff(sp, c, lt=life_tap, bane=bane, immolate=True, **o)[0] * supp, None
    if spec == 'aff-keep':
        return aff(sp, c, lt=life_tap, bane=bane, sac_imp=False, immolate=True, **o)[0] * supp, None
    if spec in ('destro-fire', 'destro-keep', 'destro-shadow'):
        version = {'destro-fire': 'incin', 'destro-keep': 'keep', 'destro-shadow': 'sb'}[spec]
        return destro(sp, c, lt=life_tap * 1.2, bane=bane, version=version, shadowburn=shadowburn,
                      aftermath=version != 'sb', **o)[0] * supp, None
    if spec == 'demo-pact':
        return demo(sp, c, lt=life_tap, bane=bane, immolate=True, hit_penalty=pen, execute=execute, **o)[0], None
    res, plan = demo_deep_run(sp, c, lt=life_tap, bane=bane, hit_penalty=pen, execute=execute, pet_dps=pet_dps,
                              imp_dps=imp_dps, brand_attacks=brand_hits, brand_scaling=brand_scaling, **o)
    return res[0], plan


def spec_lock(spec, sp, c, bane, *args, **kw):
    """spec_run() without the execute plan."""
    return spec_run(spec, sp, c, bane, *args, **kw)[0]


def rank(sp, c, pet_dps=50.0, imp_dps=None, gear_hit=0.11, execute=0.0, **opts):
    """model.js rank(): best Bane per spec plus pet, viable specs first by total. exec_plan: deep Demonology's
    execute plan ('imp' or 'succubus'), None elsewhere or with no execute phase."""
    out = []
    coe = opts.get('coe', False)
    for spec in SPEC_IDS:
        if opts.get('fire_immune') and spec in FIRE_SPECS:
            out.append(dict(id=spec, viable=False, bane='', lock=0.0, pet=0.0, total=0.0, exec_plan=None))
            continue
        a, plan_a = spec_run(spec, sp, c, 'BoA', gear_hit, execute, pet_dps, imp_dps, **opts)
        d, plan_d = spec_run(spec, sp, c, 'BoD', gear_hit, execute, pet_dps, imp_dps, **opts)
        if spec == 'demo-deep':      # the plan can differ by Bane, so compare with the demons included
            fi = opts.get('fire_immune', False)
            pet_a = deep_pet(pet_dps, imp_dps, execute, coe, fi, plan_a)
            pet_d = deep_pet(pet_dps, imp_dps, execute, coe, fi, plan_d)
            if d + pet_d >= a + pet_a:
                lock, bane, pet, plan = d, 'BoD', pet_d, plan_d
            else:
                lock, bane, pet, plan = a, 'BoA', pet_a, plan_a
        else:
            lock, bane = (d, 'BoD') if d >= a else (a, 'BoA')
            talents = SUCC_TALENTS.get(spec)
            pet, plan = (succ_mult(talents, coe) * pet_dps if talents else 0.0), None
        out.append(dict(id=spec, viable=True, bane=bane, lock=lock, pet=pet, total=lock + pet, exec_plan=plan))
    return sorted(out, key=lambda r: (not r['viable'], -r['total']))


# ------------------------------------------------------------------ discrete-event check of the budget algebra
def des_check(sp=500, c=0.10, horizon=20000.0):
    """Rotation sim for Destro Succubus-sac Incinerate BoA: refresh DoTs on expiry, CDs on ready,
    Life Tap when mana short, else Incinerate. Mana starts at 0 (steady state)."""
    dps_a, parts_a, f_a = destro(sp, c, bane='BoA', version='incin')
    # rebuild the same numbers the analytic model used
    sh, fi, AF, mal, cat = 1.10, 1.15 * 1.10, 1.10, 1.02, 0.9
    dstr, dotc = ev(c, 1.0), ev(c, 0.5)
    acts = {
        'Immolate': ((dmg(IMMOLATE_HIT, sp) + dmg(IMMOLATE_DOT, sp) * mal) * fi * AF * dstr, 15, 1.5, 380 * cat),
        'Corruption': (dmg(CORRUPTION, sp) * sh * mal * dotc, 18, 2.0, 340),
        'BoA': (dmg(AGONY, sp) * sh * mal * dotc, 24, 1.5, 215),
        'Conflagrate': (dmg(CONFLAGRATE, sp) * fi * AF * dstr, 10, 1.5, 255 * cat),
        'Shadowburn': (dmg(SHADOWBURN, sp) * sh * AF * dstr, 15, 1.5, 365 * cat),
    }
    inc = (dmg(INCINERATE, sp) * 1.25 * fi * AF * dstr, 2.0, 325 * cat)
    lt = 840 * 1.2
    t, mana, dmg_done = 0.0, 0.0, 0.0
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
                dmg_done += D; did = True; break
        if did:
            continue
        if mana < inc[2]:
            mana += lt; t += GCD; continue
        mana -= inc[2]; t += inc[1]; dmg_done += inc[0]; filler_time += inc[1]
    return dmg_done / t, filler_time / t, dps_a, f_a


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
        boa_raw = dmg(AGONY, sp) / 24 * 1.10
        bod_raw = dmg(DOOM, sp) / 60
        print(f'  SP{sp}: BoD-BoA  Aff(Wrack) {a:+.1f}  Aff(SB) {a_sb:+.1f}  Destro {d:+.1f}  Demo(lock only) {m:+.1f}'
              f'   | Aff bane raw/s BoA*1.1 {boa_raw:.1f} vs BoD {bod_raw:.1f}')
    print('  SP where IBoA makes BoA out-damage BoD per second (Affliction):',
          round((1742 / 60 - 1.1 * 552 / 24) / (1.1 * 1.596 / 24 - 4.0 / 60), 0))

    print('\n  finite fight, SP500 Affliction multipliers, bane damage only (no GCD value):')
    for T in (45, 60, 75, 90, 105, 119, 120, 150, 180, 240, 300):
        sh, mal, dc = 1.15 * 1.05, 1.05, ev(C + .05, 1.0)
        boa_s = dmg(AGONY, SP) * sh * mal * 1.10 * dc / 24
        bod_hit = dmg(DOOM, SP) * sh * mal * dc
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
