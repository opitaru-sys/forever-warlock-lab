# Forever Warlock Lab

A theorycraft lab for the Warlock class in WoW: Forever. It covers leveling rotations and talent order, the level-60 solo build, and the level-60 raid spec choice (Affliction, Destruction, or Demonology, and which pet to sacrifice).

Data is from the Forever beta as of 28-29 September 2026. Beta data can change before launch. Treat every number here as "true for this beta build," not "true forever."

Live page: https://opitaru-sys.github.io/forever-warlock-lab/

## The verdict

- **Leveling 10 to 29.** Affliction, instant Corruption first, then wand as your filler. Not Shadow Bolt, not Drain Life yet. Talents matter little before 28: every build tested lands within 4% of the best.
- **Leveling 30 to 55.** Drain Life becomes the filler as Soul Siphon comes in. Keep leveling Affliction-first. Destruction builds (Immolate, Incinerate, Shadow Bolt) kill faster but rest longer, and lose overall.
- **Solo from 56.** A Demonic Knowledge splash, 28/23/0, is optional. It kills about 3 to 4.5% faster than deep Affliction or the published drain-tank build, but only breaks even against this lab's leveling order.
- **Group at 60.** Deep Demonology, 5/31/15: Suppression 5, Imp sacrificed, Succubus out, Searing Pain to keep Demonic Brand on the boss. About 4 to 5% ahead of Pact and 7% ahead of Destruction at the calculator defaults; if Demonic Brand deals no damage, it is still about 1% ahead. Fire Destruction built around Incinerate is the pick when the Succubus cannot stay on the boss. On a Fire-immune boss the group spec still leads.
- **Race.** Undead levels fastest (about 4%). In raids, Undead's Touch of the Grave (about 1.6%) and a Human's caster sword (about 1.5%) are within half a percent, and a reported beta change may tip it to the Human. Every racial is small, so pick the race you like.

## How it was built

Data sources:
- Wowhead's Forever spell pages and talent calculator, for base spell values, SP coefficients, and talent per-rank effects.
- ForeverChanges.pro and the ElliotWood/Forever datamine, for anything Wowhead had not indexed yet.
- Since v8, the beta client's own SpellEffect table (build 1.60.1.69893, from the ElliotWood/Forever data cache) for base damage and spell power coefficients. It settled Immolate's coefficients (0.2 on the hit, 0.13 per tick) and Life Tap's (430 + Spirit).

Models:
- An expected-value leveling fight simulator (`models/leveling_sim.py`), used through `models/character.py`'s talent and character assumptions.
- A steady-state raid damage budget model (`models/raid_model.py`), reviewed by a separate Claude session working from its own code (`docs/review.md`).
- The page's JavaScript model (`model.js`) is a hand port of `models/raid_model.py`. `tests/parity_test.js` checks the two agree, cell by cell, on a spell power by crit grid, and `tests/raid_options_test.js` checks every calculator option against Python fixtures.
- The page's level planner and talent builder run `leveling.js`, a line-for-line port of the leveling model. `tests/leveling_parity_test.js` checks it against Python fixtures.
- A rougher multi-mob model (`models/multimob.py`) for pulls of several mobs.

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
| Hit | Gear hit slider, default 11%. Every build takes Suppression, which adds 5%, so 11% from gear caps you by default. Each 1% short of the 16% boss cap costs 1% of damage |
| Mana | A Major Mana Potion and a Demonic or Dark Rune on cooldown by default, optional mp5 from gear and buffs, Life Tap for the rest. No raid buffs |
| Life Tap value | `430 + Spirit` by default (Spirit 100), or flat 840 as a page toggle. Times 1.2 for builds with Improved Life Tap |
| Fight options | Shadowburn on cooldown, execute phase under 35% (Decimation's +6%) on by default; Fire-immune boss, two targets, Curse of the Elements off by default |
| Demonic Brand | 3 extra pet hits per brand by default (tooltip), 0 or 6 as page options; untested |
| Improved Shadow Bolt duration | 12 seconds by default, 60 seconds as a page toggle |
| Bane of Doom coefficient | 4.0 by default, adjustable on the page |

## How to reproduce each claim

Run every command from the repo root.

| Claim | Command |
|---|---|
| Leveling filler by level (wand to L29, Drain Life from L30 with this lab's order) | `python analysis/filler_by_level.py` |
| Destruction leveling builds (reader builds, 17/0/34, speedrun-style, respec search) | `python analysis/destro_leveling.py` |
| The planner's leveling order and solo build | `python analysis/planner_order.py` |
| Pulls of several mobs | `python analysis/multimob_leveling.py` |
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
| Gear hit, stat weights and item comparison behave as specified | `node tests/weights_test.js` |
| Every raid calculator option matches Python | `node tests/raid_options_test.js` (regenerate with `python tests/make_raid_fixtures.py`) |
| leveling.js matches the Python leveling model | `node tests/leveling_parity_test.js` (regenerate with `python tests/make_leveling_fixtures.py`) |

## Changelog

- **v8.1, 29 Sep 2026.** Group spec is now 5/31/15 (a reader's improvement: Suppression's 5% hit covers every spell, about 4% over 0/35/16 when gear alone does not cap hit). Pact takes Suppression too. Note on a reported Touch of the Grave nerf.
- **v8, 29 Sep 2026.** Closed every modeling gap readers found. Leveling: every Destruction spell and talent, Curse of the Elements, Death Coil and finishers, base damage and coefficients from the beta client, results averaged over mob health; Destruction builds lose on rest; a new leveling order, about 2% faster; the solo respec is optional. Raid: deep Demonology 0/35/16 is the recommended group spec; Fire-immune bosses, execute phase, mana consumables, two targets, Curse of the Elements and mp5 options; Life Tap reads 430 + Spirit. A first multi-mob model. Corrections: tick tables were 1 too high, Wrack's +10% only reaches Corruption and Agony, Undead leveling 3 to 6%, Troll about 1%, Nightfall under 1% a point.
- **v7, 29 Sep 2026.** Undead's Touch of the Grave now counts in the raid model. Casters get a 10% version (Wowhead Forever spell 1260201), not the 5% one the page first used. Max health slider for Undead. Reported in the Reddit thread, where the same reader tested that applying a DoT triggers it but ticks don't, which is what the model counts.
- **v6, 29 Sep 2026.** Game icons throughout (talent cells styled like the in-game talent window, race portraits, rotation icons, tree icons), and the chosen race now themes the whole page with a race badge in the section nav. Dungeons got their own section, with every dungeon on one level line filtered to your faction. Icons live in `assets/icons/` and are embedded by `src/build.py`.
- **v5, 29 Sep 2026.** A talent builder: click any build into the three trees, pick a demon, a sacrifice and gear, and see seconds per kill next to the page plan, with shareable build links (`#b-...`). It runs `leveling.js`, a port of the Python leveling model checked by `tests/leveling_parity_test.js` (444 cases, exact match). Race themes re-tint the page header, and talent trees have their own colors in the builder and the raid chart. Asked for in the Reddit thread.
- **v4, 29 Sep 2026.** Redesign after a four-reviewer UX pass (structure, visual design, interaction and accessibility, first-time Reddit visitor): sticky section nav, a beginner on-ramp and glossary, race and level controls in one place, a two-column calculator with a gap column and a sticky results panel, phone tables that stack into cards, a leader strip on phones, linkable levels and races (`#lvl-24`, `#race-undead`), clamped inputs, saved calculator settings, and calmer screen reader updates. From Reddit comments: Troll PvP corrected (Fear into Rapid Regeneration), and a 5/31/0 Succubus leveling build added as a claim with its own test (Demonic Brand aggro). Numbers unchanged.
- **v3, 29 Sep 2026.** Stat weights per build (spell power, crit, hit, with crit and hit priced in spell power). An item comparer that re-runs the full model for a swap. A gear hit slider replaces the hit-cap checkbox; the default reproduces the reviewed numbers exactly. The level planner lists dungeons that fit your level and faction (levels from zockify.com and lfcarry.com; returning dungeons use an estimated range around Forever's recommended level). Requested in the Reddit thread.
- **v2, 29 Sep 2026.** Interactive page: race picker, level planner, live raid calculator, test checklist.
- **v1, 28 Sep 2026.** First published research.

## How to rebuild the page

`index.html` is generated. Edit `src/page.src.html`, `src/builder.js`, `model.js` or `leveling.js`, then run `python src/build.py` from the repo root and rerun the three test scripts in `tests/`.

## How to contribute

If you have tested something in the beta or live game and it disagrees with a number here, open a [Test result](../../issues/new?template=test-result.yml) issue with what you did and what you saw.

If you think a formula, a spell value, or a talent effect here is wrong, open a [Correction](../../issues/new?template=correction.yml) issue with a source.

## Disclosure

Research, models and page were built with Claude (Anthropic). A separate Claude session then reviewed the work adversarially from its own code, and its corrections are applied. Every number traces to a source or a script here.

## Game art

The icons in `assets/icons/` are Blizzard Entertainment's art, downloaded from Wowhead's image server (`wow.zamimg.com`). They are used here in a non-commercial fan project and are not covered by this repo's MIT license.

## License

MIT. See `LICENSE`.
