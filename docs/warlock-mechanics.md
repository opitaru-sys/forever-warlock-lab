# Warlock Damage & Sustain Mechanics, World of Warcraft: Forever (Beta)

> These are raw research notes written by AI research agents (Claude) for this lab. "The brief" or "your task brief" means the research instructions those agents were given, not a published source. Numbers here were cross-checked before use on the page.


**Game:** WoW: Forever, Blizzard's 2026 "Classic+" title. Beta live since 17 Sep 2026, launch 4 Nov 2026, level cap 60, original world. **This is NOT WoW Classic (2019) and NOT retail**, many numbers are inherited from Classic 1.15.9 but many are deliberately rewritten.

**Beta client builds behind this data:** `1.60.1.69893` (17 Sep 2026 read) through `1.60.1.70009` (25 Sep 2026 read). Numbers have already moved between these builds in some places (noted inline). Everything here is beta-snapshot and can change before 4 Nov launch.

**Labeling convention used throughout:**
- **[FOREVER-CONFIRMED]**, read directly from the Forever beta client (datamined spell/trait tables) or an official BlizzCon panel quote.
- **[FOREVER-TESTED]**, reported from hands-on beta play (Icy Veins), not datamined, so treat as directional not exact.
- **[CLASSIC VALUE, unconfirmed for Forever]**, no Forever-specific source found; this is the Classic 1.15.9 number.
- **[NOT FOUND]**, no source located for this at all.

---

## 1. Spells

All damage/mana/duration numbers below are **[FOREVER-CONFIRMED]**, read from the beta client and cross-checked between two independent datamining projects: **ForeverChanges.pro** (client build `1.60.1.70009`, wago.tools TraitNode export) and the **ElliotWood/Forever** wowsims fork (client build `1.60.1.69893`, `tools/data_watch/spell_client.py`). Where the two builds disagree by a small amount, both are given, this is real beta-to-beta drift, not an error in either source.

Format: values shown are the **max rank** (usually the level-60 rank) unless noted. Spell power coefficient (coef) is per-cast for direct damage, per-tick for DoTs, given where the source states it.

### Direct damage / execute spells

| Spell | Max rank | Lvl learned | Mana | Cast time | Damage (Forever) | Damage (Classic) | Coef (Forever) | Notes |
|---|---|---|---|---|---|---|---|---|
| Shadow Bolt | R10 (book), R9 (trainer) | 1 | 380 / 370 | 3 sec | 253 to 283 / 237 to 265 | 482 to 538 | 1.7 sec ratio → 0.857 (coef .486/.629/.8 on ranks 1 to 3, rising) | Damage cut to ~half Classic; coefficient markedly higher on early ranks. R10 is taught only by Grimoire of Shadow Bolt X (item 21281), a Ruins of Ahn'Qiraj drop in Classic, with no Forever source yet. |
| Soul Fire | R2 | 48 | 335 | 6 sec | 383–479 (per foreverchanges) / 390–487 (per ElliotWood build) | 703–881 / 715–894 | not stated | 1 min cooldown; Decimation talent can zero its cooldown/cost for 10 sec |
| Searing Pain | R6 | 18 | 168 | 1.5 sec | 105–123 (foreverchanges) / 107–126 (ElliotWood) | 204–240 / 208–244 | .429 at every rank | High threat, unchanged from Classic in that regard |
| Incinerate (talent) | R3 | 40 (talent) | 325 | 2.5 sec | 201–233 (foreverchanges) / 201–233 (ElliotWood) | n/a, new spell | .714 | +25% damage if target has Immolate; spell IDs 412758/1293812/1293813 confirmed identical across both sources |
| Shadowburn (talent) | R6 | 20 (talent) | 365 | Instant, 15 sec CD | 251–281 (foreverchanges) / 259–288 (ElliotWood) | 450–502 / 462–514 | not stated | Range now 30 yd (was 20 yd); Soul Shard on kill within 8 sec (was 5 sec) |
| Conflagrate (talent) | R6 | 25 (talent) | 255 | Instant, 10 sec CD | 251–313 (foreverchanges) / 251–313 (ElliotWood) | 447–557 (Classic R4 max) | not stated | 6 ranks now (Classic had 4); consumes Immolate; no longer needs Improved Immolate talent |
| Death Coil | R3 | 42 | 600 | Instant, 2 min CD | 454 (foreverchanges) / 460 (ElliotWood) | 470 / 476 | not stated | Heals caster 100% of damage dealt; 3 sec horror |

### Damage-over-time / channel spells

| Spell | Max rank | Lvl learned | Mana | Cast | Total/tick dmg (Forever) | Duration/tick | Total/tick dmg (Classic) | Coef | Notes |
|---|---|---|---|---|---|---|---|---|---|
| Corruption | R7 (book), R6 (trainer) | 4 | 340 / 290 | 2 sec | 438 / 342 total | 18 sec / 3-sec ticks (6 ticks) | 822 total | **.2 per tick at every rank** (was .167 in Classic) | R7 is taught only by Grimoire of Corruption VII (item 21283), a Ruins of Ahn'Qiraj drop in Classic. |
| Bane of Agony (was Curse of Agony) | R6 | 8 | 215 | Instant | 552 total (per tick ~46/8 ticks, builds up) | 24 sec | 1044 total | **.133 per tick at every rank** | Renamed; "Only one **Bane** per Warlock per target", separate slot from Curses (see §3) |
| Bane of Doom (was Curse of Doom) | 1 rank | 60 | 300 | Instant, 1 min CD | 1742 | delayed 1 min | 3200 | **4.0**, "the largest coefficient on any Warlock spell" (ElliotWood) | Renamed; can summon a Doomguard on kill |
| Immolate | R8 (book), R7 (trainer) | 1 | 380 / 370 | 2 sec | Initial 158, DoT 275 / initial 146, DoT 260, over 15 sec | 15 sec | Initial 279, DoT 510 | .2 (initial) / .13 per DoT tick at every rank | Corrected in v8 from the client SpellEffect table (build 1.60.1.69893): this row used to have the two reversed. R8 is taught only by Grimoire of Immolate VIII (item 21282), a Ruins of Ahn'Qiraj drop in Classic. |
| Drain Soul | R4 | 10 | 290 | Channeled | 420 total | 15 sec | 455 total | .1 at every rank | Now grants a Soul Shard chance from *damaging* (not just killing) non-trivial targets while channeling; always grants one on a kill |
| Drain Life | R6 | 14 | 300 | Channeled | 51/sec | 5 sec | 71/sec | .1 at every rank | |
| Siphon Life (talent) | R4 | 30 (talent) | 365 | Instant | 41 per 3 sec | 30 sec | 45 per 3 sec | not stated | |
| Rain of Fire | R4 | 20 | 1185 | Channeled | 880 total | 8 sec | 904 total | .083 per tick (each tick is its own spell, 1282380–1282385) | |
| Hellfire | R3 | 30 | 1300 | Channeled | 206/sec to self and nearby enemies | 15 sec | 208/sec | not stated | Self-damage retained |
| Wrack (talent, new) | 1 rank | talent only | 200 | Channeled | 36/sec | 6 sec | n/a, not in Classic | not stated | +10% damage taken from your other Shadow DoTs on the target; benefits from Improved Drains/Soul Siphon/Pandemic |

### Sustain / utility

| Spell | Max rank | Lvl learned | Effect (Forever) | Effect (Classic) | Notes |
|---|---|---|---|---|---|
| Life Tap | R6 | 6 | Converts **(430 + Spirit)** Health into Mana at rank 6 (Wowhead Forever tooltip 11689 and client data, checked in v8). The earlier "840" reading is not in any current source. **"Spirit increases the amount converted"** | Converts 420 Health → 420 Mana, no Spirit scaling | Base amount roughly doubled at every rank vs. Classic **and** now scales with Spirit, a genuinely new mechanic, not just a number tweak |
| Drain Mana | R4 | 24 | 136 Mana/sec, 5 sec, Channeled, 20 yd | same numbers R2–R4; **R1 differs**: Forever R1 is a real channeled spell (95 mana, 20 yd, 42/sec) vs. Classic's old placeholder (50000 yd instant, no cost) | Forever's R1 was effectively non-functional/PvP-only in Classic; now a real early rank |
| Health Funnel | R7 | 12 | 153 health/sec to pet, 10 sec, Channeled | same values, but now explicitly "generates reduced threat" | Improved Health Funnel talent (moved to tier 1) removes the demon-health floor and can push threat reduction to 100% |
| Create Healthstone | R5 | 10 | Major Healthstone restores **1440** health | restores 1200 | All 5 ranks increased ~20% |
| Create Soulstone | R5 | 18 | resurrect with 2200 health / 2800 mana (top rank) | identical | Unchanged |
| Demon Skin / Demon Armor | R2 / R5 | 1 / 20 | Same armor/regen numbers as Classic, just reworded ("increases health regeneration" instead of "restores X health per 5 sec") |, | No numeric change |

### Fear / crowd control

| Spell | Max rank | Lvl learned | Forever | Classic | Notes |
|---|---|---|---|---|---|
| Fear | R3 | 8 | Up to 20 sec, 15% base mana, 1.5 sec cast | identical | Unchanged |
| Howl of Terror | R2 | 40 | 5 enemies/10 yd, 15 sec, 40 sec CD | identical | Unchanged |

### Curses

| Curse | Max rank | Lvl learned | Forever effect | Classic effect | Notes |
|---|---|---|---|---|---|
| Curse of the Elements | R4 (new R4) | 20 (was 32) | -75 Magic resist, +10% Magic damage taken, 5 min | -75 Fire/Frost resist, +10% Fire/Frost damage taken (old R3 cap) | **Now covers all 6 magic schools**, not just Fire/Frost. **Curse of Shadow no longer exists as a separate spell**, folded into this one (confirmed removed: spell IDs 17862/17937 gone from the beta client). Trained far earlier (lvl 20 vs 32). |
| Curse of Weakness | R6 | 4 | -37 physical damage, 2 min | -31 physical damage | |
| Curse of Recklessness | R4 | 14 | -505 armor, 2 min, **no attack power bonus** | -640 armor, **+90 attack power** | Attack-power-grant removed entirely, now a pure defensive-debuff curse with no PvP risk of buffing the target's damage |
| Curse of Tongues | R2 | 26 | +60% cast time, 30 sec | identical | Unchanged |
| Curse of Exhaustion (talent) | 1 rank | talent | -30% movement speed, 12 sec | -10% movement speed | 3x stronger slow |
| Amplify Curse (talent) | 1 rank | talent | +50% to next Curse of Weakness/Bane of Agony, or +20% to next Curse of Exhaustion, 30 sec | same numbers | Renamed target list only (Curse of Agony → Bane of Agony) |

### New Forever-only Warlock content confirmed

- **Wrack**, new baseline talent DoT (Affliction, tier 6/30-point capstone). See table above.
- **Bane of Havoc**, new Destruction talent (tier 4). 5% base mana, instant, 5 min duration: redirects 15% of all your damage dealt to *other* targets onto this one. Limited to 1 target; also a "Bane," so it competes with Bane of Agony/Doom for the one-Bane-per-target slot.
- **Incinerate**, new Destruction capstone talent (tier 6/30 points). See table above.
- **Demonic Pact**, new Demonology talent (tier 6). Your Demonic Sacrifice buff no longer cancels when you summon a *different* demon (only resummoning the sacrificed one cancels it).
- **Pandemic, Malediction, Soul Harvest, Improved Drains, Malevolence, Nightfall (reworked)**, new/reworked Affliction passives, see §Talents summary below.
- **Demonic Aegis, Demonic Energies, Decimation, Demonic Brand, Improved Felhunter, Demonic Knowledge**, new Demonology passives.
- **Molten Skin, Fire and Brimstone, Shadow and Flame**, new Destruction passives.
- **Summon Felguard**, **[NOT FOUND]**. Does not appear anywhere in the 53-entry Forever beta Warlock spellbook or the 52-entry talent list pulled from builds 1.60.1.69893–70009. If it exists in Forever, it has not surfaced in beta yet; treat the premise as unconfirmed/likely absent.
- **Drain Hope**, **[NOT FOUND]**. No spell or talent by this name in any source checked.

---

## 2. Talents (52 total, all three trees)

**[FOREVER-CONFIRMED]** from ForeverChanges.pro's talent calculator (client build `1.60.1.70009`, wago.tools `TraitNode` export), cross-checked against the ElliotWood/Forever sim project's independent beta-client read (build `1.60.1.69893`), the two agree closely on mechanics, with only build-drift-level numeric differences.

### Tree/point-gating structure, corrects the "16-point gold talent" premise

The beta client's own `aria-description` text on locked talent nodes gives the real gating: **"Requires 5/10/15/20/25/30 points in lower tiers"**, six thresholds for a standard **7-tier tree** (tier 0 free, tiers 1–6 gated at 5/10/15/20/25/30). Each tree's capstone (Affliction: **Wrack**; Demonology: **Demonic Pact**; Destruction: **Incinerate**) sits at tier index 6, i.e. requires **30 points spent in that tree**, exactly like a Classic 51-point tree capstone.

**No source found for a "gold talent unlocked at 16 points" system.** This appears to not match what's in the beta client, treat that framing as unconfirmed/likely incorrect rather than filling it in. **[NOT FOUND / contradicted by client data]**

### Notable talent reworks (rank-1/max-rank text, Forever vs. Classic)

| Talent | Tree/Tier | Forever (max rank) | Classic (max rank) | Change |
|---|---|---|---|---|
| Suppression | Affliction T0 | +5% hit chance, -20% threat (5 ranks) | -10% chance to be resisted (5 ranks) | Completely different effect, now a hit-chance talent, not a resist-reduction talent |
| Improved Corruption | Affliction T0 | -2 sec cast time **and** +10% damage (5 ranks) | -2 sec cast time only | Damage component added |
| Malediction (new) | Affliction T1 | +5% periodic damage from all Warlock spells (5 ranks) | n/a | |
| Soul Harvest (new; Soul Harvesting before the 1 Oct 2026 beta build) | Affliction T1 | On a Drain-Soul kill: 10 sec of 50–100% faster mana regen while casting + 50–100% total regen boost | n/a | |
| Improved Drains (new) | Affliction T1 | Flat +7/13/20% to Drain Life, Drain Soul, Wrack | n/a | Confirmed by ElliotWood as a flat bonus, earlier assumptions of a scaling/speed-up effect were wrong per the client |
| Fel Concentration | Affliction T2 | 23/47/70% pushback resist on Drain Life/Mana/Soul/**Wrack** (3 ranks) | 14/28/42/56/70% (5 ranks) | Fewer ranks, same max value |
| Pandemic (new) | Affliction T2 | +33/67/100% crit damage bonus on Corruption, Bane of Agony, Bane of Doom, Drain Soul, Drain Life, Siphon Life, Wrack | n/a | Huge, this is what makes DoT crit (see §3) actually matter for Affliction |
| Malevolence (new) | Affliction T3 | +1% per point, up to +5% Shadow spell crit chance | n/a | |
| Soul Siphon | Affliction T4 (replaces Improved Drain Life) | +4/8/12% per Affliction effect on target (max 3 stacks → 12/24/36%) to Drain Life/Soul/Wrack | +2/4/6/8/10% flat to Drain Life only | Old drain-speed-up and healing-penalty clauses from Classic **do not exist** in the Forever client |
| Shadow Mastery | Affliction T5 | +1% per point, up to 5%, no longer requires Siphon Life | +2% per point, up to 10%, required Siphon Life | Half the value, prerequisite removed |
| Demonic Sacrifice | Demonology T2 | 2 hr duration; **Imp→+15% Shadow dmg, Voidwalker→+2% mana/4sec, Succubus/Incubus→+15% Fire dmg, Felhunter→+3% health/4sec** | 30 min; Imp→+15% Fire dmg, Voidwalker→+3% health/4sec, Succubus/Incubus→+15% Shadow dmg, Felhunter→+2% mana/4sec | **Pairings are reversed from Classic**, confirmed independently by both ForeverChanges and ElliotWood's sim doc. Anyone sacrificing "the Classic way" will get the wrong buff. |
| Unholy Power | Demonology T0 | +2% per point (5 ranks) pet **all-damage** | +4% per point (5 ranks) pet **melee-only** damage | Moved from tier 4 to tier 0; now applies to spell damage too, not just melee |
| Master Demonologist | Demonology T5 | Imp +Fire dmg, Voidwalker -Physical dmg taken, Succubus/Incubus +Shadow dmg, Felhunter -Magic dmg taken (2%/rank, 5 ranks); no longer requires Unholy Power | Imp -threat, Voidwalker -physical dmg taken, Succubus/Incubus +all dmg, Felhunter +resist/level | Completely reworked effects per pet; ElliotWood confirms Voidwalker's line reduces **Physical only**, not "all damage" |
| Fel Domination | Demonology T3 | -5.5 sec cast, -50% mana on next summon, **5 min cooldown** | same effect, **15 min cooldown** (per ElliotWood's Classic-sim baseline) | Cooldown cut to 1/3 |
| Ruin | Destruction T2 | +20% per point, up to 100% crit damage (5 ranks), no longer needs "Devastation" prereq | flat 100% (1 rank), required Devastation | Now gradual across 5 ranks instead of an all-or-nothing 1-point talent |
| Bane (cast-time reduction) | Destruction T0 | Also reduces **Incinerate** cast time, not just Shadow Bolt/Immolate/Soul Fire | Shadow Bolt/Immolate/Soul Fire only | |

Full rank text for all 52 talents (Affliction: Improved Life Tap, Suppression, Improved Corruption, Malediction, Soul Harvest, Improved Drains, Improved Bane of Agony, Fel Concentration, Amplify Curse, Pandemic, Malevolence, Nightfall, Curse of Exhaustion, Siphon Life, Soul Siphon, Shadow Mastery, Wrack; Demonology: Improved Health Funnel, Improved Imp, Demonic Embrace, Unholy Power, Demonic Aegis, Improved Voidwalker, Fel Vitality, Demonic Energies, Improved Sayaad, Demonic Sacrifice, Master Summoner, Decimation, Fel Domination, Demonic Brand, Improved Felhunter, Soul Link, Demonic Knowledge, Master Demonologist, Demonic Pact; Destruction: Destructive Reach, Improved Shadow Bolt, Bane, Molten Skin, Cataclysm, Aftermath, Ruin, Shadowburn, Intensity, Agonizing Flames, Conflagrate, Pyroclasm, Bane of Havoc, Fire and Brimstone, Shadow and Flame, Incinerate) was pulled and cross-checked; ask if the complete per-rank table for any specific talent not shown above is needed.

---

## 3. Combat rules

| Rule | Status | Detail | Source |
|---|---|---|---|
| **DoTs/periodic effects can crit** | **[FOREVER-CONFIRMED]** | "Periodic damage can crit: dots and bleeds roll for critical strikes using the snapshot crit chance." Ignite-style exceptions carry an explicit no-periodic-crit flag; nothing suggests Warlock DoTs are excepted. | ElliotWood/Forever `forever_rules.md` (reads BlizzCon tooltip wording, Pandemic's existence as a talent is itself evidence); independently confirmed qualitatively by Icy Veins beta testing ("DoTs can now critically strike, this is one of the largest overall Warlock mechanical changes") |
| **DoT crit damage multiplier** | **[FOREVER-CONFIRMED]** via talent, not base rule | Base DoT crit bonus is **not separately stated**; Pandemic talent (Affliction T2) explicitly adds +33/67/100% *crit damage bonus* on top of whatever the base is, for Corruption/Bane of Agony/Bane of Doom/Drain Soul/Drain Life/Siphon Life/Wrack. Ruin (Destruction T2) does the same for all Destruction spells (+20/40/60/80/100%). This implies a talent-free DoT crit bonus exists but its base value is **[NOT FOUND]** in any source, likely the same +50% "spell crit" default noted below, but not directly confirmed for periodic effects specifically. | ForeverChanges talent data |
| **Spell crit multiplier (direct damage)** | **[FOREVER-CONFIRMED]**, equals Classic's value | Spell crits deal **+50% bonus damage (1.5×)** by default. Melee crits deal **+100% bonus (2×)** by default. Crit is now a single unified stat, not split melee/spell. | Warcraft Tavern Stats & Attributes Guide (Forever-specific page) |
| **Unified hit and crit** | **[FOREVER-CONFIRMED]**, mechanism specified | An item's melee/spell hit *and* crit values are **summed and paid into both pools**, one stat now covers melee, ranged, and spell (poisons/traps included per the BlizzCon panel). Attribute-to-rating conversions are unchanged. | ElliotWood `forever_rules.md` (`unifyEquipHitAndCrit`); confirmed by BlizzCon panel via Output Lag ("Hit chance is unified... Critical strike chance is merged the same way") and Method.gg ("Stats such as Hit and Critical Strike Chance will now be applied to Melee Ranged and Spell Hit, instead of being separated") |
| **Haste and DoT ticks** | **[FOREVER-TESTED, current beta build]** | "DoTs and Drain channels are **not currently affected by Haste** in this build. Haste still affects normal spellcasting." Stated explicitly as a current-build observation, not a designed-permanent rule, could change before launch. | Icy Veins beta hands-on |
| **Haste on gear** | **[FOREVER-TESTED, current beta build]** | As of the Warcraft Tavern stats guide's writing, Haste was **not yet found on any acquired gear**, so its full behavior (including whether it affects drains) can't be fully verified yet. Skyborne's "Wind Blessed" passive and the Troll "Berserking" racial do grant a Haste-like buff already. | Warcraft Tavern Stats & Attributes Guide |
| **Spell Power exists as a discrete stat** | **[FOREVER-CONFIRMED]** | Orc Blood Fury: "increases your Spell Power by 10% for 15 seconds" (was a mana-cost-reduction/other effect in Classic). Example item "Hide of the Wild" (lvl 57 cloak) grants "+42 healing and +14 damage for all spells" as separate healing/damage rolls. Create Firestone/Spellstone grant flat Fire/Shadow spell damage plus Crit%/Haste%. | Icy Veins (racial); Output Lag (BlizzCon panel item card); ForeverChanges spellbook (Firestone/Spellstone tooltips) |
| **Spell hit cap vs. raid bosses** | **[FOREVER-CONFIRMED]** | Base miss chance: spells **3%** vs. an equal-level target, **16%** vs. a raid-boss-level target (melee: 5%/9%). So **16% Hit** is the stated cap to never miss a raid boss with a spell. (Note: a hit-cap figure of "17%" appears in some unsourced stat-priority write-ups, that number was **not corroborated** by any primary source checked here; treat 16% as the sourced figure.) | Warcraft Tavern Stats & Attributes Guide |
| **Resist mechanics** | **[FOREVER-CONFIRMED]** | 5 resistance schools (Arcane/Fire/Frost/Nature/Shadow, no Holy resist). Caps at **75% damage reduction**, reached at **315 Resistance** against a raid boss (level 63-equivalent). Curse of the Elements now reduces *all 6* schools' resistance at once (see §1). | Warcraft Tavern Stats & Attributes Guide |
| **5-second rule (no mana regen while casting)** | **[NOT FOUND, likely unchanged]** | No Forever-specific source confirms or denies this mechanic by name. The ElliotWood rules diff (which lists every rule Forever changes from Classic) does **not** mention the 5-second rule anywhere, and the Warcraft Tavern stat guide describes Spirit regen as working "out of combat and/or not casting" in the same shape as Classic's 5SR/Meditation framing. Treat as **[CLASSIC VALUE, unconfirmed for Forever]** by absence rather than direct confirmation. | Absence of any changelog entry; Warcraft Tavern Spirit description |
| **Spirit regen formula (exact numbers)** | **[NOT FOUND]** | No source gives the actual Mana-per-5-sec-per-Spirit formula for Forever. Only qualitative confirmation that Spirit "increases Health and Mana Regeneration while out of combat and/or not casting," and is explicitly called out as now feeding **Life Tap** too (new, see §1). | Warcraft Tavern Stats & Attributes Guide |
| **Life Tap formula/scaling** | **[FOREVER-CONFIRMED]** | Base conversion amounts roughly doubled vs. Classic at every rank (see §1 table), **and** the amount converted now scales with Spirit, an entirely new mechanic not present in Classic Life Tap. Exact Spirit coefficient: **[NOT FOUND]**. | ForeverChanges spellbook tooltip text ("Spirit increases the amount converted"); Icy Veins ("Life Tap has changed drastically... now benefits from Spirit") |
| **"Gold talent at 16 points" system** | **[NOT FOUND / contradicted]** | See §2, the real gating is a standard 7-tier, 5/10/15/20/25/30-point tree, not a 16-point unlock. | ForeverChanges talent calculator `aria-description` data, client build 1.60.1.70009 |
| **Banes vs. Curses, separate one-per-target limits** | **[FOREVER-CONFIRMED]** | Every Bane spell (Bane of Agony, Bane of Doom, Bane of Havoc) carries its own tooltip clause: *"Only one Bane per Warlock can be active on any one target."* Every Curse spell (Curse of Weakness, Curse of Recklessness, Curse of the Elements, Curse of Tongues, Curse of Exhaustion) carries the separate clause: *"Only one Curse per Warlock can be active on any one target."* **This means a Warlock can now have one Bane AND one Curse active on the same target simultaneously**, in Classic, Curse of Agony/Doom shared the single "one curse" slot with every other curse. This is a genuine mechanical split, not just a rename. | ForeverChanges spellbook, tooltip text for every Bane/Curse spell, cross-checked |
| **Soul Shards** | **[FOREVER-CONFIRMED]** | A new dedicated reagent bag slot exists and can hold Soul Shards, freeing main-bag space. Shards **still do not stack** even in the reagent slot, stacking was reported as a top community wish-list item that did **not** make it in as of the tested build. Drain Soul now grants a shard chance from *damaging* (not just killing) a non-trivial target while channeling, and always grants one on a kill. | Icy Veins beta hands-on |
| **Healthstones** | **[FOREVER-CONFIRMED]** | All 5 ranks of Create Healthstone heal ~20% more than Classic (top rank 1440 vs. 1200). Mechanically unchanged otherwise. | ForeverChanges spellbook |
| **Soulstones** | **[FOREVER-CONFIRMED]** | Numerically identical to Classic at every rank (top rank: 2200 health/2800 mana resurrection). | ForeverChanges spellbook |
| **World buffs disabled in raids** | **[FOREVER-CONFIRMED]**, general (not Warlock-specific) | Rallying Cry, Songflower, Darkmoon Faire, Warchief's Blessing, Dire Maul tribute, and Spirit of Zandalar are explicitly disabled inside raid instances. Relevant to any Warlock DPS/sustain planning that assumes classic world-buff stacking. | ElliotWood `forever_rules.md`, sourced to a 13 Sep 2026 demo report |

---

## 4. Stats and gear

**[FOREVER-CONFIRMED]**, primarily from the BlizzCon 2026 "Deep Dive" panel (Kris Zierhut, Principal Game Designer for Combat, Items, Classes and Talents), reported independently by Output Lag and Method.gg, both citing the same panel:

- **Stats on gear, per the panel's own "Items and Gear: Stats" slide:** Hit Chance, Crit Chance, Weapon Skill, Bonus Healing, Expertise. Spell Power/spell damage is not on that specific slide list but is directly confirmed elsewhere (item examples, Blood Fury, Firestone/Spellstone), see §3.
- **Hit and Crit are unified** across melee/ranged/spell (see §3), this is the single biggest itemization change relevant to a Warlock, since Warlocks previously itemized Spell Hit/Spell Crit specifically and now share a pool with every other attack type on the item.
- **Weapon Skill is "severely nerfed"**, Zierhut: "a little too easy to get and a little too strong" in Classic; "you can't get quite as much on a single item as you used to, but you can get it." No per-item cap number was given in the panel itself.
- **Expertise is new**, replacing most of Weapon Skill's old role, working "similarly to how it did in The Burning Crusade" (reduces chance to be dodged/parried). Not directly relevant to a caster Warlock's own damage, but matters for pet melee threat/uptime discussions.
- **Resilience does NOT exist in Forever**, explicitly stated by Zierhut ("I'll say we're not adding resilience").
- **Bonus Healing gear now also carries Spell Power/damage.** Exact formula (ElliotWood sim, reading the client): `SpellDamage += HealingPower / 3`. Concretely demonstrated on the example item "Hide of the Wild" (lvl 57 cloak, +10 Int, +8 Sta, +42 healing, **+14 damage for all spells**).
- **Caster weapons (wands/staves) grant spell damage and healing starting around level 10**, much earlier than Classic. Relevant to early-leveling Warlock damage math.
- **Example itemized pieces shown on the panel** (none are Warlock class items specifically, but illustrate the new stat template): Lionheart Helm (lvl 56 plate, +18 Str, 2.0% Hit, 2.0% Crit, both unified figures on one line), Edgemaster's Handguards (lvl 44 mail, -1.0% chance to be dodged/parried, new Expertise-style stat), Staff of Westfall (biome-conditional, +48 healing/+16 spell damage/+2% move speed in specific zones), Rune of Perfection (trinket, +2 magic resist piercing, +3 more in forest/woodland biomes), Worgenbane Talisman (species-conditional stun trinket), X'caliboar (lvl 37 two-hand sword, on-hit Holy proc, tripled vs. Undead/Swine).
- **Warlock tier set bonuses:** **[NOT FOUND]**. No source located publishes Warlock-specific raid tier set bonuses for Forever. This is expected, the beta testing referenced here was capped around level 38 and raid content (Tier 1: Barrow Deeps, Hyjal Summit, Onyxia's Lair) doesn't open until 9 December 2026, over a month after the 4 Nov launch, per the ElliotWood encounter notes. Method.gg mentions "item sets such as Blackened Leather and Embrace of the Viper have new set bonuses" but these read as leveling greens/blues, not confirmed raid tier sets, and neither is Warlock-specific.
- **Itemization pass generally:** rare-spawn and epic world drops were redesigned to remove "bad" epics; new quest-reward items are being added throughout leveling zones (e.g., a new Ladimore Heirloom Ring possibly tied to the Mor'Ladim chain in Duskwood).

---

## 5. Pets / Demons

- **Demons now scale with the Warlock's own stats**, **[FOREVER-TESTED]**: "Warlock demons now scale with the Warlock's stats, making them deal much more damage and become much tankier." This mirrors the "Hunter pets now scale with player stats" mechanic referenced in the task prompt, Warlocks get the same treatment. Exact scaling formula/coefficients: **[NOT FOUND]**.
- **Per-pet beta impressions [FOREVER-TESTED, level ~38 demo, subject to rebalancing]:**
  - **Imp**, ranged Fire damage + Blood Pact group support. Fragile, and **ran out of Mana quickly** in testing, flagged as needing tuning.
  - **Voidwalker**, defensive/threat pet. Generated "an extraordinary amount of threat," at times out-threatening the actual tank.
  - **Succubus**, melee damage pet, by far the strongest DPS pet tested, credited with **roughly 23–25% of the Warlock's total damage** in the BlizzCon demo. Also brings Seduction utility.
  - **Felhunter**, utility-focused (Spell Lock interrupt, Devour Magic dispel), damage roughly between Imp and Succubus.
- **Demon base ability numbers found [FOREVER-CONFIRMED, ElliotWood sim client-read]:**
  - **Imp, Firebolt**, 7 ranks: 4–5, 7–9, 12–14, 18–19, 26–28, 36–39, 43–48 damage. (Classic: 7–10 up to 85–96, roughly halved, matching the general Warlock damage rebalance.)
  - **Succubus, Lash of Pain**, 6 ranks: 16, 22, 30, 36, 43, 50 damage. (Classic: 33 up to 99, also roughly halved.)
  - **Voidwalker (Torment, Consume Shadows, Sacrifice, Suffering) and Felhunter (Tainted Blood, Devour Magic, Paranoia, Spell Lock) base numbers: [NOT FOUND]**, these are largely non-damage/utility/threat spells and weren't captured by either datamining pass used here; only their talent-modifier percentages are confirmed (below).
- **Demonic Sacrifice pairings are REVERSED from Classic**, confirmed independently by two sources (see §2 talent table). This is the single most important pet-related gotcha for anyone porting Classic muscle memory: sacrificing the Imp now buffs **Shadow** damage (not Fire), sacrificing the Succubus now buffs **Fire** damage (not Shadow).
- **Pet-boosting talent percentages confirmed:**
  - Fel Vitality: +5/10/15% max Health & Mana to all pets, +5/10/15% Warlock max Mana (3 ranks; was 5 ranks/Mana-only in Classic as "Fel Intellect").
  - Improved Imp: +10/20/30% Firebolt damage and Fire Shield effect (Blood Pact dropped from this talent's scope vs. Classic).
  - Improved Voidwalker: +10/20/30% to Torment/Consume Shadows/Sacrifice/Suffering (unchanged from Classic).
  - Improved Sayaad (Succubus/Incubus): +10/20/30% Lash of Pain/Soothing Kiss, +10/20/30% Seduction/Lesser Invisibility duration (unchanged from Classic).
  - Improved Felhunter (new): +10/20/30% Tainted Blood/Devour Magic/Paranoia effectiveness, -2/4/6 sec Spell Lock cooldown.
  - Demonic Energies (new): pet healed for 8/15% of your spell damage dealt; pet gets 50/100% of the Mana you gain from Life Tap.
  - Unholy Power: now +2/4/6/8/10% to **all** pet damage (was melee-only in Classic), moved to tier 0.
  - Demonic Knowledge (new): +33/67/100% of your character level as spell damage to **both you and your pet**, only while a demon is summoned.
- **Soul Link (talent):** unchanged numerically from Classic, 30% of damage taken redirected to the active demon, both deal +3% more damage while active. Moved from tier 7 to tier 5 (Demonology) in the new tree layout.

---

## 6. Open questions (things this pass could not confirm)

1. **DoT crit base damage multiplier** (as opposed to the Pandemic/Ruin talent bonuses on top of it), not directly stated anywhere found.
2. **Exact Spirit → mana regen formula**, and whether the classic 5-second rule is intact by name, not directly confirmed either way, only inferred by absence of a changelog entry.
3. **Haste's final behavior on DoTs/drains**, explicitly called out by Icy Veins as a "current build" state that could still change before launch; Haste wasn't even on testable gear yet as of the Warcraft Tavern guide.
4. **Warlock raid tier set bonuses**, don't exist yet in any source; raid content doesn't open until 9 Dec 2026, after the 4 Nov launch.
5. **Voidwalker and Felhunter base ability numbers** (Torment threat value, Consume Shadows shield amount, Suffering AoE numbers, Tainted Blood AP-reduction amount, Devour Magic heal amount, Paranoia detection range/duration, Spell Lock silence duration/cooldown), only their talent modifier percentages were found, not their own base tooltip numbers.
6. **Summon Felguard and "Drain Hope"**, do not appear in any Forever Warlock spellbook or talent data pulled; likely not in the game, but this is an absence-of-evidence conclusion, not a direct denial from Blizzard.
7. **The "gold talent at 16 points" framing** in the original task brief does not match the confirmed 7-tier/5-10-15-20-25-30-point structure, flagging this as a likely misconception to correct rather than a gap to fill.
8. **Exact spell power scaling formula for demons** (how much of the Warlock's own Spell Power/Intellect translates to pet damage), only the qualitative "demons scale with your stats" claim was found, no formula.
9. **Precise weapon-skill-to-Expertise conversion or caps**, panel gave no numbers; Output Lag explicitly notes the panel "gave no conversion numbers for the unified stats, no per-item cap for weapon skill."

---

## 7. Sources

- ForeverChanges.pro, Warlock spellbook: https://foreverchanges.pro/spellbook/warlock (client build 1.60.1.70009, wago.tools TraitNode export)
- ForeverChanges.pro, Warlock talent calculator: https://foreverchanges.pro/talents/warlock (same build)
- ForeverChanges.pro, Warlock class changes vs. Classic: https://foreverchanges.pro/class/warlock
- Icy Veins, Warlock Class Guide, WoW Forever: https://www.icy-veins.com/wow-forever/warlock-class-overview
- Warcraft Tavern, Stats & Attributes Guide, WoW Forever: https://www.warcrafttavern.com/forever/guides/stats/
- Output Lag, "World of Warcraft Forever unifies hit and crit stats and gives healing gear bonus damage": https://outputlag.com/news/world-of-warcraft-forever-unifies-hit-and-crit-stats-and-gives-healing-gear-bonus-damage/
- Method.gg, "World of Warcraft: Forever Itemization (Expertise, Spell Damage & More!)": https://www.method.gg/wow-classic/itemization-updates-in-world-of-warcraft-forever-expertise-spell-damage-more
- ElliotWood/Forever (GitHub, wowsims fork), Warlock beta-client pass doc: https://github.com/ElliotWood/Forever/blob/master/docs/beta-pass/warlock.md (client build 1.60.1.69893)
- ElliotWood/Forever, general Forever ruleset changes doc: https://github.com/ElliotWood/Forever/blob/master/docs/forever_rules.md
- ElliotWood/Forever, PR #190 description (Warlock spells/talents beta update): https://github.com/ElliotWood/Forever/pull/190
- ElliotWood/Forever, data-changes changelog directory (build-by-build tracking): https://github.com/ElliotWood/Forever/tree/master/docs/data-changes
- wowsims/forever, GitHub issue #32, "[Class] Warlock talents and abilities for Forever": https://github.com/wowsims/forever/issues/32 (referenced, not deep-dived)

### Sources tried but not usable
- https://www.wowhead.com/forever/spells/abilities/warlock, page requires interactive filtering, no static spell data retrievable via fetch.
- https://wowforevertalent.com/abilities/warlock/, same issue, interactive-only spell list, no static tooltip data retrievable.
- https://wowforevertalents.com/abilities/warlock/, not checked directly (likely a mirror/typo domain of the above; skipped after wowforevertalent.com returned no usable data).
- https://mobalytics.gg/wow-forever/, not deep-fetched; surfaced in search results but ForeverChanges/Icy Veins/ElliotWood provided more direct client data.
- https://lfcarry.com/guides/wow-forever-class-changes, not fetched, redundant with sources already gathered.
- https://wowforeverbuilds.com, not found in search results under this exact domain.
- https://www.foreverwisp.com/guides/wow-forever-warlock-beta-levelling-changes, surfaced in search, not deep-fetched (time/budget prioritized the client-data sources above).
- https://wowhandbook.com, surfaced in search results, not deep-fetched.
- https://conquestcapped.com/guides/wow-forever/, surfaced in search results (talent-specific subpage), not deep-fetched.
- us.forums.blizzard.com (official forums), not searched directly; not needed given the panel transcript and client-data sources obtained.
- reddit r/classicwow, not searched directly given the strength of the datamined sources found.
- https://www.icy-veins.com/wow-forever/ (general index), the Warlock-specific subpage was used instead; general index not separately fetched.
