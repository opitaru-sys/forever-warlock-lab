"""How much each race's racials speed up leveling (v8).

Run from the repo root: python analysis/race_leveling.py
The page planner's build, Voidwalker, SP 1.0 x level. Stat racials change the character and the best rotation is
found again (evaluate(), modifiers included, averaged over mob HP x0.8 to x1.2). Per-kill racials are expected
values added to that rotation's simulated fights at each mob HP:
- Human: Sword Specialization, +2% spell crit with a caster sword; The Human Spirit, +5% Spirit (Life Tap, regen).
- Gnome: Expansive Mind, +5% max mana; Eureka!, the pull's first 3 damaging spells +10% damage and -10% mana,
  2 min cooldown, so on (kill cycle / 120 s) of pulls.
- Orc: Blood Fury, +10% spell power for 15 s, 2 min cooldown, on the pull when ready.
- Troll: Beast Slaying, +5% of your damage to beasts; Rapid Regeneration, 50% max health over 6 s between pulls,
  3 min cooldown, so it replaces up to 6 s of eating on (kill cycle / 180 s) of pulls.
- Undead: Touch of the Grave, caster version (spell 1260201): each spell cast or wand shot that hits has a 10%
  chance to drain 5% of your max health from the target (damage and healing); Cannibalize, 35% health and mana over
  10 s from a humanoid or undead corpse, 2 min cooldown, in place of eating.
Assumptions: wand speed 1.5 s; mobs 40% beasts and 40% humanoid or undead; Touch of the Grave's damage shortens the
fight in proportion to the mob health it removes; racials used whenever they are ready.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "models"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import leveling_sim as ls
from character import make_char, mob_hp, POLICIES, HP_GRID
from leveling_paths import page_build, spk_many

WAND_SPEED = 1.5
BEASTS, HUMANOIDS = 0.4, 0.4
TRAVEL = 8.0
FINISH = {'Drain Soul finish': 'DrainSoul', 'Shadowburn finish': 'Shadowburn', 'Soul Fire finish': 'SoulFire'}


def policy_of(name, tal, cycle):
    """The policy dict behind an evaluate() rotation name (the cooldown shares taken from the kill cycle)."""
    base, *mods = name.split(' +')
    pol = dict(POLICIES[base])
    for m in mods:
        if m == 'Curse of the Elements':
            pol['coe'] = True
        elif m in FINISH:
            pol['fin'] = FINISH[m]
            pol['p_sf'] = min(1.0, cycle / (60 * (1 - .45 * tal.get('Decimation', 0))))
        elif m == 'Death Coil':
            pol['dc'], pol['p_dc'] = True, min(1.0, cycle / 120.0)
    if tal.get('AmplifyCurse') and 'BoA' in pol['prio']:
        pol['p_amp'] = min(1.0, cycle / 180.0)
    return pol


def fights(L, tal, name, cycle, mods):
    """seconds_per_kill for the rotation at each mob HP multiple, with Char fields set from mods."""
    out = []
    for m in HP_GRID:
        ch = make_char(L, tal, 1.0)
        for f, v in mods.items():
            setattr(ch, f, getattr(ch, f) * v)
        pol = policy_of(name, tal, cycle)
        s = ls.seconds_per_kill(ch, mob_hp(L) * m, pol)
        s.update(ch=ch, hp=mob_hp(L) * m, k=ls.fight_consts(ch, pol))
        out.append(s)
    return out


def rest_rate(L, tal):
    return 2.2 * L + 1.2 * L * (1 + .1 * tal.get('ImprovedLifeTap', 0))


def fast_rest(rest, rr, rate, secs, share):
    """Rest when a channel restores `rate` a second for up to `secs`, available on `share` of pulls."""
    d = rest * rr
    if rate <= rr or d <= 0:
        return rest
    with_it = d / rate if d <= secs * rate else secs + (d - secs * rate) / rr
    return share * with_it + (1 - share) * rest


def totg(s, L, tal):
    """(fight seconds, rest seconds) with Touch of the Grave on spell casts and wand shots."""
    ch, hit = s['ch'], s['k']['hit']
    casts = sum(v for n, v in s['casts'].items() if n != 'LifeTap')
    wand_s = s['dmg'].get('Wand', 0.0) / max(1e-9, ch.wand_dps * hit)
    d = 0.10 * hit * (casts + wand_s / WAND_SPEED) * 0.05 * ch.max_hp
    kk = 1 + .1 * tal.get('ImprovedLifeTap', 0)
    rr = rest_rate(L, tal)
    return s['ttk'] * (1 - d / s['hp']), max(0.0, s['rest'] * rr - kk * d) / rr


def eureka(s, L, tal, cycle):
    """(fight seconds, rest seconds) with Eureka! on the first 3 damaging spells of the pull."""
    first = [a for a in s['k']['prio'] if a in s['casts'] and a not in ('CoE', 'Wand')][:3]
    dmg3 = sum(s['dmg'].get(a, 0.0) / s['casts'][a] for a in first)
    mana3 = sum(s['k']['cost'][a] for a in first)
    p = min(1.0, cycle / 120.0)
    rr = rest_rate(L, tal)
    return s['ttk'] * (1 - 0.1 * p * dmg3 / s['hp']), max(0.0, s['rest'] * rr - 0.1 * p * mana3) / rr


def mean(xs):
    return sum(xs) / len(xs)


def race_levels(L):
    """Seconds per kill at level L for each race (and the no-racial baseline). Per-kill racials enter as the ratio
    between the adjusted and the plain simulated fights of the same rotation."""
    tal = page_build(L)
    base_n, base_s = spk_many([(L, tal, 1.0, dict(full=True))], procs=1)[0]
    cycle, ttk0 = base_s['spk'], base_s['ttk']
    bf = 1 + 0.10 * min(1.0, cycle / 120.0) * min(1.0, 15.0 / ttk0)
    variants = {
        'none': {},
        'Human, caster sword': {'crit': 1.4, 'spirit': 1.05},     # 0.05 crit x 1.4 = +2%
        'Human, no sword': {'spirit': 1.05},
        'Gnome': {'max_mana': 1.05},
        'Orc': {'sp': bf},
        'Troll, on beasts': {'shadow_mult': 1.05, 'fire_mult': 1.05, 'wand_dps': 1.05},
    }
    named = dict(zip(variants, spk_many([(L, tal, 1.0, dict(full=True, char_mult=v)) for v in variants.values()])))
    out = {race: s['spk'] for race, (n, s) in named.items()}
    rr, kk = rest_rate(L, tal), 1 + .1 * tal.get('ImprovedLifeTap', 0)

    def ratio(fs, adjusted):
        return mean(adjusted) / mean([s['spk'] for s in fs])
    gf = fights(L, tal, named['Gnome'][0], cycle, variants['Gnome'])
    out['Gnome'] *= ratio(gf, [a + TRAVEL + b for a, b in (eureka(s, L, tal, cycle) for s in gf)])
    fb = fights(L, tal, base_n, cycle, {})
    ch = fb[0]['ch']
    regen = 0.5 * ch.max_hp * kk / 6.0

    def troll(fs):
        return ratio(fs, [s['ttk'] + TRAVEL + fast_rest(s['rest'], rr, regen, 6.0, min(1.0, cycle / 180.0)) for s in fs])
    tb = fights(L, tal, named['Troll, on beasts'][0], cycle, variants['Troll, on beasts'])
    out['Troll, on beasts'] *= troll(tb)
    out['Troll'] = BEASTS * out['Troll, on beasts'] + (1 - BEASTS) * out['none'] * troll(fb)
    can = 0.35 * (ch.max_hp * kk + ch.max_mana) / 10.0
    tg = [totg(s, L, tal) for s in fb]
    hum = ratio(fb, [a + TRAVEL + fast_rest(b, rr, can, 10.0, min(1.0, cycle / 120.0)) for a, b in tg])
    other = ratio(fb, [a + TRAVEL + b for a, b in tg])
    out['Undead, humanoids'] = out['none'] * hum
    out['Undead'] = HUMANOIDS * out['none'] * hum + (1 - HUMANOIDS) * out['none'] * other
    return out


if __name__ == "__main__":
    levels = (20, 30, 40, 50, 60)
    rows = {L: race_levels(L) for L in levels}
    races = ['Human, caster sword', 'Human, no sword', 'Gnome', 'Orc', 'Troll', 'Troll, on beasts', 'Undead', 'Undead, humanoids']
    print('### Leveling speed by race, % faster than no racials (page planner build, Voidwalker, SP 1.0)\n')
    print('| L | no racials | ' + ' | '.join(races) + ' |')
    print('|---|---|' + '---|' * len(races))
    for L, r in rows.items():
        b = r['none']
        print(f'| {L} | {b:.2f} | ' + ' | '.join(f'{100 * (1 - r[x] / b):.1f}%' for x in races) + ' |')
    print('| mean 20-60 | | ' + ' | '.join(f'{sum(100 * (1 - rows[L][x] / rows[L]["none"]) for L in levels) / len(levels):.1f}%'
                                            for x in races) + ' |')
