"""Expected-value solo-fight simulator for a WoW: Forever Warlock.

Spell data (v8): the beta client's SpellEffect table, build 1.60.1.69893 (ElliotWood/Forever data cache).
EffectBasePointsF is the average hit or tick and EffectBonusCoefficient the spell power coefficient. Level
scaling (EffectRealPointsPerLevel, MaxLevel) is from the same build's SpellEffect and SpellLevels tables.
Level, mana, cast time, cooldown and duration: Wowhead Forever tooltips. Talent per-rank values: src/builder.js.

Deterministic expected values: hit chance and crit are folded into every hit and tick, and short procs
(Improved Shadow Bolt, Shadow and Flame) enter as the chance they are up. Forever removed DoT snapshotting,
so multipliers are applied at tick time. Cooldowns longer than a kill (Death Coil, Soul Fire, Amplify Curse)
enter as the share of pulls they are ready for (policy p_dc, p_sf, p_amp; set by evaluate() in character.py).
"""
from dataclasses import dataclass, field

# ---------------------------------------------------------------- spell ranks
# v8: every value is the client's base points. Before v8 the DoT, drain and Shadow Bolt tables read 1 higher on
# every tick and hit (the old DBC "base points + 1" convention); Wowhead agrees with the client
# (Corruption rank 1: 40 damage over 12 sec, 10 a tick).
# v8.4: level 60 uses the trainer's ranks. Shadow Bolt 10, Corruption 7 and Immolate 8 were taught only by books
# from Ruins of Ahn'Qiraj in Classic, with no Forever source yet, so Corruption rank 6 carries at 60.
CORR = [(4, 10, 4, 35), (14, 13, 5, 55), (24, 22, 6, 100), (34, 28, 6, 160),
        (44, 40, 6, 225), (54, 57, 6, 290)]                         # lvl, per 3s tick, ticks, mana
CORR_SP = 0.2
BOA = [(8, 6, 25), (18, 10, 50), (28, 14, 90), (38, 21, 130), (48, 33, 170), (58, 46, 215)]
BOA_SP = 0.133      # 12 ticks / 2s; ramp 0.5x, 1.0x, 1.5x in thirds
DL = [(14, 10, 55), (22, 14, 85), (30, 22, 135), (38, 28, 185), (46, 39, 240), (54, 51, 300)]
DL_SP = 0.1         # 5 x 1s
SL = [(30, 11, 150), (38, 19, 205), (48, 29, 285), (58, 41, 365)]
SL_SP = 0.05        # 10 x 3s
DS = [(10, 17, 55), (24, 34, 125), (38, 54, 210), (52, 84, 290)]
DS_SP = 0.1         # 5 x 3s
WRACK = (40, 36, 200)
WRACK_SP = 0.143    # 6 x 1s; +10% to your other Shadow DoTs while channeling
IMPDRAINS = {0: 0, 1: .07, 2: .14, 3: .20}
# Life Tap: lvl, health converted at the rank's MaxLevel (plus Spirit), MaxLevel. +1 a level up to MaxLevel.
LT = [(6, 30, 16), (16, 75, 26), (26, 140, 36), (36, 220, 46), (46, 310, 56), (56, 430, 66)]

# Direct damage. The last two fields of every row are EffectRealPointsPerLevel and the rank's MaxLevel (dd_avg).
SB = [(1, 13, 1.7, 25, .486, .3, 5), (6, 25, 2.2, 40, .629, .6, 11), (12, 41, 2.8, 70, .8, .7, 17),
      (20, 56, 3, 110, .857, .9, 25), (28, 78, 3, 160, .857, 1.2, 33), (36, 101, 3, 210, .857, 1.2, 41),
      (44, 141, 3, 265, .857, 1.4, 49), (52, 191, 3, 315, .857, 1.6, 57),
      (60, 251, 3, 370, .857, 1.8, 65)]                           # lvl, avg hit, cast, mana, coef, per lvl, max
IMM = [(1, 8, 25, 3, .7, 5), (10, 17, 45, 6, .8, 15), (20, 32, 90, 12, 1.2, 25), (30, 56, 155, 19, 1.5, 35),
       (40, 72, 220, 25, 1.6, 45), (50, 106, 295, 38, 1.9, 55),
       (60, 146, 370, 52, 2.3, 65)]                               # lvl, avg hit, mana, per 3s tick (x5), per lvl, max
IMM_SP, IMM_TICK_SP, IMM_CAST = 0.2, 0.13, 2.0                    # client: 0.2 on the hit, 0.13 a tick
SEAR = [(18, 23, 45, .6, 24), (26, 33, 68, .7, 32), (34, 44, 91, .8, 40), (42, 62, 118, .9, 48),
        (50, 85, 141, 1.0, 56), (58, 114, 168, 1.2, 64)]          # Searing Pain: lvl, avg, mana, per lvl, max; 1.5s
CONF = [(25, 95, 100, .9, 30), (32, 122, 130, .9, 38), (40, 146, 165, 1.0, 46), (48, 194, 200, 1.1, 54),
        (54, 239, 230, 1.2, 60), (60, 282, 255, 1.3, 66)]         # Conflagrate: instant, 10s cooldown
BURN = [(20, 66, 105, .9, 24), (24, 80, 130, 1.0, 30), (32, 118, 190, 1.3, 38), (40, 148, 245, 1.3, 46),
        (48, 203, 305, 1.6, 54), (56, 266, 365, 1.8, 62)]         # Shadowburn: instant, 15s cooldown
INCIN = [(40, 97, 205, 1.1, 49), (50, 145, 265, 1.3, 59), (60, 217, 325, 1.4, 69)]   # 2.5s, +25% on Immolate
SOULFIRE = [(48, 377, 305, 1.7, 54), (56, 431, 335, 1.9, 62)]   # 6s cast, 60s cooldown, costs a Soul Shard
DCOIL = [(42, 272, 435, 2.2, 48), (50, 359, 525, 2.6, 56), (58, 454, 600, 3.0, 64)]  # instant, 2 min, heals you
COE = [(20, .04, 50), (30, .06, 100), (40, .08, 150), (50, .10, 200)]   # Curse of the Elements: lvl, taken, mana
SEAR_SP = CONF_SP = BURN_SP = 0.429
INCIN_SP, SOULFIRE_SP, DCOIL_SP = 0.714, 1.0, 0.214

# Talent per-rank values (src/builder.js)
CATA = (0, .03, .07, .10)       # Cataclysm: Destruction spells cost less mana
AFLAMES = (0, .03, .07, .10)    # Agonizing Flames: Destruction damage, and the same again as Searing Pain crit
FNB = (0, .08, .17, .25)        # Fire and Brimstone: Conflagrate crit chance
SH_BONUS = (0, .5, 1.0)         # Soul Harvesting: mana regeneration for 10 sec after a Drain Soul kill
BASE_HIT = {0: .96, 1: .95, 2: .94, 3: .83}
ISB_DUR = 12.0                  # Improved Shadow Bolt debuff, sec (client 17794; no charges). A community guide says 60.
SNF_DUR = 20.0                  # Shadow and Flame buffs, sec
# Not scored, no single-target leveling effect: Destructive Reach (range), Intensity (pushback; spell pushback
# is not modelled), Pyroclasm (a stun on Soul Fire), Bane of Havoc (copies damage from other targets; scored
# only as Incinerate's prerequisite).


def rank(table, lvl):
    best = None
    for row in table:
        if row[0] <= lvl:
            best = row
    return best


def dd_avg(row, lvl, mode='base'):
    """Average direct hit of a rank. 'base': the client's base points (the default). 'scaled': plus
    EffectRealPointsPerLevel for every character level above the rank's own, up to its MaxLevel (the in-game
    formula). 'wowhead': at MaxLevel, which is what Wowhead's tooltips print (Immolate rank 7: 146 + 5 x 2.3)."""
    per, top = row[-2], row[-1]
    if mode == 'scaled':
        return row[1] + per * max(0, min(lvl, top) - row[0])
    if mode == 'wowhead':
        return row[1] + per * (top - row[0])
    return row[1]


def lt_health(row, lvl, mode='base'):
    """Health Life Tap converts before Spirit. 'base' and 'wowhead' keep the MaxLevel value the model has
    always used; 'scaled' takes 1 off for every level below MaxLevel."""
    if mode == 'scaled':
        return row[1] - max(0, row[2] - lvl)
    return row[1]


@dataclass
class Char:
    level: int
    sp: float
    crit: float = 0.05
    spirit: float = 0.0
    max_hp: float = 1000.0
    max_mana: float = 1000.0
    wand_dps: float = 0.0
    pet_dps: float = 0.0
    talents: dict = field(default_factory=dict)
    shadow_mult: float = 1.0       # Demonic Sacrifice (Imp) / Master Demonologist / Soul Link
    mob_level_diff: int = 0
    mob_dps: float = 0.0
    taken_frac: float = 0.0
    felhunter_sac: bool = False   # Demonic Sacrifice (Felhunter): 3% max HP every 4s
    voidwalker_sac: bool = False  # Demonic Sacrifice (Voidwalker): 2% max mana every 4s
    fire_mult: float = 1.0        # Demonic Sacrifice (Succubus) / Master Demonologist (Imp) / Soul Link
    dd_mode: str = 'base'         # direct damage and Life Tap level scaling, see dd_avg
    supp_all: bool = True         # Suppression's hit covers every spell (client 18174: no spell family mask)

    def t(self, name):
        return self.talents.get(name, 0)

    @property
    def hit(self):
        """Affliction spells and the wand: base hit plus Suppression."""
        return min(.99, BASE_HIT[self.mob_level_diff] + .01 * self.t('Suppression'))

    @property
    def hit_destro(self):
        """Destruction spells. The client's Suppression is A_MOD_SPELL_HIT_CHANCE with no spell family mask, so
        it covers them too; supp_all=False is the Classic reading (Affliction spells only)."""
        return self.hit if self.supp_all else min(.99, BASE_HIT[self.mob_level_diff])

    def total_sp(self):
        return self.sp + self.level * self.t('DemonicKnowledge') / 3.0


DT = 0.02
AFF_DOTS = ('Corruption', 'BoA', 'SiphonLife')
FILLERS = ('Wand', 'DrainLife', 'ShadowBolt', 'SearingPain', 'Incinerate', 'Wrack')
CHANNELS = ('DrainLife', 'DrainSoul', 'Wrack')
INSTANTS = ('Conflagrate', 'Shadowburn', 'DeathCoil')
NO_NIGHTFALL = AFF_DOTS + ('Immolate', 'CoE', 'Conflagrate', 'Shadowburn', 'SoulFire', 'DeathCoil')


def full_prio(policy):
    """The priority list with the modifiers in place: the curse first, then the base policy's DoTs, then
    Death Coil and the finisher, then the filler."""
    prio = list(policy['prio'])
    i = next((j for j, s in enumerate(prio) if s in FILLERS), len(prio))
    mods = (['DeathCoil'] if policy.get('dc') else []) + ([policy['fin']] if policy.get('fin') else [])
    return (['CoE'] if policy.get('coe') else []) + prio[:i] + mods + prio[i:]


def fight_ranks(ch):
    """The rank of every spell at this level, or None when the level or the talent is missing."""
    L, T = ch.level, ch.t
    r = dict(corr=rank(CORR, L), boa=rank(BOA, L), sb=rank(SB, L), dl=rank(DL, L), ds=rank(DS, L),
             imm=rank(IMM, L), lt=rank(LT, L), sear=rank(SEAR, L), coe=rank(COE, L), dc=rank(DCOIL, L),
             sl=rank(SL, L) if T('SiphonLife') else None, conf=rank(CONF, L) if T('Conflagrate') else None,
             burn=rank(BURN, L) if T('Shadowburn') else None, incin=rank(INCIN, L) if T('Incinerate') else None,
             sf=rank(SOULFIRE, L) if T('Decimation') else None)
    r['wrack'] = WRACK if T('Wrack') and L >= 40 else None
    return r


def usable_steps(prio, ch):
    """The steps of a priority list this character can cast, without a trailing wand (the fallback anyway).
    evaluate() skips a policy whose usable steps match one it already ran."""
    r = fight_ranks(ch)
    have = dict(Corruption=r['corr'], BoA=r['boa'], SiphonLife=r['sl'], Wrack=r['wrack'], DrainLife=r['dl'],
                DrainSoul=r['ds'], ShadowBolt=r['sb'], Immolate=r['imm'], Conflagrate=r['conf'],
                SearingPain=r['sear'], Incinerate=r['incin'], Wand=True)
    steps = [s for s in prio if have.get(s)]
    while steps and steps[-1] == 'Wand':
        steps.pop()
    return tuple(steps)


def fight_mults(ch):
    """Static multipliers: hit, crit expected values and talent percentages."""
    T = ch.t
    crit_s = ch.crit + .01 * T('Malevolence')        # Malevolence: Shadow spells only
    crit_f = ch.crit
    ruin = 1.5 + .1 * T('Ruin')                     # Ruin: +20% of the crit bonus a point, 2x crits at 5/5
    pand = 1.5 + 0.5 * T('Pandemic') / 3.0
    af = AFLAMES[T('AgonizingFlames')]
    hit_d = ch.hit_destro
    return dict(
        hit=ch.hit, hit_d=hit_d, sm=1 + .01 * T('ShadowMastery'), mal=1 + .01 * T('Malediction'),
        af=1 + af, cata=1 - CATA[T('Cataclysm')], after=1 + .1 * T('Aftermath'),
        evc_dot=1 + crit_s * (pand - 1),                          # Affliction DoTs and drains (Pandemic)
        evc_sd=1 + crit_s * (ruin - 1),                           # Shadow Bolt, Shadowburn
        evc_fd=1 + crit_f * (ruin - 1),                           # Fire spells; Immolate ticks too (assumed)
        evc_sear=1 + (crit_f + af) * (ruin - 1),
        evc_conf=1 + (crit_f + FNB[T('FireAndBrimstone')]) * (ruin - 1),
        evc_dc=1 + crit_s * 0.5,                                  # Death Coil: neither Ruin nor Pandemic
        isb=.04 * T('ImprovedShadowBolt'), isb_p=hit_d * crit_s,
        snf=.02 * T('ShadowAndFlame'), keep=.2 * T('ShadowAndFlame'))


def _at(row, i, mult=1.0):
    return row[i] * mult if row else 0.0


def fight_costs(k):
    cata = k['cata']
    return dict(Corruption=_at(k['corr'], 3), BoA=_at(k['boa'], 2), SiphonLife=_at(k['sl'], 2),
                DrainLife=_at(k['dl'], 2), DrainSoul=_at(k['ds'], 2), Wrack=_at(k['wrack'], 2),
                CoE=_at(k['coe'], 2), ShadowBolt=_at(k['sb'], 3, cata), Immolate=_at(k['imm'], 2, cata),
                SearingPain=_at(k['sear'], 2, cata), Conflagrate=_at(k['conf'], 2, cata),
                Shadowburn=_at(k['burn'], 2, cata), Incinerate=_at(k['incin'], 2, cata),
                SoulFire=_at(k['sf'], 2, cata * k['p_sf']), DeathCoil=_at(k['dc'], 2, k['p_dc']), Wand=0.0)


def fight_casts(k, bane, ic):
    """Cast times after Bane (0.1 sec a point, 0.4 on Soul Fire) and Improved Corruption. Soul Fire is only
    cast under Decimation (40% faster). A cooldown spell ready on a share p of pulls costs p of its time."""
    sf = max(1.5, (6.0 - .4 * bane) * 0.6)
    return dict(Corruption=max(0.0, 2.0 - 0.4 * ic), ShadowBolt=max(1.5, k['sb'][2] - .1 * bane),
                Immolate=max(1.5, IMM_CAST - .1 * bane), SearingPain=1.5, Incinerate=max(1.5, 2.5 - .1 * bane),
                SoulFire=sf * k['p_sf'])


def fight_hits(k, L, mode):
    """Expected damage of one cast before the live school multipliers (curse, procs, Shadow Mastery, sacrifice)."""
    sp, af, hit_d = k['sp'], k['af'], k['hit_d']

    def part(row, coef):
        return dd_avg(row, L, mode) + coef * sp if row else 0.0
    return dict(
        ShadowBolt=part(k['sb'], k['sb'][4]) * af * k['evc_sd'] * hit_d,
        Shadowburn=part(k['burn'], BURN_SP) * af * k['evc_sd'] * hit_d,
        Immolate=part(k['imm'], IMM_SP) * af * k['after'] * k['evc_fd'] * hit_d,
        ImmolateTick=(k['imm'][3] + IMM_TICK_SP * sp) * af * k['mal'] * k['evc_fd'] * hit_d,
        SearingPain=part(k['sear'], SEAR_SP) * af * k['evc_sear'] * hit_d,
        Conflagrate=part(k['conf'], CONF_SP) * af * k['evc_conf'] * hit_d,
        Incinerate=part(k['incin'], INCIN_SP) * af * k['evc_fd'] * hit_d,
        SoulFire=part(k['sf'], SOULFIRE_SP) * af * k['evc_fd'] * hit_d * k['p_sf'],
        DeathCoil=part(k['dc'], DCOIL_SP) * k['evc_dc'] * k['hit'] * k['p_dc'])


def fight_consts(ch, policy):
    """Everything about a fight that stays fixed while it runs."""
    L, T, mode = ch.level, ch.t, ch.dd_mode
    k = dict(fight_ranks(ch), **fight_mults(ch))
    k['sp'], k['prio'] = ch.total_sp(), full_prio(policy)
    k['p_amp'] = policy.get('p_amp', 1.0 if policy.get('amp') else 0.0) if T('AmplifyCurse') else 0.0
    k['p_dc'], k['p_sf'] = policy.get('p_dc', 1.0), policy.get('p_sf', 1.0)
    k['lt_amt'] = lt_health(k['lt'], L, mode) + ch.spirit if k['lt'] else 0.0    # Life Tap is learned at level 6
    k['ilt'] = 1 + .10 * T('ImprovedLifeTap')
    k['nf'] = .02 * T('Nightfall')
    k['dec'] = bool(T('Decimation'))
    k['sf_cd'] = 60 * (1 - .45 * T('Decimation'))
    k['coe_mult'] = 1 + k['coe'][1] * k['hit'] if k['coe'] else 1.0
    k['cost'] = fight_costs(k)
    k['ct'] = fight_casts(k, T('Bane'), T('ImprovedCorruption'))
    k['base'] = fight_hits(k, L, mode)
    return k


def simulate(ch: Char, mob_hp: float, policy: dict, max_time=240.0):
    k = fight_consts(ch, policy)
    T = ch.t
    S = dict(mana_spent=0.0, lt_mana=0.0, hp_spent=0.0, healed=0.0, casts={}, dmg={}, hp_taken=0.0, ds_kill=False)
    st = dict(hp=mob_hp, t=0.0, mana=ch.max_mana, php=ch.max_hp, wrack_until=-1.0, nfc=0.0, gcd=0.0, wand=False,
              amp=k['p_amp'], coe=1.0, coe_on=False, cd=dict(Conflagrate=0.0, Shadowburn=0.0, SoulFire=0.0),
              dec_until=-1.0, dc_done=False)
    dots, chan, cast = {}, [None], [None]
    procs = dict(isb=[], snf_s=[], snf_f=[])       # (time, chance it landed) of each proc-giving hit

    def dmg(name, x):
        st['hp'] -= x
        S['dmg'][name] = S['dmg'].get(name, 0) + x

    def heal(x):
        st['php'] = min(ch.max_hp, st['php'] + x)
        S['healed'] += x

    def p_up(evs, dur):
        q = 1.0
        for t0, p in evs:
            if t0 <= st['t'] < t0 + dur:
                q *= 1 - p
        return 1 - q

    def shadow_now():
        m = k['sm'] * ch.shadow_mult * st['coe']
        if k['isb']:
            m *= 1 + k['isb'] * p_up(procs['isb'], ISB_DUR)    # Improved Shadow Bolt
        if k['snf']:
            m *= 1 + k['snf'] * p_up(procs['snf_s'], SNF_DUR)  # Shadow and Flame after Conflagrate
        return m

    def fire_now():
        m = ch.fire_mult * st['coe']
        if k['snf']:
            m *= 1 + k['snf'] * p_up(procs['snf_f'], SNF_DUR)  # Shadow and Flame after Shadowburn
        return m

    def n_affl():
        return min(3, sum(1 for d in AFF_DOTS if d in dots))

    def dot_mult(name):
        m = shadow_now() * k['mal'] * k['evc_dot'] * k['hit']
        if name == 'Corruption':
            m *= 1 + .02 * T('ImprovedCorruption')
        if name == 'BoA':
            m *= 1 + .05 * T('ImprovedBoA')
        if st['t'] < st['wrack_until']:
            m *= 1.10
        return m

    def drain_mult():
        return (shadow_now() * k['mal'] * k['evc_dot'] * k['hit'] * (1 + IMPDRAINS[T('ImprovedDrains')])
                * (1 + .04 * T('SoulSiphon') * n_affl()))

    def spend(name, cost):
        st['mana'] -= cost
        S['mana_spent'] += cost
        S['casts'][name] = S['casts'].get(name, 0) + 1

    def life_tap():
        amt = k['lt_amt']
        st['php'] -= amt
        S['hp_spent'] += amt
        gain = amt * k['ilt']
        st['mana'] += gain
        S['lt_mana'] += gain
        S['casts']['LifeTap'] = S['casts'].get('LifeTap', 0) + 1

    def apply_dot(name):
        t, sp = st['t'], k['sp']
        if name == 'Corruption':
            dots[name] = dict(next=t + 3, left=k['corr'][2], per=k['corr'][1] + CORR_SP * sp, period=3)
        elif name == 'BoA':
            amp = 1 + 0.5 * st['amp']                        # Amplify Curse on a share of pulls
            st['amp'] = 0.0
            dots[name] = dict(next=t + 2, left=12, per=(k['boa'][1] + BOA_SP * sp) * amp, period=2, n=0)
        elif name == 'SiphonLife':
            dots[name] = dict(next=t + 3, left=10, per=k['sl'][1] + SL_SP * sp, period=3)
        elif name == 'Immolate':
            dots[name] = dict(next=t + 3, left=5, per=k['base']['ImmolateTick'], period=3, q=1.0)

    def tick_dots(t):
        for name in list(dots):
            d = dots[name]
            if t < d['next'] - 1e-9:
                continue
            per = d['per']
            if 'n' in d:
                d['n'] += 1
                per *= 0.5 if d['n'] <= 4 else (1.0 if d['n'] <= 8 else 1.5)
            x = per * (fire_now() if name == 'Immolate' else dot_mult(name))
            dmg(name, x)
            if name == 'SiphonLife':
                heal(x)
            if name == 'Corruption' and k['nf']:
                st['nfc'] += k['nf']
            d['left'] -= 1
            d['next'] += d['period']
            if d['left'] <= 0:
                del dots[name]

    def tick_channel(t):
        c = chan[0]
        if not c or t < c['next'] - 1e-9:
            return
        x = c['per'] * drain_mult()
        dmg(c['name'], x)
        if c['name'] == 'DrainLife':
            heal(x)
        if k['nf']:
            st['nfc'] += k['nf']
        c['left'] -= 1
        c['next'] += c['period']
        if c['left'] <= 0:
            chan[0] = None

    def decimate(below):
        if k['dec'] and below:           # Decimation: Shadow Bolt or Searing Pain under 35% readies Soul Fire
            st['dec_until'] = st['t'] + 10.0

    def bolt(name):
        below = st['hp'] < .35 * mob_hp
        dmg(name, k['base']['ShadowBolt'] * shadow_now())
        if k['isb']:
            procs['isb'].append((st['t'], k['isb_p']))
        decimate(below)

    def land(a):
        if a == 'Corruption':
            apply_dot(a)
        elif a == 'ShadowBolt':
            bolt(a)
        elif a == 'Immolate':
            dmg(a, k['base'][a] * fire_now())
            apply_dot(a)
        elif a == 'SearingPain':
            below = st['hp'] < .35 * mob_hp
            dmg(a, k['base'][a] * fire_now())
            decimate(below)
        elif a == 'Incinerate':
            d = dots.get('Immolate')
            dmg(a, k['base'][a] * (1 + .25 * (d['q'] if d else 0.0)) * fire_now())
        elif a == 'SoulFire':
            dmg(a, k['base'][a] * fire_now())
            st['cd'][a] = st['t'] + k['sf_cd']

    def instant(a, t):
        if a == 'Conflagrate':
            dmg(a, k['base'][a] * fire_now())
            st['cd'][a] = t + 10.0
            if k['snf']:
                procs['snf_s'].append((t, k['hit_d']))
            if k['keep'] < 1:                  # consumes Immolate unless Shadow and Flame saves it (20% a point)
                d, q = dots['Immolate'], 1 - k['hit_d'] * (1 - k['keep'])
                d['per'] *= q
                d['q'] *= q
                d['gone'] = True
        elif a == 'Shadowburn':
            dmg(a, k['base'][a] * shadow_now())
            st['cd'][a] = t + 15.0
            if k['snf']:
                procs['snf_f'].append((t, k['hit_d']))
        elif a == 'DeathCoil':
            x = k['base'][a] * shadow_now()
            dmg(a, x)
            heal(x)
            st['dc_done'] = True

    def channel(a, t):
        sp = k['sp']
        if a == 'DrainLife':
            chan[0] = dict(name=a, next=t + 1, left=5, period=1, per=k['dl'][1] + DL_SP * sp)
        elif a == 'DrainSoul':
            chan[0] = dict(name=a, next=t + 3, left=5, period=3, per=k['ds'][1] + DS_SP * sp)
        else:
            chan[0] = dict(name=a, next=t + 1, left=6, period=1, per=WRACK[1] + WRACK_SP * sp)
            st['wrack_until'] = t + 6

    def start(a, t):
        if a in CHANNELS:
            channel(a, t)
        elif a in ('BoA', 'SiphonLife'):
            apply_dot(a)
        elif a == 'CoE':
            st['coe'], st['coe_on'] = k['coe_mult'], True
        elif a in INSTANTS:
            instant(a, t)
        elif k['ct'][a] > 0:
            cast[0] = dict(end=t + k['ct'][a], fn=lambda: land(a))
        else:
            land(a)

    def act(a, t):
        if a != 'Wand':
            st['wand'] = False
            st['gcd'] = t + 1.5 * (k['p_dc'] if a == 'DeathCoil' else (k['p_sf'] if a == 'SoulFire' else 1.0))
        if a == 'LifeTap':
            life_tap()
        elif a == 'Wand':
            st['wand'] = True
        elif a == 'NightfallSB':
            st['nfc'] -= 1
            spend('ShadowBolt', k['cost']['ShadowBolt'])
            bolt('Nightfall')
        else:
            spend(a, k['cost'][a])
            start(a, t)

    while st['hp'] > 0 and st['t'] < max_time:
        t = st['t']
        ds_on = chan[0] is not None and chan[0]['name'] == 'DrainSoul'
        tick_dots(t)
        tick_channel(t)
        kc = cast[0]
        if kc and t >= kc['end'] - 1e-9:
            cast[0] = None
            kc['fn']()
        dmg('Pet', ch.pet_dps * DT)
        taken = ch.mob_dps * ch.taken_frac * DT
        st['php'] -= taken
        S['hp_taken'] += taken
        if ch.felhunter_sac:
            heal(0.03 * ch.max_hp / 4 * DT)
        if ch.voidwalker_sac:
            st['mana'] = min(ch.max_mana * 2, st['mana'] + 0.02 * ch.max_mana / 4 * DT)
        busy = chan[0] is not None or cast[0] is not None
        if st['wand'] and not busy:
            dmg('Wand', ch.wand_dps * DT * k['hit'] * st['coe'])
        if not busy and t >= st['gcd'] - 1e-9 and st['hp'] > 0:
            a = choose(policy, ch, dots, st, mob_hp, k)
            if st['nfc'] >= 1 and st['mana'] >= k['cost']['ShadowBolt'] and a not in NO_NIGHTFALL:
                a = 'NightfallSB'
            act(a, t)
        if st['hp'] <= 0:
            S['ds_kill'] = ds_on                 # Soul Harvesting: the mob died with Drain Soul on it
        st['t'] += DT
    S['ttk'] = st['t']
    S['end_mana'] = st['mana']
    S['end_hp'] = st['php']
    # net resource change in mana-equivalents (1 health = 1.2 mana via tapped Life Tap w/ ILT 2/2)
    S['net_mana'] = st['mana'] - ch.max_mana
    S['net_hp'] = st['php'] - ch.max_hp
    return S


def imm_up(dots):
    return 'Immolate' in dots and not dots['Immolate'].get('gone')


def ready(step, policy, dots, st, frac, k):
    """Whether a priority step can be cast now, mana aside."""
    t = st['t']
    if step == 'Corruption':
        return bool(k['corr']) and 'Corruption' not in dots and frac > policy.get('corr_min', 0.15)
    if step == 'BoA':
        return bool(k['boa']) and 'BoA' not in dots and frac > policy.get('boa_min', 0.5)
    if step == 'SiphonLife':
        return bool(k['sl']) and 'SiphonLife' not in dots and frac > policy.get('sl_min', 0.4)
    if step == 'Wrack':
        return bool(k['wrack']) and frac > 0.25 and sum(1 for d in AFF_DOTS if d in dots) >= 2
    if step == 'DrainLife':
        return bool(k['dl'])
    if step == 'DrainSoul':
        return bool(k['ds']) and frac <= policy.get('ds_below', 0.25)
    if step == 'Immolate':
        return not imm_up(dots) and frac > policy.get('imm_min', 0.2)
    if step == 'Conflagrate':
        return bool(k['conf']) and imm_up(dots) and t >= st['cd']['Conflagrate'] - 1e-9
    if step == 'SearingPain':
        return bool(k['sear'])
    if step == 'Incinerate':
        return bool(k['incin'])
    if step == 'Shadowburn':       # finisher only: the mob dies within 8 sec, so the Soul Shard comes back
        return bool(k['burn']) and t >= st['cd']['Shadowburn'] - 1e-9 and frac <= policy.get('burn_below', 0.2)
    if step == 'SoulFire':         # only under Decimation, which also makes it free of a Soul Shard
        return bool(k['sf']) and t < st['dec_until'] and t >= st['cd']['SoulFire'] - 1e-9
    if step == 'DeathCoil':
        return bool(k['dc']) and not st['dc_done']
    if step == 'CoE':
        return bool(k['coe']) and not st['coe_on']
    return step in ('ShadowBolt', 'Wand')


def choose(policy, ch, dots, st, mob_hp, k):
    frac = st['hp'] / mob_hp
    has_lt = bool(k['lt'])                    # no Life Tap before level 6: never tap, wand when out of mana
    lt_gain = k['lt_amt'] * k['ilt']
    if (has_lt and st['php'] - k['lt_amt'] > policy.get('tap_above', 0.75) * ch.max_hp
            and st['mana'] + lt_gain <= ch.max_mana):
        return 'LifeTap'
    lt_ok = has_lt and st['php'] > policy.get('lt_hp_floor', 0.35) * ch.max_hp
    for step in k['prio']:
        if not ready(step, policy, dots, st, frac, k):
            continue
        if step == 'Wand':
            return 'Wand'
        if st['mana'] >= k['cost'][step]:
            return step
        if lt_ok:
            return 'LifeTap'
        return 'Wand'
    return 'Wand'


# ---------------------------------------------------------------- per-kill economics
def rest_seconds(deficit, rest_rate, walk_gain=0.0, drink_boost=0.0):
    """Rest time for a deficit in mana-equivalents. Soul Harvest lasts 10 sec after a Drain Soul kill. Spent
    walking, it adds walk_gain (natural mana regen, raised). If it also speeds up drinking (the harvest_drink
    assumption), the player may drink first instead, at rest_rate + drink_boost for up to 10 sec; the better
    order counts."""
    rest = max(0.0, deficit - walk_gain) / rest_rate
    if drink_boost > 0:
        fast = rest_rate + drink_boost
        first = deficit / fast if deficit <= 10 * fast else 10 + (deficit - 10 * fast) / rest_rate
        rest = min(rest, first)
    return rest


def rest_model(ch, rest_rate=None, regen_rate=None):
    """The rest model of seconds_per_kill, shared with models/multimob.py: (k, drink, rest_rate, mana_regen,
    regen_rate). k is the mana-equivalent of 1 health (Life Tap's rate), drink the drink half of rest_rate."""
    L = ch.level
    k = 1 + .10 * ch.t('ImprovedLifeTap')
    drink = 2.2 * L
    if rest_rate is None:
        rest_rate = drink + 1.2 * L * k   # Classic-style level-appropriate water + food, assumption
    mana_regen = (8 + ch.spirit / 4) / 2
    if regen_rate is None:
        regen_rate = mana_regen + ch.spirit / 5 * k * 0.5  # out-of-combat, rough Classic shape
    return k, drink, rest_rate, mana_regen, regen_rate


def seconds_per_kill(ch, mob_hp, policy, travel=8.0, rest_rate=None, regen_rate=None, harvest_drink=False):
    """TTK + travel + time to rest back the net resource deficit.

    Resource is counted in mana-equivalents: 1 health = (1 + 0.1*ILT) mana, because
    Life Tap converts it at that rate. Rest (eat + drink together) restores
    rest_rate mana-eq per second. Natural regen during travel is regen_rate.
    Soul Harvesting (after a Drain Soul kill) raises natural mana regen for 10 sec; harvest_drink=True also
    lets it raise the drink half of rest_rate (a reader's claim, untested in game).
    Before level 6 there is no Life Tap, so health and mana rest apart: eat and drink together, the slower counts.
    """
    k, drink, rest_rate, mana_regen, regen_rate = rest_model(ch, rest_rate, regen_rate)
    s = simulate(ch, mob_hp, policy)
    bonus = SH_BONUS[ch.t('SoulHarvesting')] if s['ds_kill'] else 0.0
    walk = bonus * mana_regen * min(10.0, travel)
    boost = bonus * drink if harvest_drink else 0.0
    if rank(LT, ch.level):
        net = s['net_mana'] + k * s['net_hp'] + regen_rate * travel
        s['rest'] = rest_seconds(max(0.0, -net), rest_rate, walk, boost)
    else:
        # rest_rate and regen_rate count health at k mana a point; the health side takes k back out (k >= 1)
        eat, hp_regen = (rest_rate - drink) / k, (regen_rate - mana_regen) / k
        m_def = max(0.0, -(s['net_mana'] + mana_regen * travel))
        h_def = max(0.0, -(s['net_hp'] + hp_regen * travel))
        s['rest'] = max(rest_seconds(m_def, drink, walk, boost), h_def / eat)
    s['spk'] = s['ttk'] + travel + s['rest']
    return s
