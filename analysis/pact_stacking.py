import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "models"))

import leveling_sim as ls
from character import make_char, mob_hp, POLICIES, valid
import io, contextlib
with contextlib.redirect_stdout(io.StringIO()):
    from solo_builds_60 import S
def rep(*p):
    d = {}
    for k, n in p: d[k] = d.get(k, 0) + n
    return d
PACT = rep(('DemonicEmbrace',5),('UnholyPower',5),('FelVitality',3),('ImprovedVoidwalker',2),('DemonicSacrifice',1),('MasterSummoner',2),
           ('ImprovedSayaad',2),('FelDomination',1),('Decimation',1),('SoulLink',1),('DemonicKnowledge',3),('MasterDemonologist',4),('DemonicPact',1),
           ('ImprovedCorruption',5),('Suppression',3),('ImprovedDrains',3),('Malediction',5),('Pandemic',3),('ImprovedBoA',1))
assert valid(PACT) and sum(PACT.values()) == 51
def best(ch, L):
    b = None
    for pn, p in POLICIES.items():
        s = ls.seconds_per_kill(ch, mob_hp(L), dict(p, amp=False))
        if b is None or s['spk'] < b[0]: b = (s['spk'], pn, s['ttk'], s['rest'])
    return b
L = 60
print("L60 seconds per kill, sp = 1.0 x level")
r = best(make_char(L, S['Demonic Knowledge splash 28/23/0'], 1.0), L); print(f"  DK splash 28/23/0 + Voidwalker          {r[0]:.2f} (ttk {r[2]:.1f} rest {r[3]:.1f})")
for pet in ('voidwalker', 'succubus'):
    t = dict(PACT, _sac='imp')
    r = best(make_char(L, t, 1.0, pet), L); print(f"  Pact, Imp sac only + {pet:10s}         {r[0]:.2f} (ttk {r[2]:.1f} rest {r[3]:.1f})")
    ch = make_char(L, t, 1.0, pet)
    ch.felhunter_sac = True
    if pet != 'voidwalker':
        ch.voidwalker_sac = True
    r = best(ch, L); print(f"  Pact, IF sacrifices stack + {pet:10s}  {r[0]:.2f} (ttk {r[2]:.1f} rest {r[3]:.1f})")
