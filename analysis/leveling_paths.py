import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "models"))

import leveling_sim as ls
from character import make_char, mob_hp, POLICIES, valid
def rep(*p):
    out = []
    for k, n in p: out += [k]*n
    return out
AFF_FIRST = rep(('ImprovedCorruption',5),('Suppression',3),('ImprovedDrains',3),('Malediction',5),('ImprovedBoA',2),('Pandemic',2),
                ('SiphonLife',1),('SoulSiphon',3),('Nightfall',2),('ShadowMastery',5),('Wrack',1),('Pandemic',1),('FelConcentration',3),('ImprovedLifeTap',2),
                ('DemonicEmbrace',5),('ImprovedVoidwalker',3),('FelVitality',3),('DemonicAegis',2))
# Affliction core to Soul Siphon first (21 pts, level 30), then Demonology to Demonic Knowledge (23 pts, level 53), then back to Affliction
DK_PATH = rep(('ImprovedCorruption',5),('Suppression',3),('ImprovedDrains',3),('Malediction',5),('ImprovedBoA',2),('Pandemic',2),
              ('SiphonLife',1),('SoulSiphon',3),
              ('DemonicEmbrace',5),('UnholyPower',5),('FelVitality',3),('ImprovedVoidwalker',3),('DemonicSacrifice',1),('MasterSummoner',2),('FelDomination',1),('DemonicKnowledge',3),
              ('Nightfall',2),('Pandemic',1),('ImprovedLifeTap',1))
# Demonology first to Demonic Knowledge (levels 10-32), then Affliction
DK_FIRST = rep(('ImprovedCorruption',5),('DemonicEmbrace',5),('UnholyPower',5),('FelVitality',3),('ImprovedVoidwalker',3),('DemonicSacrifice',1),('MasterSummoner',2),('FelDomination',1),('DemonicKnowledge',3),
               ('Suppression',3),('ImprovedDrains',3),('Malediction',5),('ImprovedBoA',2),('Pandemic',3),('SiphonLife',1),('SoulSiphon',3),('Nightfall',2),('ImprovedLifeTap',1))
def build(order, n):
    t = {}
    for k in order:
        if sum(t.values()) >= n: break
        t[k] = t.get(k,0)+1
        assert valid(t), (k, t)
    return t
def spk(L, t, sp=1.0):
    best = None
    for pn, p in POLICIES.items():
        s = ls.seconds_per_kill(make_char(L, t, sp), mob_hp(L), dict(p, amp=False))
        if best is None or s['spk'] < best[0]:
            best = (s['spk'], pn)
    return best
if __name__ == "__main__":
    print("seconds per kill (lower is better), sp = 1.0 x level")
    print(f"{'L':>3} {'Affliction first':>22} {'Aff to 21 then DK':>22} {'DK first':>22}")
    for L in (20, 25, 30, 35, 40, 45, 50, 55, 60):
        n = L - 9
        r = [spk(L, build(o, n)) for o in (AFF_FIRST, DK_PATH, DK_FIRST)]
        print(f"{L:>3} " + " ".join(f"{a:8.2f} {b[:13]:>13}" for a, b in r))
