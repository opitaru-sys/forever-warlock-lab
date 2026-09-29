import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "models"))

# Does the leveling filler conclusion survive changes in the uncertain assumptions?
import character as model
import leveling_sim
from character import make_char, mob_hp, POLICIES
from leveling_sim import seconds_per_kill
from filler_by_level import aff_build
import itertools

base_make = model.make_char
def run(L, wand_mult, pet_mult, hp_mult, rest_mult, sp):
    tal = aff_build(L)
    ch = base_make(L, tal, sp)
    ch.wand_dps *= wand_mult; ch.pet_dps *= pet_mult
    res = []
    for name, pol in POLICIES.items():
        rr = (2.2 * L + 1.2 * L * (1 + .1 * tal.get('ImprovedLifeTap', 0))) * rest_mult
        s = seconds_per_kill(ch, mob_hp(L) * hp_mult, dict(pol, amp=False), rest_rate=rr)
        res.append((s['spk'], name))
    res.sort()
    return res[0][1]

from collections import Counter
for L in (20, 30, 40, 50, 60):
    c = Counter()
    for wm, pm, hm, rm, sp in itertools.product((0.6, 1.0, 1.3), (0.5, 1.0, 2.0), (0.7, 1.0, 1.3), (0.5, 1.0, 2.0), (0.5, 1.0, 2.0)):
        best = run(L, wm, pm, hm, rm, sp)
        fam = 'Wand' if 'Wand' in best else ('SB' if 'SB' in best or 'ShadowBolt' in best else 'DrainLife')
        c[fam] += 1
    print(L, dict(c), 'of', sum(c.values()))
