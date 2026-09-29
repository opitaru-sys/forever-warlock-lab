# Forever Warlock Lab

A theorycraft lab for the Warlock class in WoW: Forever. It covers leveling rotations and talent order, the level-60 solo build, and the level-60 raid spec choice (Affliction, Destruction, or Demonology, and which pet to sacrifice).

Data is from the Forever beta as of 28-29 September 2026. Beta data can change before launch. Treat every number here as "true for this beta build," not "true forever."

Live page: https://opitaru-sys.github.io/forever-warlock-lab/

## The verdict

- **Leveling 10 to 33.** Affliction, instant Corruption first, then wand as your filler. Not Shadow Bolt, not Drain Life yet. Talents barely matter here: every sane build lands within 3% of the best.
- **Leveling 34 to 55.** Drain Life becomes the filler the moment Soul Siphon is done. Keep leveling Affliction-first.
- **Solo from 56.** Switch to a Demonic Knowledge splash, 28/23/0. It kills 5 to 7% faster than deep Affliction or the published drain-tank build, and held up when spell power tripled and pet damage halved.
- **Group at 60.** Destruction built around Incinerate, not Shadow Bolt. 4 to 7% ahead of the published build. Your Succubus decides the rest: sacrifice her under about 8% of your damage, keep her out above that, Demonology only above about 17 to 20%.
- **Race.** Undead levels fastest. A Human with a caster sword does the most raid damage. Every racial is worth under 2% of raid damage, so pick the race you like.

## How it was built

Data sources:
- Wowhead's Forever spell pages and talent calculator, for base spell values, SP coefficients, and talent per-rank effects.
- ForeverChanges.pro and the ElliotWood/Forever datamine, for anything Wowhead had not indexed yet.

Models:
- An expected-value leveling fight simulator (`models/leveling_sim.py`), used through `models/character.py`'s talent and character assumptions.
- A steady-state raid damage budget model (`models/raid_model.py`), reviewed by a separate Claude session working from its own code (`docs/review.md`).
- The page's JavaScript model (`model.js`) is a hand port of `models/raid_model.py`. `tests/parity_test.js` checks the two agree, cell by cell, on a spell power by crit grid.

Every number on the page or in this README traces back to one of the scripts in `models/` or `analysis/`.

## Assumptions

### Leveling model (`models/character.py`, `models/leveling_sim.py`)

| Input | Value as used |
|---|---|
| Spell power per level | `sp_per_level * level`, with `sp_per_level` in (0.5, 1.0, 2.0) across the scripts |
| Base crit | 5% flat, plus talents |
| Spirit | `15 + 1.2 * level` |
| Max health | `(20 + 28*L + 0.4*L^2) * (1 + 0.013 * Demonic Embrace ranks)` |
| Max mana | `(20 + 25*L + 0.45*L^2) * (1 + 0.035 * Fel Vitality ranks)` |
| Wand DPS | `0.9 * level + 3` |
| Pet DPS per pet (before talents) | Voidwalker 0.5/level, Succubus 1.1/level, Imp 0.8/level, Felhunter 0.8/level, no pet 0 |
| Mob HP | `18 * level + 0.62 * level^2` |
| Mob DPS (to the player) | `0.035 * level^2` |
| Damage taken fraction | 10% with a Voidwalker tanking, 100% with any other pet or no pet |
| Travel time between kills | 8 seconds, fixed |
| Rest rate (eating and drinking) | `2.2*L + 1.2*L*(1 + 0.10 * Improved Life Tap ranks)` mana-equivalent per second |
| Level-difference hit chance | 96% same level, 95% one level up, 94% two up, 83% three up, plus 1%/rank Suppression, capped at 99% |

### Raid model (`models/raid_model.py`, `model.js`)

| Input | Value as used |
|---|---|
| Hit | Assumed capped (no misses modeled), except a Demonology build without Suppression, which is modeled with a 5% throughput penalty when gear is not hit-capped |
| Mana | Life Tap only. No regen, no raid mana buffs, no potions |
| Life Tap value | Flat 840 by default, or `430 + Spirit` as a page toggle. Times 1.2 for builds with Improved Life Tap |
| Improved Shadow Bolt duration | 12 seconds by default, 60 seconds as a page toggle |
| Bane of Doom coefficient | 4.0 by default, adjustable on the page |

## How to reproduce each claim

Run every command from the repo root.

| Claim | Command |
|---|---|
| Leveling filler by level (Corruption/wand to L33, Drain Life from L34) | `python analysis/filler_by_level.py` |
| Leveling filler holds up under uncertain wand/pet/HP/rest assumptions | `python analysis/filler_robustness.py` |
| Best talent order while leveling (Affliction-first vs a Demonic Knowledge detour) | `python analysis/leveling_paths.py` |
| Best solo build from level 56 (Demonic Knowledge splash 28/23/0) | `python analysis/solo_builds_60.py` |
| Demonic Pact sacrifice stacking (Imp plus Felhunter/Voidwalker effects together) | `python analysis/pact_stacking.py` |
| Marginal value of a single talent point at levels 30/45/60 | `python analysis/talent_point_values.py` |
| Race effect on leveling speed | `python analysis/race_leveling.py` |
| Raid spec ranking, Bane of Doom vs Bane of Agony, Succubus sacrifice breakeven, Demonology crossover | `python models/raid_model.py` |
| Race effect on raid damage, and the live calculator behind the page | open `index.html`, or read `model.js` |
| Adversarial review of the raid model's claims and caveats | `docs/review.md` |
| model.js and models/raid_model.py agree | `node tests/parity_test.js` |

## How to contribute

If you have tested something in the beta or live game and it disagrees with a number here, open a [Test result](../../issues/new?template=test-result.yml) issue with what you did and what you saw.

If you think a formula, a spell value, or a talent effect here is wrong, open a [Correction](../../issues/new?template=correction.yml) issue with a source.

## Disclosure

Research, models and page were built with Claude (Anthropic). A separate Claude session then reviewed the work adversarially from its own code, and its corrections are applied. Every number traces to a source or a script here.

## License

MIT. See `LICENSE`.
