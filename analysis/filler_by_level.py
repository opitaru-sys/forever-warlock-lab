import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "models"))

from character import make_char, mob_hp, POLICIES, valid
from leveling_sim import seconds_per_kill


def aff_build(L):
    n = L - 9
    order = (['ImprovedCorruption'] * 5 + ['Suppression'] * 3 + ['ImprovedDrains'] * 3 + ['Malediction'] * 5 +
             ['Pandemic'] * 3 + ['ImprovedBoA'] * 2 + ['SiphonLife'] + ['SoulSiphon'] * 3 + ['ShadowMastery'] * 5 +
             ['Wrack'] + ['Malevolence'] * 5 + ['Nightfall'] * 2 + ['ImprovedLifeTap'] * 2 + ['AmplifyCurse'] +
             ['FelConcentration'] * 3 + ['DemonicEmbrace'] * 5 + ['FelVitality'] * 3)
    tal = {}
    for k in order:
        if sum(tal.values()) >= n:
            break
        tal[k] = tal.get(k, 0) + 1
        if not valid(tal):
            tal[k] -= 1
    return tal

if __name__ == "__main__":
  print("seconds-per-kill (TTK + 8s travel + rest) | TTK | rest   -- Voidwalker pet, full-Affliction build")
  for sp in (0.5, 1.0, 2.0):
      print(f"\n== spell power = {sp} x level ==")
      for L in (20, 30, 40, 50, 60):
          tal = aff_build(L)
          row = []
          for name, pol in POLICIES.items():
              s = seconds_per_kill(make_char(L, tal, sp), mob_hp(L), dict(pol, amp=False))
              row.append((s['spk'], name, s['ttk'], s['rest']))
          row.sort()
          print(f"L{L}: " + " | ".join(f"{n} {spk:.1f} ({ttk:.1f}+{r:.1f})" for spk, n, ttk, r in row[:4]))
