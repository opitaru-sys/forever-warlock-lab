"""Multi-mob leveling model (v8, phase 3). A SEPARATE model from the single-mob sim in leveling_sim.py.

It asks one question: does fighting 2 to 5 mobs at once beat killing them one at a time, and when does it kill
you. Spell ranks, talent multipliers, mana costs, cast times and the rest model come from leveling_sim.py
(fight_consts, rest_model); the character (health, mana, pet damage, mob damage) from character.make_char. New
here: Rain of Fire, Hellfire, Fear, Bane of Havoc, the Voidwalker's taunts and its health. Every assumption that
the single-mob model does not already make is a field of Setup or a named constant below, labelled M1 to M17 as
in the results file, so the analysis can show its sensitivity.

Same method as the single-mob sim: deterministic expected values in 0.02 s steps (hit and crit folded into every
hit and tick). A pull of n mobs with the same health starts with you at full health and mana; it ends when every
mob is dead, when your expected health reaches zero (you died: the pull size fails) or after 300 s (stalled).

Not modelled here, all small single-target gains of the single-mob sim: Curse of the Elements as a pull opener
(it is a spread curse instead), Amplify Curse, Death Coil, Drain Soul / Shadowburn / Soul Fire finishers, Wrack,
Conflagrate, Incinerate, Improved Shadow Bolt and Shadow and Flame. Their absence makes pulls look a little
worse than they are. Health stones, potions, bandages and Health Funnel are not modelled either.
"""
from dataclasses import dataclass

import leveling_sim as ls
from leveling_sim import (rank, dd_avg, fight_consts, rest_model, rest_seconds, AFF_DOTS, NO_NIGHTFALL, IMPDRAINS,
                          CORR_SP, BOA_SP, SL_SP, DL_SP)
from character import taken_scale

DT = ls.DT

# ---------------------------------------------------------------- spell data new to this model
# Rain of Fire. The channel spells (5740, 6219, 11677, 11678) carry only a dummy effect with coefficient 0.03; the
# damage sits on the triggered spells 1282380, 1282383, 1282384, 1282385 (ElliotWood gen.go RainOfFireTriggered):
# base points 40/91/149/220 a tick plus 0.3 to 0.6 a level up to MaxLevel, 0.083 spell power A TICK, 4 ticks, one
# every 2 sec. Wowhead's "4 x 41.5" is the rank-1 tick at its MaxLevel 25 (40 + 5 x 0.3).
ROF = [(20, 40, 295, .3, 25), (34, 91, 605, .4, 39), (46, 149, 885, .5, 51),
       (58, 220, 1185, .6, 63)]                 # lvl, avg tick, mana, per lvl, MaxLevel (dd_avg row layout)
ROF_SP, ROF_TICKS, ROF_PERIOD = 0.083, 4, 2.0
# Hellfire. Enemy damage: HellfireEffect 5857, 11681, 11682 (82/137/206 a tick, 0.022 spell power a tick). The
# channel's own effect 1 burns you for the same base points every second (Wowhead: self damage equals enemy damage).
HELLFIRE = [(30, 82, 645, .4, 40), (42, 137, 975, .5, 52), (54, 206, 1300, .7, 64)]
HELLFIRE_SP, HELLFIRE_TICKS, HELLFIRE_PERIOD = 0.022, 15, 1.0
FEAR = [(8, 10.0), (32, 15.0), (56, 20.0)]      # lvl, duration ("up to", Wowhead Forever); 1.5 s cast
FEAR_CAST, FEAR_BASE_SHARE = 1.5, 0.15          # costs 15% of base mana
SUFFERING = (24, 120.0)                          # Voidwalker Suffering 17735: taunts all within 10 yd, 2 min cooldown
HAVOC_SHARE = 0.15                               # Bane of Havoc: 15% of your damage to other targets copied to it

# ---------------------------------------------------------------- named assumptions (constants)
BASE_MANA_SHARE = 0.4    # M10: base mana (for Fear's 15%) is 40% of the model's no-talent max mana
HAVOC_COST_SHARE = 0.10  # M11: Bane of Havoc costs 10% of base mana (not in the data we have)
HELD_FRAC = 0.10         # a mob the Voidwalker holds hits you for 10%: the single-mob model's Voidwalker taken_frac
SOUL_LINK_SHARE = 0.30   # Soul Link: 30% of the damage you take goes to the demon
DE_HEAL = (0.0, 0.08, 0.15)   # M17: Demonic Energies, your spells heal the demon for 8/15% of their damage
LIVE = ('pet', 'you')    # a mob that fights: held by the Voidwalker, or hitting you. Others: 'fear', 'dead'
NO_NF = NO_NIGHTFALL + ('Fear', 'Havoc', 'RoF', 'Hellfire')   # a Nightfall bolt never replaces these


@dataclass(frozen=True)
class Setup:
    """The assumptions this model adds. Defaults are the headline run; the analysis varies one at a time."""
    hold: str = 'one'         # M1 Voidwalker threat: 'one' (Torment: one mob at a time), 'suffering' (from 24 it
    #                           holds the whole pull when Suffering is ready, see suffering_mix), 'all' (always)
    travel0: float = 8.0      # M2 pull travel, sec: travel0 + travel_per x (n - 1), no damage taken while gathering
    travel_per: float = 6.0
    fear_mult: float = 1.0    # M3 share of Fear's full duration it lasts (no early breaks, no adds pulled)
    vw_hp: float = 1.0        # M4 Voidwalker health as a multiple of your base health (0: it never dies)
    vw_taken: float = 0.7     # M5 a mob's damage to the Voidwalker as a share of its damage to you (armor)
    mob_dps: float = 1.0      # M6 multiple of the single-mob model's mob damage (0.035 x level^2 a second)
    rest: str = 'pooled'      # M7 'pooled' (seconds_per_kill's model) or 'eat' (health comes back only by eating)
    margin: float = 0.0       # M8 lowest expected health allowed, share of max health (0: survive at all)
    aoe_crit: bool = True     # M9 Rain of Fire and Hellfire ticks crit like Immolate ticks (Ruin applies)


def base_health(L):
    """The model's no-talent health (character.make_char), the Voidwalker's health scale (M4)."""
    return 20 + 28 * L + 0.4 * L * L


def base_mana(L):
    return BASE_MANA_SHARE * (20 + 25 * L + 0.45 * L * L)


def travel(su, n):
    return su.travel0 + su.travel_per * (n - 1)


def aoe_consts(ch, k, crit=True):
    """Rain of Fire and Hellfire at this level: expected damage a tick to each mob before the school multiplier,
    mana, ticks, and Hellfire's burn on you (M14: base points only, as the ElliotWood sim removes it). They are
    Destruction Fire spells: Agonizing Flames, Cataclysm, Destruction hit and (M9) crit with Ruin. Malediction
    does not apply (M15: the damage is a triggered direct hit, not a periodic aura)."""
    L, mode, sp = ch.level, ch.dd_mode, k['sp']
    mult = k['af'] * (k['evc_fd'] if crit else 1.0) * k['hit_d']
    out = {}
    r = rank(ROF, L)
    if r:
        out['RoF'] = dict(per=(dd_avg(r, L, mode) + ROF_SP * sp) * mult, cost=r[2] * k['cata'], ticks=ROF_TICKS,
                          period=ROF_PERIOD, burn=0.0)
    h = rank(HELLFIRE, L)
    if h:
        out['Hellfire'] = dict(per=(dd_avg(h, L, mode) + HELLFIRE_SP * sp) * mult, cost=h[2] * k['cata'],
                               ticks=HELLFIRE_TICKS, period=HELLFIRE_PERIOD, burn=dd_avg(h, L, mode))
    return out


def castable(step, ch, k, aoe):
    """Whether a policy step exists at this level with these talents."""
    have = dict(Corruption=k['corr'], BoA=k['boa'], SiphonLife=k['sl'], Immolate=k['imm'], CoE=k['coe'],
                DrainLife=k['dl'], SearingPain=k['sear'], Fear=rank(FEAR, ch.level), Havoc=ch.t('BaneOfHavoc'),
                RoF='RoF' in aoe, Hellfire='Hellfire' in aoe, ShadowBolt=True, Wand=True)
    return bool(have.get(step))


class Mob:
    __slots__ = ('hp', 'top', 'state', 'dots', 'curse', 'fear_end')

    def __init__(self, hp):
        self.hp, self.top, self.state = hp, hp, 'you'
        self.dots, self.curse, self.fear_end = {}, None, 0.0


class Fight:
    """One pull of n mobs with the same health.

    Policy keys: prio (steps in priority order: Fear, Havoc, Corruption, BoA, CoE, SiphonLife, Immolate, Hellfire,
    RoF, DrainLife, ShadowBolt, SearingPain, Wand), spread (DoTs go on every mob, not only the focus), and the
    single-mob thresholds (tap_above, lt_hp_floor, corr_min, boa_min, sl_min, imm_min) plus aoe_min (mobs alive for
    an area spell), hf_start and hf_stop (your health share to start and to stop Hellfire).
    The focus is the mob you drain, wand or bolt: the lowest-health mob hitting you, else the lowest held one."""

    def __init__(self, ch, pet, n, hp_each, pol, su):
        self.ch, self.pol, self.su, self.T = ch, pol, su, ch.t
        self.k = k = fight_consts(ch, dict(prio=list(pol['prio'])))
        self.aoe = aoe_consts(ch, k, su.aoe_crit)
        self.prio = [s for s in pol['prio'] if castable(s, ch, k, self.aoe)]
        self.mobs = [Mob(hp_each) for _ in range(n)]
        self.alive = n
        self.vw = pet == 'voidwalker'
        L = ch.level
        self.hold_all = self.vw and n > 1 and (su.hold == 'all' or (su.hold == 'suffering' and L >= SUFFERING[0]))
        md = .02 * self.T('MasterDemonologist') if self.vw else 0.0   # M16: less physical taken, you and the demon
        self.ts_pet, self.ts_nopet = taken_scale(ch.talents, pet) * (1 - md), taken_scale(ch.talents, 'none')
        self.ts = self.ts_pet
        self.sl = SOUL_LINK_SHARE if self.T('SoulLink') and pet != 'none' else 0.0
        self.de = DE_HEAL[self.T('DemonicEnergies')] if self.vw else 0.0
        vw_top = su.vw_hp * base_health(L) * (1 + .05 * self.T('FelVitality'))
        self.vw_top = self.vw_hp = vw_top if su.vw_hp > 0 else float('inf')
        self.vw_mult = su.vw_taken * (1 - md)
        self.pet_alive, self.mob_dps = True, ch.mob_dps * su.mob_dps
        self.fear_row = rank(FEAR, L)
        self.fear_cost = FEAR_BASE_SHARE * base_mana(L) / k['hit']       # a resisted Fear is cast again
        self.php, self.mana, self.min_php, self.vw_min = ch.max_hp, ch.max_mana, ch.max_hp, self.vw_hp
        self.t = self.gcd = self.nfc = 0.0
        self.wand_on, self.chan, self.cast, self.havoc, self.died = False, None, None, None, False
        self.S = dict(casts={}, dmg={}, healed=0.0, hp_taken=0.0, burn=0.0, pet_died_at=None)
        if self.vw:
            for m in (self.mobs if self.hold_all else self.mobs[:1]):
                m.state = 'pet'

    # ------------------------------------------------ multipliers (the single-mob sim's, per mob)
    def coe(self, m):
        return self.k['coe_mult'] if m.curse == 'CoE' else 1.0

    def shadow(self, m):
        return self.k['sm'] * self.ch.shadow_mult * self.coe(m)

    def fire(self, m):
        return self.ch.fire_mult * self.coe(m)

    def dot_mult(self, name, m):
        k, T = self.k, self.T
        x = self.shadow(m) * k['mal'] * k['evc_dot'] * k['hit']
        if name == 'Corruption':
            x *= 1 + .02 * T('ImprovedCorruption')
        if name == 'BoA':
            x *= 1 + .05 * T('ImprovedBoA')
        return x

    def drain_mult(self, m):
        k, T = self.k, self.T
        n_affl = min(3, sum(1 for d in AFF_DOTS if d in m.dots))
        return (self.shadow(m) * k['mal'] * k['evc_dot'] * k['hit'] * (1 + IMPDRAINS[T('ImprovedDrains')])
                * (1 + .04 * T('SoulSiphon') * n_affl))

    # ------------------------------------------------ damage, healing, deaths
    def hit(self, m, name, x, spell=True):
        if m.state == 'dead':
            return
        m.hp -= x
        dmg = self.S['dmg']
        dmg[name] = dmg.get(name, 0.0) + x
        if spell and self.de and self.pet_alive:
            self.vw_hp = min(self.vw_top, self.vw_hp + self.de * x)
        h = self.havoc
        if h is not None and h is not m and name != 'Pet' and h.state != 'dead':
            h.hp -= HAVOC_SHARE * x
            dmg['Havoc'] = dmg.get('Havoc', 0.0) + HAVOC_SHARE * x
            if h.hp <= 0:
                self.kill(h)
        if m.hp <= 0:
            self.kill(m)

    def kill(self, m):
        m.state, m.hp = 'dead', min(m.hp, 0.0)
        m.dots.clear()
        self.alive -= 1
        if self.havoc is m:
            self.havoc = None
        if self.chan is not None and self.chan['tgt'] is m:
            self.chan = None

    def heal(self, x):
        self.php = min(self.ch.max_hp, self.php + x)
        self.S['healed'] += x

    def pet_dies(self):
        self.pet_alive, self.S['pet_died_at'] = False, self.t
        self.ts = self.ts_nopet
        for m in self.mobs:
            if m.state == 'pet':
                m.state = 'you'

    # ------------------------------------------------ targets
    def focus(self):
        best = None
        for want in LIVE[::-1]:              # 'you' first, then 'pet'
            for m in self.mobs:
                if m.state == want and (best is None or m.hp < best.hp):
                    best = m
            if best is not None:
                return best
        return None

    def pet_target(self):
        if self.vw:
            held = [m for m in self.mobs if m.state == 'pet']
            return min(held, key=lambda m: m.hp) if held else None
        return self.focus()

    def n_live(self):
        return sum(1 for m in self.mobs if m.state in LIVE)

    def dot_target(self, step):
        k, pol = self.k, self.pol
        lim = dict(Corruption=pol.get('corr_min', 0.15), BoA=pol.get('boa_min', 0.5), CoE=pol.get('boa_min', 0.5),
                   SiphonLife=pol.get('sl_min', 0.4), Immolate=pol.get('imm_min', 0.2))[step]
        f = self.focus()
        if f is None:
            return None
        order = [f]
        if pol.get('spread'):
            order += sorted((m for m in self.mobs if m.state in LIVE and m is not f), key=lambda m: -m.hp)
        curse = step in ('BoA', 'CoE')
        for m in order:
            if (m.curse is not None) if curse else (step in m.dots):
                continue
            if m.hp / m.top > lim:
                return m
        return None

    def fear_target(self):
        """Fear one untouched mob (no damage, DoT or curse on it: damage breaks Fear) that is hitting you, while at
        least one other mob fights. Never the mob your pet attacks."""
        if not self.fear_row or any(m.state == 'fear' for m in self.mobs) or self.n_live() < 2:
            return None
        excl = self.pet_target()
        cands = [m for m in self.mobs if m.state == 'you' and m.hp >= m.top - 1e-9 and not m.dots
                 and m.curse is None and m is not excl]
        return cands[-1] if cands else None

    def havoc_target(self):
        if self.havoc is not None or self.n_live() < 2:
            return None
        cands = [m for m in self.mobs if m.state in LIVE and m.curse is None]
        if not cands:
            return None
        held = [m for m in cands if m.state == 'pet' and not self.hold_all]
        pool = held or cands
        return max(reversed(pool), key=lambda m: m.hp)      # the one that dies last; ties: the last mob

    def target(self, step):
        """The mob a step would go on, or None when it is not ready (mana aside)."""
        if step in ('Wand', 'ShadowBolt', 'DrainLife', 'SearingPain'):
            return self.focus()
        if step in ('RoF', 'Hellfire'):
            if self.n_live() < self.pol.get('aoe_min', 2):
                return None
            if step == 'Hellfire' and self.php < self.pol.get('hf_start', 0.6) * self.ch.max_hp:
                return None
            return self.focus()
        if step == 'Fear':
            return self.fear_target()
        if step == 'Havoc':
            return self.havoc_target()
        return self.dot_target(step)

    # ------------------------------------------------ the player
    def cost(self, step):
        if step in self.aoe:
            return self.aoe[step]['cost']
        if step == 'Fear':
            return self.fear_cost
        if step == 'Havoc':
            return HAVOC_COST_SHARE * base_mana(self.ch.level)
        return self.k['cost'][step]

    def choose(self):
        """leveling_sim.choose over several mobs: Life Tap when healthy and short of mana, then the first ready step
        you can pay for; out of mana, Life Tap above lt_hp_floor, else the wand. drain_below (multi-mob only): under
        that health share, Drain Life on the focus comes before everything else."""
        ch, k, pol = self.ch, self.k, self.pol
        if (self.php - k['lt_amt'] > pol.get('tap_above', 0.75) * ch.max_hp
                and self.mana + k['lt_amt'] * k['ilt'] <= ch.max_mana):
            return 'LifeTap', None
        low = pol.get('drain_below')
        if low and self.php < low * ch.max_hp and 'DrainLife' in self.prio and self.mana >= self.cost('DrainLife'):
            m = self.focus()
            if m is not None:
                return 'DrainLife', m
        lt_ok = self.php > pol.get('lt_hp_floor', 0.35) * ch.max_hp
        for step in self.prio:
            m = self.target(step)
            if m is None:
                continue
            if step == 'Wand' or self.mana >= self.cost(step):
                return step, m
            return ('LifeTap', None) if lt_ok else ('Wand', self.focus())
        return 'Wand', self.focus()

    def act(self, a, m):
        t, k, S = self.t, self.k, self.S
        if a != 'Wand':
            self.wand_on, self.gcd = False, t + 1.5
        if a == 'LifeTap':
            self.php -= k['lt_amt']
            self.mana += k['lt_amt'] * k['ilt']
        elif a == 'Wand':
            self.wand_on = True
            return
        elif a == 'NightfallSB':
            self.nfc -= 1
            self.mana -= k['cost']['ShadowBolt']
            self.hit(m, 'Nightfall', k['base']['ShadowBolt'] * self.shadow(m))
        else:
            self.mana -= self.cost(a)
            self.start(a, m)
        S['casts'][a] = S['casts'].get(a, 0) + 1

    def start(self, a, m):
        t, k, sp = self.t, self.k, self.k['sp']
        if a == 'DrainLife':
            self.chan = dict(name=a, tgt=m, next=t + 1, left=5, period=1, per=k['dl'][1] + DL_SP * sp, burn=0.0)
        elif a in ('RoF', 'Hellfire'):
            x = self.aoe[a]
            self.chan = dict(name=a, tgt=None, next=t + x['period'], left=x['ticks'], period=x['period'],
                             per=x['per'], burn=x['burn'])
        elif a in ('BoA', 'SiphonLife'):
            self.apply_dot(a, m)
        elif a == 'CoE':
            m.curse = 'CoE'
        elif a == 'Havoc':
            m.curse, self.havoc = 'Havoc', m
        elif a == 'Fear':
            self.cast = dict(end=t + FEAR_CAST, step=a, tgt=m)
        elif k['ct'][a] > 0:
            self.cast = dict(end=t + k['ct'][a], step=a, tgt=m)
        else:
            self.land(a, m)

    def land(self, a, m):
        k = self.k
        if m.state == 'dead':
            return                              # the target died during the cast: the mana is gone
        if a == 'Corruption':
            self.apply_dot(a, m)
        elif a == 'Immolate':
            self.hit(m, a, k['base'][a] * self.fire(m))
            if m.state != 'dead':
                self.apply_dot(a, m)
        elif a == 'ShadowBolt':
            self.hit(m, a, k['base'][a] * self.shadow(m))
        elif a == 'SearingPain':
            self.hit(m, a, k['base'][a] * self.fire(m))
        elif a == 'Fear' and m.state in LIVE and not m.dots and m.curse is None:
            m.state, m.fear_end = 'fear', self.t + self.fear_row[1] * self.su.fear_mult

    def apply_dot(self, name, m):
        t, k, sp = self.t, self.k, self.k['sp']
        if name == 'Corruption':
            m.dots[name] = dict(next=t + 3, left=k['corr'][2], per=k['corr'][1] + CORR_SP * sp, period=3)
        elif name == 'BoA':
            m.dots[name] = dict(next=t + 2, left=12, per=k['boa'][1] + BOA_SP * sp, period=2, n=0)
            m.curse = 'BoA'
        elif name == 'SiphonLife':
            m.dots[name] = dict(next=t + 3, left=10, per=k['sl'][1] + SL_SP * sp, period=3)
        elif name == 'Immolate':
            m.dots[name] = dict(next=t + 3, left=5, per=k['base']['ImmolateTick'], period=3)

    # ------------------------------------------------ one time step
    def tick_dots(self, t):
        nf = self.k['nf']
        for m in self.mobs:
            for name in list(m.dots):
                d = m.dots[name]
                if t < d['next'] - 1e-9:
                    continue
                per = d['per']
                if 'n' in d:                    # Bane of Agony ramp: 0.5x, 1.0x, 1.5x in thirds
                    d['n'] += 1
                    per *= 0.5 if d['n'] <= 4 else (1.0 if d['n'] <= 8 else 1.5)
                x = per * (self.fire(m) if name == 'Immolate' else self.dot_mult(name, m))
                self.hit(m, name, x)
                if name == 'SiphonLife':
                    self.heal(x)
                if name == 'Corruption' and nf:
                    self.nfc += nf
                if m.state == 'dead':
                    break
                d['left'] -= 1
                d['next'] += d['period']
                if d['left'] <= 0:
                    del m.dots[name]
                    if name == 'BoA':
                        m.curse = None

    def tick_channel(self, t):
        c = self.chan
        if c is None or t < c['next'] - 1e-9:
            return
        if c['name'] == 'DrainLife':
            x = c['per'] * self.drain_mult(c['tgt'])
            self.hit(c['tgt'], 'DrainLife', x)
            self.heal(x)
            if self.k['nf']:
                self.nfc += self.k['nf']
        else:
            for m in self.mobs:
                if m.state in LIVE:
                    self.hit(m, c['name'], c['per'] * self.fire(m))
            self.php -= c['burn']
            self.S['burn'] += c['burn']
        if self.chan is not c:                  # the drained mob died
            return
        c['left'] -= 1
        c['next'] += c['period']
        stop = self.alive == 0 or self.n_live() == 0
        if c['name'] == 'Hellfire' and self.php < self.pol.get('hf_stop', 0.35) * self.ch.max_hp:
            stop = True
        if c['left'] <= 0 or stop:
            self.chan = None

    def take_hits(self):
        you = sum(1 for m in self.mobs if m.state == 'you')
        held = sum(1 for m in self.mobs if m.state == 'pet')
        raw = self.mob_dps * DT * (you + HELD_FRAC * held)
        taken = raw * self.ts
        self.php -= taken
        self.S['hp_taken'] += taken
        if self.vw and self.pet_alive:
            self.vw_hp -= self.mob_dps * DT * held * self.vw_mult + raw * self.sl
            self.vw_min = min(self.vw_min, self.vw_hp)
            if self.vw_hp <= 0:
                self.pet_dies()

    def update_mobs(self, t):
        """Fear runs out; the last feared mob is let go when nothing else fights; the Voidwalker takes a free mob
        (Torment) when it holds none, or every free mob when it holds the pull."""
        for m in self.mobs:
            if m.state == 'fear' and t >= m.fear_end - 1e-9:
                m.state = 'you'
        if self.n_live() == 0:
            for m in self.mobs:
                if m.state == 'fear':
                    m.state = 'you'
        if not (self.vw and self.pet_alive):
            return
        free = [m for m in self.mobs if m.state == 'you']
        if self.hold_all:
            for m in free:
                m.state = 'pet'
        elif free and not any(m.state == 'pet' for m in self.mobs):
            max(reversed(free), key=lambda m: m.hp).state = 'pet'

    def step(self):
        t, ch = self.t, self.ch
        self.tick_dots(t)
        self.tick_channel(t)
        c = self.cast
        if c is not None and t >= c['end'] - 1e-9:
            self.cast = None
            self.land(c['step'], c['tgt'])
        if self.pet_alive and ch.pet_dps > 0:
            m = self.pet_target()
            if m is not None:
                self.hit(m, 'Pet', ch.pet_dps * DT, spell=False)
        self.take_hits()
        if ch.felhunter_sac:
            self.heal(0.03 * ch.max_hp / 4 * DT)
        if ch.voidwalker_sac:
            self.mana = min(ch.max_mana * 2, self.mana + 0.02 * ch.max_mana / 4 * DT)
        busy = self.chan is not None or self.cast is not None
        if self.wand_on and not busy:
            m = self.focus()
            if m is not None:
                self.hit(m, 'Wand', ch.wand_dps * DT * self.k['hit'] * self.coe(m), spell=False)
        self.update_mobs(t)
        if not busy and t >= self.gcd - 1e-9 and self.alive > 0 and self.php > 0:
            a, m = self.choose()
            if self.nfc >= 1 and self.mana >= self.k['cost']['ShadowBolt'] and a not in NO_NF:
                a, m = 'NightfallSB', self.focus()
            if m is not None or a == 'LifeTap':
                self.act(a, m)
        self.min_php = min(self.min_php, self.php)
        self.t += DT

    def run(self, max_time=300.0):
        while self.alive > 0 and self.t < max_time:
            self.step()
            if self.php <= 0:
                self.died = True
                break
        ch = self.ch
        return dict(self.S, ttk=self.t, died=self.died, stalled=self.alive > 0 and not self.died,
                    min_hp=self.min_php / ch.max_hp, net_mana=self.mana - ch.max_mana, net_hp=self.php - ch.max_hp,
                    pet_died=not self.pet_alive, vw_min=(self.vw_min / self.vw_top) if self.vw else None,
                    hold_all=self.hold_all)


# ---------------------------------------------------------------- per-kill economics
def eat_floor(ch, net_hp, trav):
    """M7 'eat': health comes back only by eating (1.2 x level a second in the rest model) plus out-of-combat
    health regen while walking; mana cannot be turned back into health. The pooled model is exact whenever
    drinking takes longer than eating, so this only matters when a pull costs mostly health."""
    walk = ch.spirit / 5 * 0.5 * trav
    return max(0.0, -net_hp - walk) / (1.2 * ch.level)


def pull(ch, pet, n, hp_each, pol, su=Setup()):
    """One pull: the fight, then seconds per kill = (fight + pull travel + rest) / n with seconds_per_kill's rest
    model. A pull the Voidwalker holds with Suffering also has to fit its cooldown: see suffering_mix."""
    s = Fight(ch, pet, n, hp_each, pol, su).run()
    trav = travel(su, n)
    k, _drink, rest_rate, _regen, regen_rate = rest_model(ch)
    net = s['net_mana'] + k * s['net_hp'] + regen_rate * trav
    rest = rest_seconds(max(0.0, -net), rest_rate)
    if su.rest == 'eat':
        rest = max(rest, eat_floor(ch, s['net_hp'], trav))
    cycle = s['ttk'] + trav + rest
    ok = not s['died'] and not s['stalled'] and s['min_hp'] > su.margin
    s.update(rest=rest, travel=trav, cycle=cycle, spk=cycle / n if ok else float('inf'), safe=ok)
    return s


def suffering_mix(cs, co, n, cd=SUFFERING[1]):
    """M1 'suffering': Suffering holds the whole pull but is ready once every 2 min. A block is one Suffering pull
    (cycle cs) and then m pulls the Voidwalker holds one mob at a time (cycle co; inf when that pull size kills you),
    waiting for the cooldown when the block is shorter. Returns (seconds per kill, m) for the best m, m = -1 when
    Torment-only pulls alone are faster."""
    inf = float('inf')
    best = (co / n, -1)
    if cs == inf:
        return best
    m = 0
    while True:
        block = cs + m * co
        best = min(best, (max(block, cd) / ((1 + m) * n), m))
        if block >= cd or co == inf:
            return best
        m += 1


def signature(pol, ch):
    """Policies whose castable steps and switches match run once (first name wins), like character.evaluate."""
    k = fight_consts(ch, dict(prio=list(pol['prio'])))
    aoe = aoe_consts(ch, k)
    steps = [s for s in pol['prio'] if castable(s, ch, k, aoe)]
    while steps and steps[-1] == 'Wand':
        steps.pop()
    keys = ('spread', 'lt_hp_floor', 'drain_below', 'hf_start', 'hf_stop')
    hf = 'Hellfire' in steps
    return tuple(steps), tuple(pol.get(x) for x in keys if hf or not x.startswith('hf'))


def best_pull(ch, pet, n, hp_mults, policies, su=Setup(), top=8):
    """The fastest SAFE policy for pulls of n: every distinct policy at mob health x1.0, then, fastest first, the safe
    ones at every multiple in hp_mults until `top` of them survive all of them (safe means surviving every one).
    Policies with the same outcome at x1.0 (a Fear step with nothing to fear, say) count once, the first name wins.
    Returns (name, averaged result) or (None, the least-bad result) when nothing is safe."""
    from character import mob_hp
    hp = mob_hp(ch.level)
    seen, first = set(), []
    for name, pol in policies.items():
        sig = signature(pol, ch)
        if sig in seen:
            continue
        seen.add(sig)
        first.append((name, pol, pull(ch, pet, n, hp, pol, su)))
    best, passed, outcomes = None, 0, set()
    for name, pol, r1 in sorted((r for r in first if r[2]['safe']), key=lambda r: r[2]['spk']):
        if passed >= top:
            break
        same = tuple(round(r1[x], 6) for x in ('spk', 'ttk', 'min_hp', 'net_mana', 'net_hp'))
        if same in outcomes:
            continue
        outcomes.add(same)
        rs = [r1 if m == 1.0 else pull(ch, pet, n, hp * m, pol, su) for m in hp_mults]
        if not all(r['safe'] for r in rs):
            continue
        passed += 1
        out = dict(rs[0])
        for key in ('spk', 'ttk', 'rest', 'cycle'):
            out[key] = sum(r[key] for r in rs) / len(rs)
        out['min_hp'] = min(r['min_hp'] for r in rs)
        if best is None or out['spk'] < best[1]['spk']:
            best = (name, out)
    if best is None:
        worst = max(first, key=lambda r: (r[2]['min_hp'], -r[2]['ttk']))
        return None, worst[2]
    return best
