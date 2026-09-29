import sys, importlib, os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "models"))

import leveling_sim as ls
import character as model
model.seconds_per_kill = None
from character import make_char, POLICIES
def dmg30(L, tal, pol):
    s = ls.simulate(make_char(L, tal, 1.0), 1e9, dict(POLICIES[pol], amp=False), max_time=120)
    return sum(s['dmg'].values()), s['mana_spent'] - s['lt_mana'], s['healed']
for L, base, pol in [(30, {'ImprovedCorruption':5,'Suppression':3}, 'DoTs+Wand'),
                     (45, {'ImprovedCorruption':5,'Suppression':3,'SiphonLife':1,'ImprovedDrains':3}, 'DoTs+DrainLife'),
                     (60, {'ImprovedCorruption':5,'Suppression':3,'SiphonLife':1,'ImprovedDrains':3,'SoulSiphon':3,'Malediction':5,'ShadowMastery':5}, 'DoTs+DrainLife')]:
    b, mana, heal = dmg30(L, base, pol)
    print(f"\nL{L} {pol}: 30s damage {b:.0f} net mana {mana:.0f} healed {heal:.0f}")
    for k, n in [('Malediction',5),('ShadowMastery',5),('Pandemic',3),('Malevolence',5),('ImprovedBoA',2),('Nightfall',2),
                 ('SoulSiphon',3),('ImprovedDrains',3),('UnholyPower',5),('DemonicKnowledge',3),('SiphonLife',1),('SoulHarvesting',2),('ImprovedLifeTap',2)]:
        t = dict(base)
        if t.get(k, 0) + n > model.AFF.get(k, model.DEMO.get(k, (0, 99)))[1]:
            continue
        t[k] = t.get(k,0)+n
        v, m2, h2 = dmg30(L, t, pol)
        print(f"  +{n} {k:18s} dmg {100*(v-b)/b:+5.2f}%  ({100*(v-b)/b/n:+.2f}%/pt)  net-mana {m2-mana:+5.0f} heal {h2-heal:+5.0f}")
