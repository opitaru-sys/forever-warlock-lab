import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "models"))

import leveling_sim as ls
from character import make_char, mob_hp, POLICIES
from leveling_paths import build, AFF_FIRST
import io, contextlib
def best(L, t):
    b = None
    for pn, p in POLICIES.items():
        ch = make_char(L, t, 1.0)
        s = ls.seconds_per_kill(ch, mob_hp(L), dict(p, amp=False))
        if b is None or s['spk'] < b['spk']:
            b = s; b['ch'] = ch; b['pol'] = pn
    return b
print("L  spk  ttk  rest | share of rest removed by: Cannibalize(humanoid/undead mobs), Rapid Regen, Touch of the Grave | Beast Slaying ttk gain")
for L in (20, 30, 40, 50, 60):
    t = build(AFF_FIRST, L - 9)
    s = best(L, t); ch = s['ch']
    k = 1 + .1 * t.get('ImprovedLifeTap', 0)
    L_ = L
    rest_rate = 2.2 * L + 1.2 * L * k
    deficit = s['rest'] * rest_rate                       # mana-eq to recover per kill
    spk = s['spk']
    cann = 0.35 * (ch.max_hp * k + ch.max_mana) * spk / 120   # per kill, 2 min cd
    rapid = 0.5 * ch.max_hp * k * spk / 180                   # 3 min cd, health only
    events = 1.0                                               # ~1 spell/tick event per second in combat
    totg = 0.05 * 0.05 * ch.max_hp * k * events * s['ttk']     # 5% chance, 5% max HP
    f = lambda x: min(100, 100 * x / deficit) if deficit > 1 else 100
    print(f"{L}  {spk:4.1f} {s['ttk']:4.1f} {s['rest']:4.1f} | Cannibalize {f(cann):5.0f}%  Rapid Regen {f(rapid):5.0f}%  Touch of the Grave {f(totg):5.0f}%  | Beast Slaying ~{0.05*s['ttk']:.1f}s faster on beasts")
