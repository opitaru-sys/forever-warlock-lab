import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "models"))

import leveling_sim as ls
from character import make_char, mob_hp, POLICIES, valid
def rep(*p):
    d = {}
    for k, n in p: d[k] = d.get(k, 0) + n
    return d
S = {
 'Deep Affliction 38/13/0': rep(('ImprovedCorruption',5),('ImprovedLifeTap',2),('Suppression',3),('Malediction',5),('ImprovedDrains',3),
    ('ImprovedBoA',2),('FelConcentration',3),('Pandemic',3),('Nightfall',2),('SiphonLife',1),('SoulSiphon',3),('ShadowMastery',5),('Wrack',1),
    ('DemonicEmbrace',5),('ImprovedVoidwalker',3),('FelVitality',3),('DemonicAegis',2)),
 'Demonic Knowledge splash 28/23/0': rep(('ImprovedCorruption',5),('Suppression',3),('ImprovedLifeTap',1),('ImprovedDrains',3),('Malediction',5),
    ('Pandemic',3),('ImprovedBoA',2),('Nightfall',2),('SiphonLife',1),('SoulSiphon',3),
    ('DemonicEmbrace',5),('UnholyPower',5),('FelVitality',3),('ImprovedVoidwalker',3),('DemonicSacrifice',1),('MasterSummoner',2),('FelDomination',1),('DemonicKnowledge',3)),
 'wowforeverbuilds drain tank (51)': rep(('ImprovedCorruption',5),('ImprovedLifeTap',2),('ImprovedDrains',3),('SoulHarvesting',2),('FelConcentration',3),
    ('Suppression',2),('AmplifyCurse',1),('Nightfall',2),('SiphonLife',1),('DemonicEmbrace',5),('ImprovedVoidwalker',3),('SoulSiphon',3),('ImprovedBoA',2),
    ('ShadowMastery',5),('Wrack',1),('Malediction',5),('CurseOfExhaustion',1),('Suppression',3),('FelVitality',2)),
}
if __name__ == "__main__":
    for name, t in S.items():
        assert valid(t), name
        print(name, sum(t.values()), 'pts')
    print()
    for L in (50, 60):
        for sp in (1.0, 2.0):
            print(f"L{L} sp={sp}xL")
            for name, t in S.items():
                n = L - 9
                # trim builds to the level's points by dropping from the end of dict order is messy; only compare at 60 fully, at 50 skip
                if L < 60 and sum(t.values()) > n:
                    continue
                best = None
                for pn, p in POLICIES.items():
                    s = ls.seconds_per_kill(make_char(L, t, sp), mob_hp(L), dict(p, amp=False))
                    if best is None or s['spk'] < best[1]['spk']:
                        best = (pn, s)
                w = ls.simulate(make_char(L, t, sp), 1e9, dict(POLICIES['DoTs+DrainLife'], amp=False), max_time=120)
                print(f"   {name:36s} spk {best[1]['spk']:5.2f} (ttk {best[1]['ttk']:4.1f} rest {best[1]['rest']:3.1f}) {best[0]:18s} 120s dmg {sum(w['dmg'].values()):6.0f} heal {w['healed']:5.0f}")
