# World of Warcraft: Forever, Warlock Talent Reference

> These are raw research notes written by AI research agents (Claude) for this lab. "The brief" or "your task brief" means the research instructions those agents were given, not a published source. Numbers here were cross-checked before use on the page.


Compiled 2026-09-28 from web research (WebSearch + WebFetch). WoW Forever beta has been running since 17 Sep 2026 (launch 4 Nov 2026). This is a "Classic+" title, NOT WoW Classic 2019 and NOT retail, the Warlock trees have been heavily reworked.

**Research method / caveats (read first):**
- Most talent-calculator sites (Wowhead, Icy-Veins, Zockify, Mobalytics, wowforevertalent.com) render their talent data client-side via JavaScript. WebFetch (which converts static HTML to markdown before an AI reads it) could NOT retrieve the actual talent grids from these, it only saw page shells/headers. Those are marked as failed sources below.
- Usable verbatim/near-verbatim data came from wowforevertalents.com, foreverchanges.pro, classicwowforever.com, forevertalents.org, conquestcapped.com (partial), and classicwow.gg, all of which appear to be third-party "guide" sites that had already scraped or transcribed the calculator data into static text/tables.
- Because none of these are Blizzard's own site, and several explicitly flagged their own numbers as beta-in-flux ("Numbers and talents below will change", warcrafttavern.com, beta build 1.60.1.69913, level cap 20 at time of writing), **treat exact numeric values (damage ranges, %, sec) as beta snapshots, not final**, and cross-check dates aren't published on any of these sites (no visible "last updated" timestamps), so recency could not be independently confirmed beyond internal text clues.
- I did not fill any gap from my own pre-2026 WoW Classic knowledge. Anything not found in a fetched source is marked **NOT FOUND**.

---

## Tree-wide rules

| Rule | Value | Sources |
|---|---|---|
| Total talent points at level 60 | **51** (points from level 10–60, one per level) | wowforevertalents.com, wowforevertalent.com, classicwow.gg, forevertalents.org, classicwowforever.com, foreverwisp.com, all six independently agree on 51 |
| "Gold" talents per tree (general Forever system, all 27 trees across all classes) | **4 per tree**: the Classic one-point milestone talents at **11, 21, and 31 points spent in that tree**, plus a **new 16-point milestone** added in Forever ("Blizzard calls them gold medal talents") | lfcarry.com/guides/wow-forever-talent-calculator, goldboosting.com/blog/wow-forever-class-rework-talent-trees-guide (two independent sources, consistent) |
| Can you take gold talents from multiple trees? | Points can be split across trees (a 20/31/0 or 31/20/0 style split is explicitly used as an example build), and lfcarry.com states "a 51-point single tree is legal," implying no hard restriction on where you invest, so yes, if a build crosses the 11/16/21/31 threshold in more than one tree, it collects the gold talent in each. No source explicitly states a cap on how many trees' gold talents you can combine. | lfcarry.com (inference from stated flexibility), **not explicitly confirmed in these words by any source, treat as reasoned inference, not verbatim confirmation** |
| Which specific talent occupies each of the 4 gold-talent slots (11/16/21/31 pts) per Warlock tree | **NOT FOUND.** One source (wowforevertalents.com) marks talents with a "★" it calls "New in Forever," but that is a *new-talent* marker, not a *point-threshold-gold* marker, it flags 6 Affliction, 7 Demonology, and 5 Destruction talents (18 total), far more than the 4-per-tree gold-talent mechanic described above. These two things are being conflated across sources; I could not find a site that maps the actual 11/16/21/31-point slot to a specific talent name for Warlock. | wowforevertalents.com (★ list); no source resolves the mapping |
| Row-gating rule | One source (classicwowforever.com) states: "the planner enforces a five-point minimum in earlier rows to access subsequent rows, plus prerequisite talents must be fully ranked", consistent with Classic's 5-points-per-row-to-unlock-next-row convention. Not independently corroborated by a second source in these exact words. | classicwowforever.com |
| Curses vs. Banes | Banes (Bane of Agony, Bane of Doom, Bane of Havoc) are now a separate school from Curses (Curse of Weakness, Curse of Exhaustion, Curse of Tongues, etc.), **one Bane AND one Curse can be active on a target simultaneously**, unlike Classic where all curses/banes shared one debuff slot. | WebSearch summary citing mobalytics.gg/wow-forever/guides/warlock-class-overview, foreverchanges.pro/class/warlock |
| Curse of Agony → Bane of Agony | Confirmed rename. Damage/coefficient reportedly changed: one source (foreverchanges.pro) states rank-6 damage dropped from 1044 to 552 while the spell-power coefficient rose from 8.3% to 13.3% (i.e., lower base, more scaling). Curse of Doom → Bane of Doom similarly: 3200→1742 damage, 100%→400% SP coefficient. **Only one source gave these exact numbers; NOT independently cross-checked.** | foreverchanges.pro/class/warlock |
| DoTs can critically strike | Confirmed by multiple independent guide summaries: "damage-over-time effects (DoTs) can now critically strike," making Malevolence (crit chance) and Pandemic (crit damage bonus on DoTs) meaningful for the first time. | mobalytics.gg/wow-forever/guides/warlock-class-overview, wowforeverbuilds.com/guide/beta-20-affliction-warlock-leveling, leprestore.com guides (via WebSearch summaries) |
| Total new / removed talent counts | **Disagreement across sources, see Discrepancies.** No source matched the task brief's "22 new, 20 removed" figure exactly. |

---

## AFFLICTION TREE

17 talents across 7 rows, ending in a 1-rank capstone (name disputed, see Discrepancies: **Wrack** vs **Drain Hope**).

| # | Talent | Row | Max Ranks | Prereq | New in Forever? | Tooltip (verbatim/near-verbatim per best source) |
|---|---|---|---|---|---|---|
| 1 | Improved Life Tap | 1 | 2 |, | Carried from Classic | "Increases the amount of Mana awarded by your Life Tap spell by 10%" per rank (R2: 20%) |
| 2 | Suppression | 1 | 5 |, | Carried | "Improves your chance to hit by 1% and reduces all threat you generate by 4%" per rank (R5: +5% hit / -20% threat) |
| 3 | Improved Corruption | 1 | 5 |, | Carried (buffed) | "Reduces the casting time of your Corruption spell by 0.4 sec and increases the damage it deals by 2%" per rank (R5: -2.0 sec cast [effectively instant per one source], +10% dmg) |
| 4 | Malediction | 2 | 5 |, | **NEW** | "Increases all periodic damage done by your Warlock spells by 1%" per rank (R5: 5%) |
| 5 | Soul Harvest (Soul Harvesting before the 1 Oct 2026 beta build) | 2 | 2 |, | **NEW** | Grants "Soul Harvest" for 10 sec on a kill while target is afflicted by your Drain Soul, mana regen buff, R1: 50%, R2: 100% (one source phrases as bonus mana regen; exact wording varies by fetch, see Discrepancies) |
| 6 | Improved Drains | 2 | 3 |, | **NEW** | "Increases health drained or damage done by your Drain Life, Drain Soul, and Wrack spells by 7%" per rank (R3: 20%, not a clean 3×7, likely non-linear ranks) |
| 7 | Improved Bane of Agony | 3 | 2 |, | Carried (renamed target spell) | "Increases the damage done by your Bane of Agony by 5%" per rank (R2: 10%) |
| 8 | Fel Concentration | 3 | 3 |, | Carried | "Gives you a 23% chance to avoid interruption caused by damage while channeling or casting" per rank (R3: 70%), one source specifies this protects Drain Life/Drain Mana/Drain Soul but explicitly NOT Drain Hope/Wrack |
| 9 | Amplify Curse | 3 | 1 |, | Carried | "Increases the effect of your next Curse of Weakness or Bane of Agony by 50%, or Curse of Exhaustion by 20%" |
| 10 | Pandemic | 3 | 3 |, | **NEW** | "Increases the critical strike damage bonus of your Corruption, Bane of Agony, Bane of Doom, Drain Soul, Drain Life, Siphon Life, and Wrack spells by 33%" per rank (R3: 100%) |
| 11 | Malevolence | 4 | 5 |, | **NEW** | "Increases the critical effect chance of your Shadow spells by 1%" per rank (R5: 5%) |
| 12 | Nightfall | 4 | 2 |, | Carried | "Gives your Corruption, Drain Soul, Drain Life, and Wrack spells a 2% chance to cause Shadow Trance" per rank (R2: 4%) |
| 13 | Curse of Exhaustion | 4 | 1 | Amplify Curse (per one source; unconfirmed by others) | Carried | "Reduces the target's movement speed by 30% for 12 sec" |
| 14 | Siphon Life | 5 | 1 | ~20 Affliction points (per one source) | Carried | "Transfers 11 health from the target to the caster every 3 sec. Lasts 30 sec." |
| 15 | Soul Siphon | 5 | 3 |, | **NEW** | "Increases damage done or health drained by Drain Life, Drain Soul, Wrack by 4% per Affliction effect" per rank (R3: 12% per effect, cap given once as "max 36%") |
| 16 | Shadow Mastery | 6 | 5 |, | Carried | "Increases the damage dealt or life drained by your Shadow spells by 1%" per rank (R5: 5%) |
| 17 | **Wrack / Drain Hope** (capstone) | 7 | 1 | Siphon Life (per two sources) | **NEW** | See Discrepancies, two competing tooltips found, under two different names |

---

## DEMONOLOGY TREE

18–19 talents (source count disagrees) across 7 rows, ending in a 1-rank capstone: **Demonic Pact** (all sources agree on this name, no naming dispute here).

| # | Talent | Row | Max Ranks | Prereq | New in Forever? | Tooltip (verbatim/near-verbatim) |
|---|---|---|---|---|---|---|
| 1 | Improved Health Funnel | 1 | 2 |, | Carried | "Increases the amount of health transferred by your Health Funnel spell by 20%" per rank; also reduces the health cost to caster (R2: 40% transfer / up to 100% cost reduction per one source, inconsistent, see Discrepancies) |
| 2 | Improved Imp | 1 | 3 |, | Carried | "Increases the damage of your Imp's Firebolt spell by 10% and the effect of its Fire Shield by 10%" per rank (R3: 30%) |
| 3 | Demonic Embrace | 1 | 5 |, | Carried | "Increases your total Stamina by 3%" per rank (R5: 15%) |
| 4 | Unholy Power | 1 | 5 |, | Carried | "Increases all damage done by your Imp, Voidwalker, Succubus, Incubus, and Felhunter pets by 2%" per rank (R5: 10%) |
| 5 | Demonic Aegis | 2 | 2 |, | **NEW** | "Increases the effectiveness of your Demon Skin and Demon Armor spells by 15%" per rank (R2: 30%) |
| 6 | Improved Voidwalker | 2 | 3 |, | Carried | "Increases the effectiveness of your Voidwalker's Torment, Consume Shadows, Sacrifice, and Suffering spells by 10%" per rank (R3: 30%) |
| 7 | Fel Vitality | 2 | 3 |, | Carried | "Increases the maximum health and Mana of your Imp, Voidwalker, Succubus, Incubus, Felhunter by 5%, and increases your maximum Mana by 5%" per rank (R3: 15%) |
| 8 | Demonic Energies | 2 | 2 |, | **NEW** | "You heal your pet for 8% of all spell damage you deal. When you gain Mana from Life Tap, your demon gains 50%[of that]" per rank (R2: 15% heal / 100% mana share) |
| 9 | Improved Sayaad | 3 | 3 |, | Carried | "Increases the effect of your Succubus' and Incubus' Lash of Pain and Soothing Kiss spells by 10%" per rank (R3: 30%) |
| 10 | Demonic Sacrifice | 3 | 1 | ~10 Demonology points (one source) | Carried | "When activated, sacrifices your summoned Demon" for a buff depending on type: Imp +15% Shadow dmg; Voidwalker +2% mana regen; Succubus/Incubus +15% Fire dmg; Felhunter +3% health regen |
| 11 | Master Summoner | 3 | 2 |, | Carried | "Reduces the casting time of your Summoning spells by 2 sec and Mana cost by 20%" per rank (R2: 4 sec / 40%) |
| 12 | Decimation | 3 | 2 |, | **NEW** | "Reduces the cooldown of your Soul Fire spell by 45%" per rank (R2: 90%); also grants bonus damage (one source: +3%/rank, cap 6%) when the enemy is below 35% health |
| 13 | Fel Domination | 4 | 1 |, | Carried | "Your next Summon spell has its casting time reduced by 5.5 sec and Mana cost reduced by 50%" |
| 14 | Demonic Brand | 4 | 3 |, | **NEW** | "Your Searing Pain generates 17% less threat and brands the target for 10 sec" per rank (R3: 50% less threat) |
| 15 | Improved Felhunter | 5 | 3 |, | **NEW** | "Increases the Attack Power reduction of your Felhunter's Tainted Blood, healing of Devour Magic, and detection level of Paranoia by 10%, and reduces Spell Lock cooldown by 2 sec" per rank (R3: 30% / 6 sec) |
| 16 | Soul Link | 5 | 1 | Demonic Sacrifice | Carried | "When active, 30% of all damage taken by the caster is taken by your Demon instead", both Demon and master then inflict 3% more damage (per one source) |
| 17 | Demonic Knowledge | 5 | 3 |, | **NEW** | "Increases your spell damage and your Demon pet's spell damage by up to 33% of your level" per rank (R3: 100% of level) |
| 18 | Master Demonologist | 6 | 5 |, | Carried | Grants both Warlock and active demon a per-pet-type bonus: Imp +Fire dmg, Voidwalker −Physical dmg taken, Succubus/Incubus +Shadow dmg, Felhunter −Magic dmg taken, 2%/rank, 10% at R5 (per one source) |
| 19 | **Demonic Pact** (capstone) | 7 | 1 | Soul Link | **NEW** | "Your Demonic Sacrifice effect is no longer cancelled by summoning a different Demon pet." One source adds the caveat: "Resummoning the sacrificed pet will still cancel the effect." |

Note: one source also lists a talent called **"Portal of Summoning"** as new to Demonology (foreverchanges.pro), which no other fetched source mentioned or placed in a row. **NOT independently corroborated, possibly a beta-only/renamed/cut talent. Row/rank/tooltip: NOT FOUND.**

---

## DESTRUCTION TREE

16 talents across 7 rows, ending in a 1-rank capstone: **Incinerate** (all sources agree on this name).

| # | Talent | Row | Max Ranks | Prereq | New in Forever? | Tooltip (verbatim/near-verbatim) |
|---|---|---|---|---|---|---|
| 1 | Destructive Reach | 1 | 2 |, | Carried | "Increases the range of your damaging spells by 10%" per rank (R2: 20%) |
| 2 | Improved Shadow Bolt | 1 | 5 |, | Carried | "Your Shadow Bolt critical strikes increase Shadow damage taken by the target by 4% for 12 sec" per rank (R5: 20%) |
| 3 | Bane | 1 | 5 |, | Carried | "Reduces the casting time of your Shadow Bolt, Immolate, and Incinerate spells by 0.1 sec and Soul Fire by 0.4 sec" per rank (R5: 0.5 sec / 2 sec) |
| 4 | Molten Skin | 1 or 2 (disputed) | 5 |, | **NEW** | "Reduces all damage taken by 2%" per rank (R5: 10%) |
| 5 | Cataclysm | 2 | 3 |, | Carried | "Reduces the Mana cost of your Destruction spells by 3%" per rank (R3: 10%) |
| 6 | Aftermath | 2 | 5 |, | Carried | "Increases the initial damage of your Immolate spell by 10% and your Conflagrate spell has a 20% chance to Daze" per rank (R5: 50% Immolate dmg / 100% Daze chance) |
| 7 | Ruin | 2 or 3 (disputed) | 5 |, | Carried | "Increases the critical strike damage bonus of your Destruction spells by 20%" per rank (R5: 100%) |
| 8 | Shadowburn | 3 | 1 |, | Carried | "Instantly blasts the target for [X] Shadow damage. If the target is non-trivial and dies within 8 sec, the caster gains a Soul Shard." Damage range disputed across sources, see Discrepancies |
| 9 | Intensity | 3 or 4 (disputed) | 3 |, | Carried | "Gives you a 23% chance to resist interruption caused by damage while casting any Destruction spell" per rank (R3: 70%) |
| 10 | Agonizing Flames | 3 or 4 (disputed) | 3 |, | Carried | "Increases the critical strike chance of your Searing Pain spell by 3% and damage of all Destruction spells by 3%" per rank (R3: 10%) |
| 11 | Conflagrate | 4 | 1 | Shadowburn (per one source) | Carried | "Ignites a target already afflicted by your Immolate spell, dealing [X] Fire damage and consuming your Immolate effect." Damage range disputed, see Discrepancies |
| 12 | Pyroclasm | 4 or 5 (disputed) | 2 | Intensity (per one source) | Carried | "Gives your Soul Fire spell a 13% chance to Stun the target for 3 sec" per rank (R2: 26%) |
| 13 | Bane of Havoc | 5 | 1 |, | **NEW** | "Afflicts the target for 5 min, causing 15% of all damage done by the Warlock to other targets to also be dealt to the cursed target" |
| 14 | Fire and Brimstone | 5 | 3 | Conflagrate (per one source) | **NEW** | "Increases the critical strike chance of your Conflagrate spell by 8%" per rank (R3: 25%) |
| 15 | Shadow and Flame | 6 | 5 |, | **NEW** | "Hitting an enemy with Conflagrate increases all Shadow damage you deal by 2% [for 20 sec, per one source]; Shadowburn increases all Fire damage by 2%; 20% chance not to consume Immolate [on Conflagrate]" per rank (R5: 10% / 100% chance not to consume) |
| 16 | **Incinerate** (capstone) | 7 | 1 | Bane of Havoc (per one source) | **NEW** | "Deals [X] Fire damage to your target and an additional 25% damage if the target is afflicted by Immolate." Damage range disputed, see Discrepancies |

---

## Discrepancies

### 1. Affliction capstone name: "Wrack" vs. "Drain Hope"
- **wowforevertalents.com, wowforevertalent.com, classicwow.gg, classicwowforever.com** all name the capstone **Wrack**: "Tears the target apart from within, dealing 36 Shadow damage every 1 sec and increasing damage they take from your other Shadow damage over time effects by 10%. Lasts 6 sec."
- **forevertalents.org, expcarry.com/wow-forever-warlock-guide** name it **Drain Hope**: "Drains all hope from the target, dealing 52 Shadow damage every 1 sec and increasing all other Shadow damage over time you deal to that target by 10%. Lasts 6 sec."
- **mythicsim.com/wow-forever/warlock explicitly resolves this**: "Wrack was called Drain Hope in the BlizzCon preview", implying Wrack is the current (post-rename) in-game name and Drain Hope is an older beta/preview name some guide sites haven't updated. **This is the newest-looking explanation found**, but no source carries a visible patch-date to confirm which name is live in the current (17 Sep 2026-onward) beta build.
- The damage-per-tick differs (36 vs 52) even between sources using different names for what is otherwise an identical effect (Shadow dmg/1 sec, +10% other Shadow DoT dmg, 6 sec duration), this could reflect a genuine tuning pass between the "Drain Hope" preview and the "Wrack" beta version, not just a naming change.
- **Your task brief lists "Drain Hope" as a known capstone name, that matches the older/preview naming per mythicsim, not what looks like the current beta name (Wrack).** Flagging this directly since it affects which name is "correct" for a verbatim reference.

### 2. Damage ranges for flat-damage Destruction spells/talents (Shadowburn, Conflagrate, Incinerate)
Three separate numeric sets were found across otherwise similar tables, with no source dated to resolve which is newest:

| Talent | wowforevertalents.com | foreverchanges.pro | classicwow.gg | forevertalents.org | classicwowforever.com |
|---|---|---|---|---|---|
| Shadowburn | 65–74 | 62–70 | 65–73 | (not given) | 65–73 |
| Conflagrate | 87–112 | 84–106 | 88–110 | (not given) | (not given) |
| Incinerate | 99–115 | 90–104 | 99–113 | **125–140** | 99–113 |

Four of five sources cluster near "99–115" for Incinerate; **forevertalents.org's 125–140 is an outlier** and worth treating with suspicion (possibly a stale/different beta patch, or an error in that site's own scrape). No source states a patch/build number next to these specific numbers, so "which looks newer" could not be determined with confidence, flagging the outlier rather than guessing.

### 3. Total new/removed talent counts
- Your task brief states **22 new talents, 20 removed**.
- WebSearch summary of wowforevertalents.com stated **18 new, 32 changed** (does not give a "removed" count in the same terms).
- WebSearch summary citing multiple guide sites stated **19 new, 28 changed**.
- mythicsim.com stated **"19 new talents and 17 removed."**
- foreverchanges.pro/class/warlock (fetched directly) lists by name: **6 new Affliction + 8 new Demonology (incl. the uncorroborated "Portal of Summoning") + 5 new Destruction = 19 new**; and **6 removed Affliction + 5 removed Demonology + 5 removed Destruction = 16 removed**.
- **None of the fetched/searched sources match the brief's "22 new / 20 removed" exactly.** The closest and most directly itemized (named, not just counted) is foreverchanges.pro's 19 new / 16 removed. This may reflect the count changing between beta patches (new beta patches could have added/cut a few more talents since whatever snapshot these guide sites scraped), or the brief's figures may come from a source I could not reach (e.g., official Blizzard patch notes, which I did not find indexed by search).

### 4. Row/tier numbering for several Destruction talents
Two fetches disagreed by one row on where several talents sit (Molten Skin row 1 vs 2; Ruin row 2 vs 3; Intensity/Agonizing Flames row 3 vs 4; Pyroclasm row 4 vs 5), the talent's rank count, tooltip, and relative order were otherwise consistent, so this looks like an off-by-one indexing difference between how two guide sites numbered rows (e.g., whether row 1 is "row 0" in one site's internal data), not a real content dispute. Flagged for completeness; **exact row number for these five talents should be treated as approximate.**

### 5. Prerequisites are thin and inconsistently reported
Only classicwowforever.com and forevertalents.org gave a fairly complete prerequisite column, and even those largely say "None" for most talents, reserving named prerequisites only for capstones and a handful of others (Curse of Exhaustion ← Amplify Curse; Fel Domination ← Master Summoner; Soul Link ← Demonic Sacrifice; Conflagrate ← Shadowburn; Pyroclasm ← Intensity; Fire and Brimstone ← Conflagrate). Whether these are true hard prerequisites or just "same row, must fill row first" artifacts of the Classic-style 5-points-per-row gate **could not be fully disentangled from available sources**.

### 6. "Gold talent" mechanic vs. individual talent's "New in Forever" flag
wowforevertalents.com marks 18 talents across the three Warlock trees with a "★" which its page frames as "New in Forever," not as the specific 11/16/21/31-point "gold talent" milestone mechanic described by lfcarry.com and goldboosting.com (which is a 4-per-tree, all-classes system). These are two different concepts that multiple guide sites' summaries blur together. **I could not find a source that names which single talent occupies each of the 4 actual point-threshold gold slots for any Warlock tree, this is NOT FOUND, not just uncertain.**

### 7. Health Funnel / Demonic Energies rank-2 numbers
Two fetches gave inconsistent rank-2 values for Improved Health Funnel's threat-cost reduction (40% vs 100% at R2) and for Demonic Energies' pet-heal percentage (15% vs a differently-worded "100%" mana-share clause), likely the two source pages conflated two different effects on the same talent (health-transfer amount vs. threat/cost reduction). Recorded both readings in the tables above rather than picking one.

---

## Items marked NOT FOUND
- Exact mapping of which specific talent sits at each tree's 11-, 16-, 21-, and 31-point gold-talent threshold (Warlock-specific).
- Row, rank count, and tooltip for "Portal of Summoning" (Demonology), named by only one source, not located elsewhere.
- Any Blizzard-official (first-party) source, patch notes, official talent calculator, or developer post, confirming final (non-beta) numbers. Everything above comes from third-party fan/guide sites; none carried a visible "last updated"/patch-version date next to the specific numbers quoted, except warcrafttavern.com's build tag (1.60.1.69913, level cap 20), which is too early (pre-level-60) to certify endgame tooltip numbers.
- Exact prerequisite (points-in-tree) requirement for several mid-tree talents (e.g., Siphon Life's "~20 Affliction points," Demonic Sacrifice's "~10 Demonology points"), only approximate/rounded figures were available, sourced from single fetches each.
- Confirmation of whether Fel Domination is genuinely gated behind Master Summoner or whether that's an artifact of row order.
- A verbatim, complete tooltip for Soul Harvest (formerly Soul Harvesting) rank 1 and rank 2 (paraphrased differently by every source that mentioned it).

---

## Sources

Fetched successfully and used for talent data:
- https://wowforevertalents.com/warlock/
- https://wowforevertalent.com/warlock/
- https://foreverchanges.pro/talents/warlock
- https://foreverchanges.pro/class/warlock
- https://classicwow.gg/forever/guides/warlock
- https://forevertalents.org/warlock/
- https://classicwowforever.com/talents/warlock/

Fetched but yielded only partial/summary data (page not fully scrapable as static HTML, or content was guide commentary rather than a full talent grid):
- https://conquestcapped.com/guides/wow-forever/wow-forever-warlock-talents/
- https://www.foreverwisp.com/guides/wow-forever-warlock-leveling-talents
- https://www.zockify.com/forever/warlock/
- https://www.mmoexp.com/News/wow-forever-warlock-talents-affliction-looks-insane-demonology-gets-major-changes.html
- https://www.warcrafttavern.com/forever/guides/warlock/
- https://mythicsim.com/wow-forever/warlock
- https://lfcarry.com/guides/wow-forever-talent-calculator
- https://goldboosting.com/blog/wow-forever-class-rework-talent-trees-guide
- https://expcarry.com/wow-forever-warlock-guide

Fetch failed (HTTP 403 or JS-only shell page with no usable content):
- https://www.icy-veins.com/wow-forever/warlock-talent-calculator (403)
- https://www.icy-veins.com/wow-forever/warlock-class-overview (403)
- https://www.wowhead.com/forever/talent-calc/warlock (JS shell only)
- https://www.wowhead.com/forever/class=9/warlock (JS shell only)
- https://mobalytics.gg/wow-forever/classes/affliction-warlock-guide (403)
- https://mobalytics.gg/wow-forever/classes/demonology-warlock-guide (403)

Referenced only via WebSearch result snippets (not independently fetched, so treat as secondhand/lower-confidence):
- https://mobalytics.gg/wow-forever/guides/warlock-class-overview (Curses/Banes split, DoT crit confirmation)
- https://wowforeverbuilds.com/guide/beta-20-affliction-warlock-leveling (DoT crit confirmation)
- https://leprestore.com/guides/world-of-warcraft-forever/wow-forever-affliction-warlock-guide-best-builds-race-professions/ (DoT crit confirmation)
- https://leprestore.com/guides/world-of-warcraft-forever/wow-forever-warlock-guide-overview/
- https://www.rpgstash.com/blog/wow-forever-classes-and-talents-guide
- https://boostroom.com/blog/wow-forever-talent-trees-guide-talents-builds-and-class-changes-explained
- https://wow.gg/guides/warlock-affliction-forever-overview
- https://talentsforever.com/warlock (never directly fetched)
- https://www.wowhead.com/forever/talent-calc/warlock/affliction (referenced by expcarry.com as its own citation, not independently verified)

Not usable / off-topic despite appearing in results:
- https://us.forums.blizzard.com/en/wow/t/wow-forever-warlock-guide-all-the-changes-you-didnt-notice/2359459 (official forum thread exists, a first-party-adjacent community source, but was not fetched; **worth a follow-up fetch if more confidence is needed on the Wrack/Drain Hope naming and exact numbers**)
- https://github.com/ElliotWood/Forever/pull/526 (a GitHub PR about a UI addon showing Forever-renamed spell/talent names, potentially useful for confirming exact current names, not fetched)
- https://en.wikipedia.org/wiki/Agony_(2018_video_game) (irrelevant, unrelated game titled "Agony")
