"""Expected-value solo-fight simulator for a WoW: Forever Warlock.

Spell data: Wowhead Forever spell pages (base per-tick values and SP coefficients),
pulled 2026-09-28. Talent per-rank values: Wowhead calculator hover tooltips,
cross-checked against third-party talent tables.

Deterministic expected values: hit chance and crit are folded into every hit/tick.
Forever removed DoT snapshotting, so multipliers are applied at tick time.
"""
from dataclasses import dataclass, field

# ---------------------------------------------------------------- spell ranks
CORR = [(4, 11, 4, 35), (14, 14, 5, 55), (24, 23, 6, 100), (34, 29, 6, 160),
        (44, 41, 6, 225), (54, 58, 6, 290), (60, 74, 6, 340)]      # lvl, per 3s tick, ticks, mana
CORR_SP = 0.2
BOA = [(8, 7, 25), (18, 11, 50), (28, 15, 90), (38, 22, 130), (48, 34, 170), (58, 47, 215)]
BOA_SP = 0.133      # 12 ticks / 2s; ramp 0.5x, 1.0x, 1.5x in thirds
SB = [(1, 14, 1.7, 25, .486), (6, 26, 2.2, 40, .629), (12, 42, 2.8, 70, .8), (20, 57, 3, 110, .857),
      (28, 79, 3, 160, .857), (36, 102, 3, 210, .857), (44, 142, 3, 265, .857), (52, 192, 3, 315, .857),
      (60, 269, 3, 380, .857)]                                    # lvl, avg hit, cast, mana, coef
DL = [(14, 11, 55), (22, 15, 85), (30, 23, 135), (38, 29, 185), (46, 40, 240), (54, 52, 300)]
DL_SP = 0.1         # 5 x 1s
SL = [(30, 12, 150), (38, 20, 205), (48, 30, 285), (58, 42, 365)]
SL_SP = 0.05        # 10 x 3s
DS = [(10, 18, 55), (24, 35, 125), (38, 55, 210), (52, 85, 290)]
DS_SP = 0.1         # 5 x 3s
LT = [(6, 30), (16, 75), (26, 140), (36, 220), (46, 310), (56, 430)]   # health converted = base + Spirit
WRACK = (40, 37, 200)
WRACK_SP = 0.143    # 6 x 1s; +10% to your other Shadow DoTs while channeling
IMPDRAINS = {0: 0, 1: .07, 2: .14, 3: .20}


def rank(table, lvl):
    best = None
    for row in table:
        if row[0] <= lvl:
            best = row
    return best


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

    def t(self, name):
        return self.talents.get(name, 0)

    @property
    def hit(self):
        base = {0: .96, 1: .95, 2: .94, 3: .83}[self.mob_level_diff]
        return min(.99, base + .01 * self.t('Suppression'))

    def total_sp(self):
        return self.sp + self.level * self.t('DemonicKnowledge') / 3.0


DT = 0.02


def simulate(ch: Char, mob_hp: float, policy: dict, max_time=240.0):
    lvl = ch.level
    sp = ch.total_sp()
    hit = ch.hit
    sm = 1 + .01 * ch.t('ShadowMastery')
    mal = 1 + .01 * ch.t('Malediction')
    crit = ch.crit + .01 * ch.t('Malevolence')
    pand = 1.5 + 0.5 * ch.t('Pandemic') / 3.0
    evc_dot = 1 + crit * (pand - 1)          # DoT / drain crit EV
    evc_sb = 1 + crit * 0.5                  # Shadow Bolt crit EV (no Ruin)
    corr, boa, sb, dl, ds = (rank(CORR, lvl), rank(BOA, lvl), rank(SB, lvl), rank(DL, lvl), rank(DS, lvl))
    sl = rank(SL, lvl) if ch.t('SiphonLife') else None
    wrack_ok = bool(ch.t('Wrack')) and lvl >= 40
    lt = rank(LT, lvl)
    nf = .02 * ch.t('Nightfall')
    sb_hit = (sb[1] + sb[4] * sp) * sm * ch.shadow_mult * evc_sb * hit

    S = dict(mana_spent=0.0, lt_mana=0.0, hp_spent=0.0, healed=0.0, casts={}, dmg={})
    st = dict(hp=mob_hp, t=0.0, mana=ch.max_mana, php=ch.max_hp, wrack_until=-1.0,
              amp=bool(policy.get('amp')) and bool(ch.t('AmplifyCurse')))
    dots, chan, cast = {}, [None], [None]

    def dmg(name, x):
        st['hp'] -= x
        S['dmg'][name] = S['dmg'].get(name, 0) + x

    def heal(x):
        st['php'] = min(ch.max_hp, st['php'] + x)
        S['healed'] += x

    def n_affl():
        return min(3, sum(1 for k in ('Corruption', 'BoA', 'SiphonLife') if k in dots))

    def dot_mult(name):
        m = sm * mal * ch.shadow_mult * evc_dot * hit
        if name == 'Corruption':
            m *= 1 + .02 * ch.t('ImprovedCorruption')
        if name == 'BoA':
            m *= 1 + .05 * ch.t('ImprovedBoA')
        if st['t'] < st['wrack_until']:
            m *= 1.10
        return m

    def drain_mult():
        return (sm * mal * ch.shadow_mult * evc_dot * hit * (1 + IMPDRAINS[ch.t('ImprovedDrains')])
                * (1 + .04 * ch.t('SoulSiphon') * n_affl()))

    def spend(name, cost):
        st['mana'] -= cost
        S['mana_spent'] += cost
        S['casts'][name] = S['casts'].get(name, 0) + 1

    def life_tap():
        amt = lt[1] + ch.spirit
        st['php'] -= amt
        S['hp_spent'] += amt
        gain = amt * (1 + .10 * ch.t('ImprovedLifeTap'))
        st['mana'] += gain
        S['lt_mana'] += gain
        S['casts']['LifeTap'] = S['casts'].get('LifeTap', 0) + 1

    def apply_dot(name):
        if name == 'Corruption':
            dots[name] = dict(next=st['t'] + 3, left=corr[2], per=corr[1] + CORR_SP * sp, period=3)
        elif name == 'BoA':
            amp = 1.0
            if st['amp']:
                amp, st['amp'] = 1.5, False
            dots[name] = dict(next=st['t'] + 2, left=12, per=(boa[1] + BOA_SP * sp) * amp, period=2, n=0)
        elif name == 'SiphonLife':
            dots[name] = dict(next=st['t'] + 3, left=10, per=sl[1] + SL_SP * sp, period=3)

    while st['hp'] > 0 and st['t'] < max_time:
        t = st['t']
        for name in list(dots):
            d = dots[name]
            if t >= d['next'] - 1e-9:
                per = d['per']
                if 'n' in d:
                    d['n'] += 1
                    per *= 0.5 if d['n'] <= 4 else (1.0 if d['n'] <= 8 else 1.5)
                x = per * dot_mult(name)
                dmg(name, x)
                if name == 'SiphonLife':
                    heal(x)
                if name == 'Corruption' and nf:
                    st['nfc'] = st.get('nfc', 0) + nf
                d['left'] -= 1
                d['next'] += d['period']
                if d['left'] <= 0:
                    del dots[name]
        c = chan[0]
        if c and t >= c['next'] - 1e-9:
            x = c['per'] * drain_mult()
            dmg(c['name'], x)
            if c['name'] == 'DrainLife':
                heal(x)
            if nf:
                st['nfc'] = st.get('nfc', 0) + nf
            c['left'] -= 1
            c['next'] += c['period']
            if c['left'] <= 0:
                chan[0] = None
        k = cast[0]
        if k and t >= k['end'] - 1e-9:
            k['fn']()
            cast[0] = None
        dmg('Pet', ch.pet_dps * DT)
        st['php'] -= ch.mob_dps * ch.taken_frac * DT
        S['hp_taken'] = S.get('hp_taken', 0) + ch.mob_dps * ch.taken_frac * DT
        if ch.felhunter_sac:
            heal(0.03 * ch.max_hp / 4 * DT)
        if ch.voidwalker_sac:
            st['mana'] = min(ch.max_mana * 2, st['mana'] + 0.02 * ch.max_mana / 4 * DT)
        busy = chan[0] is not None or cast[0] is not None
        if st.get('wand') and not busy:
            dmg('Wand', ch.wand_dps * DT * hit)
        if not busy and t >= st.get('gcd', 0) - 1e-9 and st['hp'] > 0:
            a = choose(policy, ch, dots, st, mob_hp, corr, boa, sl, dl, ds, sb, wrack_ok)
            if st.get('nfc', 0) >= 1 and st['mana'] >= sb[3] and a not in ('Corruption', 'BoA', 'SiphonLife'):
                a = 'NightfallSB'
            if a != 'Wand':
                st['wand'] = False
                st['gcd'] = t + 1.5
            if a == 'LifeTap':
                life_tap()
            elif a == 'Corruption':
                spend(a, corr[3])
                ct = max(0.0, 2.0 - 0.4 * ch.t('ImprovedCorruption'))
                if ct > 0:
                    cast[0] = dict(end=t + ct, fn=lambda: apply_dot('Corruption'))
                else:
                    apply_dot('Corruption')
            elif a == 'BoA':
                spend(a, boa[2]); apply_dot('BoA')
            elif a == 'SiphonLife':
                spend(a, sl[2]); apply_dot('SiphonLife')
            elif a == 'DrainLife':
                spend(a, dl[2]); chan[0] = dict(name='DrainLife', next=t + 1, left=5, period=1, per=dl[1] + DL_SP * sp)
            elif a == 'DrainSoul':
                spend(a, ds[2]); chan[0] = dict(name='DrainSoul', next=t + 3, left=5, period=3, per=ds[1] + DS_SP * sp)
            elif a == 'Wrack':
                spend(a, WRACK[2]); chan[0] = dict(name='Wrack', next=t + 1, left=6, period=1, per=WRACK[1] + WRACK_SP * sp)
                st['wrack_until'] = t + 6
            elif a == 'ShadowBolt':
                spend(a, sb[3])
                ct = max(1.5, sb[2] - 0.1 * ch.t('Bane'))
                cast[0] = dict(end=t + ct, fn=lambda: dmg('ShadowBolt', sb_hit))
            elif a == 'NightfallSB':
                st['nfc'] -= 1
                spend('ShadowBolt', sb[3])
                dmg('Nightfall', sb_hit)
            elif a == 'Wand':
                st['wand'] = True
        st['t'] += DT
    S['ttk'] = st['t']
    S['end_mana'] = st['mana']
    S['end_hp'] = st['php']
    # net resource change in mana-equivalents (1 health = 1.2 mana via tapped Life Tap w/ ILT 2/2)
    S['net_mana'] = st['mana'] - ch.max_mana
    S['net_hp'] = st['php'] - ch.max_hp
    return S


def choose(policy, ch, dots, st, mob_hp, corr, boa, sl, dl, ds, sb, wrack_ok):
    frac = st['hp'] / mob_hp
    lt_gain = (rank(LT, ch.level)[1] + ch.spirit) * (1 + .10 * ch.t('ImprovedLifeTap'))
    if (st['php'] - (rank(LT, ch.level)[1] + ch.spirit) > policy.get('tap_above', 0.75) * ch.max_hp
            and st['mana'] + lt_gain <= ch.max_mana):
        return 'LifeTap'
    lt_ok = st['php'] > policy.get('lt_hp_floor', 0.35) * ch.max_hp
    mana = st['mana']
    for step in policy['prio']:
        cost = None
        if step == 'Corruption':
            if 'Corruption' in dots or frac <= policy.get('corr_min', 0.15):
                continue
            cost = corr[3]
        elif step == 'BoA':
            if not boa or 'BoA' in dots or frac <= policy.get('boa_min', 0.5):
                continue
            cost = boa[2]
        elif step == 'SiphonLife':
            if not sl or 'SiphonLife' in dots or frac <= policy.get('sl_min', 0.4):
                continue
            cost = sl[2]
        elif step == 'Wrack':
            if not wrack_ok or frac <= 0.25 or len(dots) < 2:
                continue
            cost = WRACK[2]
        elif step == 'DrainLife':
            if not dl:
                continue
            cost = dl[2]
        elif step == 'DrainSoul':
            if frac > policy.get('ds_below', 0.25):
                continue
            cost = ds[2]
        elif step == 'ShadowBolt':
            cost = sb[3]
        elif step == 'Wand':
            return 'Wand'
        if mana >= cost:
            return step
        if lt_ok:
            return 'LifeTap'
        return 'Wand'
    return 'Wand'


# ---------------------------------------------------------------- per-kill economics
def seconds_per_kill(ch, mob_hp, policy, travel=8.0, rest_rate=None, regen_rate=None):
    """TTK + travel + time to rest back the net resource deficit.

    Resource is counted in mana-equivalents: 1 health = (1 + 0.1*ILT) mana, because
    Life Tap converts it at that rate. Rest (eat + drink together) restores
    rest_rate mana-eq per second. Natural regen during travel is regen_rate.
    """
    L = ch.level
    k = 1 + .10 * ch.t('ImprovedLifeTap')
    if rest_rate is None:
        rest_rate = 2.2 * L + 1.2 * L * k   # Classic-style level-appropriate water + food, assumption
    if regen_rate is None:
        regen_rate = (8 + ch.spirit / 4) / 2 + ch.spirit / 5 * k * 0.5  # out-of-combat, rough Classic shape
    s = simulate(ch, mob_hp, policy)
    net = s['net_mana'] + k * s['net_hp'] + regen_rate * travel
    rest = max(0.0, -net) / rest_rate
    s['rest'] = rest
    s['spk'] = s['ttk'] + travel + rest
    return s
