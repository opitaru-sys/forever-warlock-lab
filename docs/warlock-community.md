# WoW: Forever, Warlock Community Survey

> These are raw research notes written by AI research agents (Claude) for this lab. "The brief" or "your task brief" means the research instructions those agents were given, not a published source. Numbers here were cross-checked before use on the page.

Compiled 28 Sep 2026. Scope: WoW: Forever beta (started 17 Sep 2026, cap 20 rising to ~30 around 1 Oct, launch 4 Nov 2026). Excludes WoW Classic (2019) and retail.

**1 Oct 2026 update:** the beta notes of 1 Oct 2026 renamed the talent Soul Harvesting to Soul Harvest. The notes below keep the old name, as their sources used it.

**Methodology note / reliability caveat:** icy-veins.com, mobalytics.gg, and barrens.chat returned HTTP 403 to direct page fetches (as expected per the task brief), everything attributed to them below comes from search-engine snippets/AI-search-summaries, not a verified direct read of the page, and should be treated as lower-confidence than the wowforeverbuilds.com and Blizzard-forum material, which was read directly. Where a search-summary and a directly-fetched page disagreed on the same build, both are recorded with their source.

---

## 1. Published builds

### 1a. Affliction, Beta Level 20 leveling ("DoTs that crit")
- **Source:** wowforeverbuilds.com/guide/beta-20-affliction-warlock-leveling, **guide claim** (page fetched directly)
- **Allocation (11 pts, all Affliction):** Improved Corruption 5/5 → Soul Harvesting 2/2 → Malediction 3/5 → Pandemic 1/3
- **Level order:** 10–14 Improved Corruption 5/5; 15–16 Soul Harvesting 2/2; 17–19 Malediction 3/5; 20 Pandemic 1/3
- **Reasoning quoted:** "Corruption casts 2 sec faster (instant at 5 points) and deals 10% more damage." Soul Harvesting, "Killing a target while Drain Soul is on it gives Soul Harvest, letting your mana regenerate at full rate for 20 sec." Pandemic, "Increases the critical strike bonus of your DoTs" and "DoTs can crit in Forever."
- **Playstyle:** "Send the Voidwalker in, then Bane of Agony and Corruption." Life Tap between pulls, Drain Life to recover.
- **Contradicting variant reported elsewhere for the same "beta level 20" build** (source: barrens.chat forum thread and an unnamed WebSearch synthesis, both **player report / guide claim**, not independently verified by direct fetch): 11/0/0 with Improved Corruption 5/5, Suppression 4/5, Soul Harvesting 1/2, Improved Life Tap 1/2. Barrens.chat poster "Zephan" (via Warcraft Tavern) specifically emphasizes Suppression 4/5 for hit-cap + threat reduction, arguing wands now scale with Spell Power so Destruction talents aren't worth it yet at 20.

### 1b. Affliction, "Drain Tank" leveling, 10–60
- **Source:** wowforeverbuilds.com/guide/affliction-drain-tank-warlock-leveling, **guide claim** (fetched directly)
- **Final allocation: 41/10/0**
  - Affliction (41): Improved Corruption 5/5, Suppression 5/5, Improved Life Tap 2/2, Improved Drains 3/3, Soul Harvesting 2/2, Fel Concentration 3/3, Amplify Curse 1/1, Nightfall 2/2, Siphon Life 1/1, Soul Siphon 3/3, Improved Bane of Agony 2/2, Shadow Mastery 5/5, Drain Hope 1/1, Malediction 5/5, Curse of Exhaustion 1/1
  - Demonology (10): Demonic Embrace 5/5, Improved Voidwalker 3/3, Fel Vitality 2/3
- **Reasoning quoted:** "Improved Corruption 5/5 first because Corruption becomes instant and deals 10% more damage: cast it while moving." "Improved Life Tap 2/2 and Soul Harvesting 2/2 form the drain-tank loop... finish mobs with Drain Soul to cast with full mana regeneration for 20 sec." "Fel Concentration 3/3 at 22... protects casts as well as channels, so Drain Life survives three mobs chewing on you."
- **Playstyle:** "Put your damage over time spells on two or three mobs, let the Voidwalker hold them, and channel Drain Life to heal while they die."

### 1c. Demonology, "Voidwalker Tank" leveling, 1–40
- **Source:** wowforeverbuilds.com/guide/demonology-voidwalker-warlock-leveling, **guide claim** (fetched directly)
- **Allocation (level 40): Affliction 5 / Demonology 26 / Destruction 0** (page's own site-wide summary elsewhere calls this range "1–40")
  - Affliction (5): Improved Corruption 5/5
  - Demonology (26): Demonic Embrace 5/5, Improved Voidwalker 3/3, Fel Vitality 3/3, Unholy Power 5/5, Master Summoner 2/2, Fel Domination 1/1, Demonic Energies 2/2, Demonic Sacrifice 1/1, Demonic Knowledge 3/3, Soul Link 1/1
- **Level order:** 10–14 Imp. Corruption 5/5; 15–19 Demonic Embrace 5/5; 20–22 Imp. Voidwalker 3/3; 23–25 Fel Vitality 3/3; 26–27 Unholy Power 2/5; 28–29 Master Summoner 2/2; 30 Fel Domination 1/1; 31–32 Demonic Energies 2/2; 33 Demonic Sacrifice 1/1; 34–36 Unholy Power (to 5/5); 37–39 Demonic Knowledge 3/3; 40 Soul Link 1/1
- **Reasoning quoted:** "The Voidwalker tanks, your DoTs do the damage, and your demon keeps absorbing hits that would kill another cloth wearer." "Soul Link moves 30% of the damage you take onto your demon." "Demonic Energies heals the Voidwalker as you fight and gives it your Life Tap mana."
- **Rotation:** "Send the pet in first and let it Torment once or twice before you cast anything," then Corruption + Bane of Agony, then wand.
- **Stated tradeoffs:** "Lower personal damage than Affliction or Destruction"; "Pet dependent. A dead or out-of-range Voidwalker leaves you fragile."

### 1d. Destruction, "Shadow Bolt nuke" leveling, 30–60
- **Source:** wowforeverbuilds.com/guide/destruction-shadow-bolt-warlock-leveling, **guide claim** (fetched directly)
- **Final allocation: 17/0/34**
  - Affliction (17): Improved Corruption 5/5, Improved Life Tap 2/2, Suppression 5/5, Malediction 3/5, Nightfall 2/2
  - Destruction (34): Improved Shadow Bolt 5/5, Bane 5/5, Molten Skin 3/5, Ruin 5/5, Shadowburn 1/1, Cataclysm 3/3, Conflagrate 1/1, Shadow and Flame 5/5, Intensity 3/3, Agonizing Flames 3/3
- **Level order:** 10–14 Imp. Corruption; 15–19 Imp. Shadow Bolt; 20–24 Bane; 25–26 Imp. Life Tap; 27–29 Molten Skin; 30–34 Ruin; 35 Shadowburn; 36–38 Cataclysm; 39 Conflagrate; 40–44 Shadow and Flame; 45–50 Intensity/Agonizing Flames; 51–60 Suppression, Malediction, Nightfall
- **Reasoning quoted:** "Shadow Bolt crits make the target take 20% more Shadow damage from you for 60 sec" (Improved Shadow Bolt). "Ruin doubles the critical strike damage bonus of Destruction spells." "Most mobs die before they reach you, so your pet rarely needs to tank."
- **Rotation:** "Instant Corruption on the target, then Immolate from maximum range and Conflagrate when it lands," repeat Shadow Bolt, "Shadowburn if the mob is about to reach you" as finisher.
- **Stated weaknesses:** higher mana cost, weak vs multiple enemies without CC.

### 1e. Affliction, Dungeon "Shadow Cleave", 40–60
- **Source:** wowforeverbuilds.com/guide/shadow-cleave-affliction-warlock-dungeon-leveling, **guide claim** (fetched directly)
- **Allocation: 46 Affliction / 5 Demonology / 0 Destruction**
  - Early (10–19): Improved Corruption 5/5, Suppression 5/5
  - Mid (20–32): Malediction 5/5, Improved Bane of Agony 2/2, Pandemic 3/3, Nightfall 2/2
  - Late (33–60): Malevolence 5/5, Siphon Life, Shadow Mastery 5/5, Drain Hope, Soul Siphon 3/3, Curse of Exhaustion, Improved Life Tap, Soul Harvesting, Improved Drains 3/3, Demonic Embrace 5/5
- **Reasoning quoted:** "Instant Corruption is the whole plan", cast-time Corruption "cannot tab through five mobs before the tank loses threat." Suppression: "+5% hit and 20% less threat on everything." Pandemic "makes the crits from those spells hit far harder by doubling critical damage bonuses on damage-over-time effects."
- **Pull rotation:** wait for third tank Swipe → Corruption on every mob (furthest first, skip already-low) → Bane of Agony on longest-living mobs, Siphon Life on the kill target → instant Shadow Bolts off Nightfall procs → Curse of Exhaustion on fleeing mobs.

### 1f. Affliction, Raid PvE, level 60, "Drain Hope and DoT raid build"
- **Source:** wowforeverbuilds.com/guide/affliction-warlock-pve-guide, **guide claim** (fetched directly)
- **Allocation: 40/11/0**
  - Affliction (40): Suppression 5/5, Improved Corruption 5/5, Malediction 5/5, Improved Drains 3/3, Improved Bane of Agony 2/2, Pandemic 3/3, Malevolence 5/5, Nightfall 2/2, Siphon Life 1/1, Soul Siphon 3/3, Shadow Mastery 5/5, Drain Hope 1/1
  - Demonology (11): Improved Health Funnel 2/2, Demonic Embrace 5/5, Fel Vitality 3/3, Demonic Sacrifice 1/1
- **Reasoning quoted:** Suppression is "the hit talent every Affliction build starts with" since resisted DoTs = lost duration damage. Pandemic "doubles the crit bonus of Corruption, Bane of Agony, Bane of Doom, the drains, Siphon Life and Drain Hope", the guide frames this as fixing the Classic limitation where DoTs couldn't crit. Drain Hope "makes your other Shadow damage over time on the target 10% stronger" during its 6-sec channel. "Bane of Agony for damage plus the raid Curse the leader assigns now occupy separate debuff slots, unlike Classic."
- **Rotation:** sacrifice Imp pre-pull (+15% Shadow dmg) → assigned Curse + Bane of Agony together → maintain Corruption + Siphon Life → Drain Hope when up → filler Shadow Bolt/Drain Soul (Improved Drains triples below 60% target HP on Drain Soul) → instant Shadow Bolt on Nightfall.

### 1g. Demonology, Raid PvE, level 60, "Demonic Pact / Master Demonologist"
- **Source:** wowforeverbuilds.com/guide/demonology-warlock-pve-guide, **guide claim** (fetched directly)
- **Allocation: 0/31/20**
  - Demonology (31): Demonic Embrace 5/5, Unholy Power 1/5, Demonic Aegis 2/2, Fel Vitality 3/3, Improved Sayaad 3/3, Demonic Sacrifice 1/1, Master Summoner 2/2, Decimation 2/2, Demonic Energies 2/2, Soul Link 1/1, Demonic Knowledge 3/3, Master Demonologist 5/5, Demonic Pact 1/1
  - Destruction (20): Destructive Reach 2/2, Improved Shadow Bolt 5/5, Cataclysm 3/3, Bane 5/5, Ruin 5/5
- **Core interaction quoted:** "Your Demonic Sacrifice buff is no longer cancelled when you summon a different demon, so you can sacrifice the Imp for 15% Shadow damage, then summon a Succubus", stacking "Demonic Sacrifice, Master Demonologist, Soul Link and Demonic Knowledge" concurrently. Soul Link gives "3% more damage" plus redirects "30% of your damage taken" to the pet. Master Demonologist: "10% more Shadow damage" with Succubus/Incubus out. Improved Shadow Bolt crits: "target take[s] 20% more Shadow damage from you for 60 sec."
- **Uncertainty flagged by the guide itself:** "Demonic Pact is new, so how it behaves with Soul Link and dismissed pets needs beta testing", i.e. buff-persistence-through-pet-death/dismiss is explicitly unresolved.

### 1h. Destruction, Raid PvE, level 60, "Shadow and Flame / Ruin / Incinerate"
- **Source:** wowforeverbuilds.com/guide/destruction-warlock-pve-guide, **guide claim** (fetched directly)
- **Allocation: 9/11/31**
  - Affliction (9): Improved Life Tap 2/2, Suppression 5/5, Malediction 2/5
  - Demonology (11): Demonic Embrace 5/5, Demonic Aegis 2/2, Fel Vitality 3/3, Demonic Sacrifice 1/1
  - Destruction (31): Destructive Reach 1/2, Improved Shadow Bolt 5/5, Cataclysm 3/3, Bane 5/5, Ruin 5/5, Shadowburn 1/1, Shadow and Flame 5/5, Conflagrate 1/1, Bane of Havoc 1/1, Agonizing Flames 3/3, Incinerate 1/1
- **Reasoning quoted:** "Conflagrate grants +10% Shadow damage and Shadowburn +10% Fire damage for 100 sec; Conflagrate keeps Immolate [running]" (Shadow and Flame). "Ruin doubles the crit damage bonus of Destruction spells" and is "the core of the build." Incinerate "hits harder on targets with Immolate," used as a resist-fallback.
- **Rotation:** sacrifice Imp → assigned Curse + Immolate → Conflagrate to start the 100-sec Shadow-damage buff.

### 1i. Affliction, PvP, level 60, "Soul Link / Curse of Exhaustion drain"
- **Source:** wowforeverbuilds.com/guide/affliction-warlock-pvp-guide, **guide claim** (fetched directly)
- **Allocation: 30/21/0**
  - Affliction (30): Suppression 2/5, Improved Corruption 5/5, Malediction 3/5, Improved Bane of Agony 1/2, Fel Concentration 3/3, Amplify Curse 1/1, Malevolence 4/5, Nightfall 2/2, Curse of Exhaustion 1/1, Siphon Life 1/1, Soul Siphon 2/3, Shadow Mastery 5/5
  - Demonology (21): Improved Health Funnel 2/2, Demonic Embrace 5/5, Demonic Aegis 2/2, Fel Vitality 3/3, Improved Sayaad 2/3, Demonic Sacrifice 1/1, Master Summoner 2/2, Fel Domination 1/1, Demonic Energies 2/2, Soul Link 1/1
- **Reasoning quoted:** "Curse of Exhaustion and Bane of Agony can sit on the same target", "a slowed enemy is also taking damage." Fel Concentration + Soul Link: "Drain Life and Drain Soul are much harder to push back or interrupt with damage." Nightfall: "an instant Shadow Bolt while you drain or dot: surprise burst."

### 1j. Demonology, PvP, level 60, "Felhunter / Soul Link survival"
- **Source:** wowforeverbuilds.com/guide/demonology-warlock-pvp-guide, **guide claim** (fetched directly)
- **Allocation: 16/35/0**
  - Affliction (16): Improved Corruption 5/5, Malediction 5/5, Improved Bane of Agony 1/2, Fel Concentration 3/3, Amplify Curse 1/1, Curse of Exhaustion 1/1
  - Demonology (35): Improved Health Funnel 2/2, Demonic Embrace 5/5, Unholy Power 4/5, Demonic Aegis 2/2, Fel Vitality 3/3, Demonic Sacrifice 1/1, Master Summoner 2/2, Fel Domination 1/1, Demonic Energies 2/2, Improved Felhunter 3/3, Soul Link 1/1, Demonic Knowledge 3/3, Master Demonologist 5/5, Demonic Pact 1/1
- **Reasoning quoted:** "Soul Link, Demonic Embrace and Master Demonologist make you hard to kill, while a Felhunter with Improved Felhunter silences healers more often through a shorter Spell Lock cooldown." "Demonic Pact lets you keep a sacrificed demon's buff even after you summon another demon... sacrifice a Felhunter for health regeneration, then bring out a Voidwalker or another Felhunter."

### 1k. Destruction, PvP, level 60, "Burst / control"
- **Source:** wowforeverbuilds.com/guide/destruction-warlock-pvp-guide, **guide claim** (fetched directly)
- **Allocation: 0/16/35**
  - Demonology (16): Improved Health Funnel 2/2, Demonic Embrace 5/5, Demonic Aegis 2/2, Fel Vitality 3/3, Improved Sayaad 1/3, Master Summoner 2/2, Fel Domination 1/1
  - Destruction (35): Aftermath 5/5, Molten Skin 5/5, Bane 5/5, Ruin 5/5, Shadowburn 1/1, Intensity 3/3, Shadow and Flame 5/5, Conflagrate 1/1, Pyroclasm 2/2, Bane of Havoc 1/1, Agonizing Flames 1/3, Incinerate 1/1
- **Reasoning quoted:** "Destruction in PvP is the burst warlock. Conflagrate, Shadowburn and Ruin crits kill quickly, and the WoW Forever tree adds real defense." Molten Skin: "10% less damage taken from everything." Aftermath: makes "Conflagrate daze the target" after Immolate. Pyroclasm: "Soul Fire, Rain of Fire and Hellfire [get] a chance to stun for 6 sec."

### 1l. Affliction 44/5/2, endgame build cited via mobalytics.gg search summary
- **Source:** mobalytics.gg/wow-forever/classes/affliction-warlock-guide, **guide claim, low-confidence** (site 403'd; from WebSearch synthesis only, not directly verified)
- **Allocation:** "Affliction 44, Demonology 5, Destruction 2." Key talents cited: Wrack, Siphon Life, Curse of Exhaustion, Amplify Curse, Malevolence 5/5, Malediction 5/5.
- **Rotation cited:** Summon Imp → Curse of Shadow + Bane of Agony → prioritize Nightfall procs → Corruption + Siphon Life → Life Tap on the move → Amplify Curse as needed.
- Note: this total build (44/5/2 = 51 pts, the full level-60 pool) differs materially from wowforeverbuilds.com's 40/11/0 raid build (1f above) for the same spec, a genuine cross-site disagreement on the "best" endgame Affliction spread, not just a rounding difference.

### 1m. Level 20 leveling build via mobalytics/icy-veins search summary
- **Source:** search-summary attributed to mobalytics.gg, **guide claim, low-confidence** (403'd, unverified directly)
- **Cited allocation:** "5 points into Improved Corruption, then 3 points into Improved Drains and 2 points into Suppression. Get 3/3 Fel Concentration and 2 points into Malediction, put 2 points into Nightfall and then finish Malediction with 3 more points, and finally grab Siphon Life at level 30." This is a leveling *sequence* past 20 rather than a fixed 20-point build, and doesn't cleanly reconcile with either wowforeverbuilds' beta-20 build (1a) or icy-veins' cited build (1n), treat as directional, not exact.

### 1n. Icy-Veins level-20-equivalent build via search summary
- **Source:** icy-veins.com/wow-forever/affliction-warlock-ranged-dps-pve-guide, **guide claim, low-confidence** (403'd, unverified directly)
- **Cited allocation: 11/0/0**, Improved Corruption 5/5, Improved Life Tap 2/2, Suppression 3/5, Soul Harvesting 1/2.
- **Reasoning cited:** Improved Corruption "makes Corruption instant and increases its damage by 10%"; Improved Life Tap "help[s] you gain more Mana whenever you Life Tap"; Suppression improves hit 1%/point and cuts threat 4%/point.
- Note: this again does not match wowforeverbuilds' beta-20 build (1a: 5/2/3/1 across Imp. Corruption/Soul Harvesting/Malediction/Pandemic) or the barrens.chat 4/1/1 Suppression/Soul Harvesting/Life Tap split (1a contradicting variant). Three different sites give three different 11-point "best beta build" spreads, flagged as unresolved community disagreement, not a copy error on my part.

### 1o. Foreverwisp.com, 31/20/0 Affliction/Demonology hybrid leveling proposal
- **Source:** foreverwisp.com/guides/wow-forever-warlock-leveling-talents, **guide claim** (fetched directly)
- **Allocation: Affliction 31 / Demonology 20 / Destruction 0**, explicitly labeled a "proposal," not a tested build.
- **Quoted:** "This Affliction-first proposal is for solo questing with a summoned demon and a drain-oriented rhythm." "The intended advantage is a repeatable resource cycle across several pulls; that remains a hypothesis until tested." "Demonology requires an explicit pet plan. Know which demon is present, what job it performs and what happens when it is lost."
- Notable for explicitly flagging itself as untested theorycraft rather than a played/verified build, the only source in this survey that does so.

### 1p. Level-60 raid builds with DPS figures, expcarry.com
- **Source:** expcarry.com/wow-forever-warlock-guide, **guide claim citing sim-style numbers, source of the underlying number not stated on page** (fetched directly)
- Destruction 13/11/27, "current public DPS ~627," editorial tier A. Key mechanics: Bane of Havoc cleave, Shadow and Flame synergy, Incinerate filler w/ Immolate.
- Demonology 5/31/15, "~625 DPS," editorial tier B ("watch candidate"). Quoted: "Largest disagreement with our tier list. Demonology is a clear spec to watch for an upgrade."
- Affliction 36/0/15, "~559 DPS," editorial tier A. Quoted: "Lower public single-target sim, but values sustained pressure, solo strength and encounters rewarding DoTs differently."
- Also gives a separate leveling-track summary at levels 20/30 with its own point spreads (11pt Affliction beta-20 table, 30pt Affliction/Fel Concentration/Malevolence/Siphon Life table), see full data pulled in-session; broadly consistent with 1a/1b above but with Fel Concentration and Malevolence substituted at 23-29 instead of wowforeverbuilds' choices.
- Note: none of expcarry's three level-60 talent totals (13+11+27=51, 5+31+15=51, 36+0+15=51) match the wowforeverbuilds.com raid builds (1f/1g/1h) point-for-point, despite both being "the level 60 raid build" for the same spec. Another cross-site disagreement.

---

## 2. Interactions and combos discussed

- **DoTs can now crit, and Pandemic doubles that crit bonus.** Universally repeated across wowforeverbuilds, expcarry, and the mmoexp article, described as the single biggest Affliction change vs Classic. wowforeverbuilds guide claim: Pandemic "doubles the crit bonus of Corruption, Bane of Agony, Bane of Doom, the drains, Siphon Life and Drain Hope."
- **Nightfall proc mechanics**, guide claim (search-summary, wowforevertalents.com-style source): triggers off Corruption, Drain Soul, Drain Life, **and** Wrack (Wrack is new vs Classic, where only Corruption/Drain Life proc it). Rank 1 = 2% chance, Rank 2 = 4% chance, grants Shadow Trance (next Shadow Bolt cast time -100%, i.e. instant).
- **Demonic Sacrifice + Demonic Pact stacking**, guide claim, wowforeverbuilds.com demonology PvE guide (1g), directly fetched: sacrificing Imp for +15% Shadow damage no longer cancels when a different demon (e.g. Succubus) is subsequently summoned, letting a player run "Demonic Sacrifice, Master Demonologist, Soul Link and Demonic Knowledge" concurrently. The same guide flags this as still needing beta verification for pet-death/dismiss edge cases.
- **Soul Link**, guide claim: redirects 30% of damage taken to the pet, +3% damage to both warlock and pet. Cited as core to both the demonology PvP build (1j) and as a possible cross-spec "SL/SL" (Soul Link + Siphon Life) PvP hybrid per one mobalytics-sourced search summary (low confidence, unverified directly).
- **Drain Hope**, guide claim: 6-sec channel that raises the warlock's other Shadow DoTs on the same target by 10% while channeling; described as the Affliction tree capstone synergy with Malediction/Pandemic.
- **Improved Drains tripling below 60% target health on Drain Soul**, guide claim, wowforeverbuilds affliction PvE guide, directly fetched.
- **Curses and Banes occupying separate debuff slots**, guide claim, repeated in multiple wowforeverbuilds pages: "Bane of Agony for damage plus the raid Curse the leader assigns now occupy separate debuff slots, unlike Classic," and in PvP "Curse of Exhaustion and Bane of Agony can sit on the same target."
- **Shadow and Flame (Conflagrate/Shadowburn cross-buff)**, guide claim: max-rank Conflagrate no longer consumes Immolate, grants +10% Shadow damage for 100 sec; Shadowburn grants +10% Fire damage for 100 sec and (per icy-veins search summary) auto-refunds its Soul Shard at max rank, "essentially free."
- **Destructive Reach vs old Grim Reach, Fear range regression.** **Player report**, us.forums.blizzard.com thread "Warlock Fear range reduced from 24 to 20 yards (Likely oversight)," poster "Niks": Grim Reach used to extend Fear from 20→24 yards; Destructive Reach (its replacement) only affects damaging spells, so Fear's range regressed to base 20 yards. Niks proposes Destructive Reach apply to offensive spells generally, not just damaging ones. No developer or community reply was visible in the fetched content, status unresolved as of this survey.
- **Destructive Reach range description**, guide claim (wowhead spell page/search summary): "increases the range of your damaging spells by 20%... no Forever talent extends Drain Life's range", i.e. Drain Life stays short-range even under this talent, which is itself noted as a gap.
- **Haste does not affect DoTs or channeled spells**, **player report / dev-confirmed design note**, us.forums.blizzard.com "Bugs Surrounding Warlock" thread (compiled by poster "Chadams"): "Haste does not currently seem to affect channeled or DoT spells." Reply from "Plaguesqt": developers confirmed this is intentional, not a bug. Poster "Poptart" questioned the design choice in the same thread. This is a significant theorycraft implication (haste devalued for Affliction relative to a haste-scales-DoTs model).
- **Eureka! (Gnome racial) whole-character buff interacting with DoT snapshotting removal**, **player report**, same "Bugs Surrounding Warlock" thread, Chadams: the 10% damage racial applies to the character rather than a specific spell, so it "will increase the damage of all...DoTs for the length of the buff." Reply from "ZAU": likely intended, "a byproduct of the removal of snapshotting," and the buff's short duration makes it insignificant anyway. **Changed by the 1 Oct 2026 beta notes:** Eureka! no longer benefits periodic effects at all; channeled spells still count.
- **Demonic Energies mana funneling to pet**, guide claim, demonology voidwalker leveling guide (1c): "Demonic Energies heals the Voidwalker as you fight and gives it your Life Tap mana," framed as core to the drain-tank/pet-tank sustain loop.
- **Life Tap now scales with Spirit**, repeated across foreverwisp.com and forum bug reports as a headline mechanical change vs Classic (where it didn't scale with a stat this way); see Bugs section for the tooltip-vs-actual-ratio dispute.
- **"Support caster" framing for Affliction at low level**, **player report**, us.forums.blizzard.com thread by poster "Sakurarosa": argues Affliction's 20–25% raw damage-meter share at level 20 undersells its value because "dps meter isnt tracking all the support your giving." Reply from "Æonic": counters that they've topped meters in dungeons already, "though acknowledges it's early beta."

---

## 3. Beta performance reports

- **Leveling speed:** **guide claim**, search-summary sourced to wowforever.games/misti.services-style tier content: "Warlock is one of the top classes [for leveling speed], with Mage and Hunter being slightly faster." Also cited: Warlock (with Frost Mage and Warrior) can clear a dungeon room in "30 seconds" via AoE pulls in places like the Stockade or Hall of Thanes.
- **Spec ranking disagreement, level 60 DPS:**
  - expcarry.com (guide claim, numbers unattributed to a named sim): Destruction ~627 DPS (A-tier), Demonology ~625 DPS (B-tier, called a "clear spec to watch for an upgrade" because its sim result is judged stronger than its editorial tier), Affliction ~559 DPS (A-tier despite lower parse, credited for "sustained pressure, solo strength").
  - Other search-summarized tier lists (mmoexp.com, skycoach.gg, overgear.com, **guide claim, not independently fetched**) are inconsistent with each other: one calls Affliction "current S-Tier," another calls Demonology "an S-Tier contender," a third frames Affliction and Destruction as "A-tier editorial" with Demonology "B editorially despite a much stronger current sim result" (this last statement echoes expcarry's framing almost exactly, suggesting shared/derivative sourcing across sites rather than independent confirmation).
  - **Consensus direction, despite the numeric disagreement:** Affliction is repeatedly called the safest/most reliable leveling and solo spec; Destruction is repeatedly called the strongest raw level-60 DPS/cleave signal; Demonology is repeatedly flagged as the spec people think is *underrated relative to its sim/parse results*, especially for PvP survivability (Soul Link/Felhunter) and for the Demonic Sacrifice+Pact stacking trick.
- **Forum sentiment split on leveling feel (1–20):**
  - **Player report**, us.forums.blizzard.com "Warlock feels SO bad" thread, OP "TrueGamer": "Dots do so little damage you can auto attack with wands for virtually the same damage," complains a DoT rotation takes ~30 sec to match one melee rotation, criticizes the Soul Shard system's lack of QoL.
    - Reply "Metaspark": OP is only level 20; "Affliction seems to have a lot of its damage talents backloaded."
    - Reply "Scorched": "the game is not, and has never been, balanced for low level play. you're level 20 tops at this point."
    - Reply "Dixa": "warlock leveling was always slow and boring at these levels," improves later.
    - Reply "DeuceBane": expects Warlock to perform well at endgame raid support ("locks will be standing around summoning for tips", a joking reference to warlocks being asked to summon raid members).
  - **Player report**, us.forums.blizzard.com "Warlock 1-20 Feedback" thread, OP "lightningpaw": levels 1–5 fine; 6–10 "painful" (mana inefficiency, wand-dependent); 11–20 improved once Voidwalker is out, though threat management stayed hard. Quoted: "having to sink 5 talent points off the rip into instant Corruption feels bad." Also flags being funneled into Tailoring/Enchanting for wand crafting, and that caster spell-power nerfs make casters "significantly harder than melee classes" at this stage. Reports latency and minimap texture bugs, not warlock-specific.
    - Reply "Theryl": skipped instant Corruption, used the base 1.2-sec cast instead, says threat resolved itself once drains came online.
    - Reply "Krissey": ignored instant Corruption entirely, prioritized hit chance and pet-damage talents.
    - Reply "Miskatonic81": champions Affliction w/ instant Corruption as essential, "2 dots and a wand was enough to pull threat but I'm used to it", reports minimal downtime through 20.
  - **Player report**, eu.forums.blizzard.com "Hunter feels like Forever, Warlock feels like Vanilla" thread, OP "anakin": argues Hunter got a real redesign while Warlock's new identity (interesting talents) arrives too late in leveling; wants talents to change abilities qualitatively, not just add numbers.
    - Reply "Argonil": disagrees re: Corruption example, notes the relevant talent "already makes Corruption instant"; separately worried Wrack (the Affliction capstone) resembles a disliked mechanic from a prior expansion.
    - Reply "Svenn": dismisses as a beta-cap artifact, bigger changes are gated behind levels not yet reachable.
    - Reply "Aphne": agrees, but says it's true of all casters at low level, not Warlock-specific.
- **General note repeated by several forum posters:** because the beta cap is 20 (rising to ~30), nobody has actually played a "finished" talent tree yet, several of the level-60 "raid build" guides (1f–1k) are therefore necessarily theorycrafted from datamined talent tooltips rather than played and verified, even though they're written with played-guide confidence. Treat 1f–1k's rotation claims as unverified-in-practice.

---

## 4. Bugs

All from us.forums.blizzard.com thread "Bugs Surrounding Warlock (compiled from personal and community experience)," posted by "Chadams," described as "compiled from personal and community experience" incl. the Classic Warlock Discord, **player report**, fetched directly:

1. **Life Tap tooltip mismatch.** Tooltip states life cost is half of mana returned (e.g. "53 life for 106 mana"), scaling with Spirit; Chadams reports actual in-game behavior is a 1:1 life:mana ratio. Reply "Panzer" disputes this specific characterization: "Life tap is not 1:1, it is considerably more health lost than mana gained", i.e. the two posters disagree on what the *actual* (not tooltip) ratio is. Separately, the official Sept-24 beta dev notes (fetched directly from us.forums.blizzard.com) confirm a fix: "Tooltip of Life Tap has been updated to correctly display the amount of Life converted, and only states that it scales with Spirit", so the tooltip text itself was patched, though whether the underlying ratio dispute was also resolved is not stated.
2. **Soul Shard: flight-path free shard.** Pet despawns when boarding a flight path, its "shard refund" fires, then the pet respawns on landing, net a free extra shard, per Chadams. Reply "ZAU": "Not a bug."
3. **Soul Shard: Ritual of Summoning doesn't consume a shard.** Chadams: "Ritual of Summoning does not currently consume a soul shard when cast." Reply "Plaguesqt": "Definitely a bug" (confirmed by another player, not a developer).
4. **Soul Shard: Drain Soul grants a shard even if channel is cancelled before the target dies**, and "you can even cast other spells during this time" per Chadams. Reply "Plaguesqt" suggests this may be a leftover Season-of-Discovery passive; reply "ZAU" says "Not a bug," pointing out the tooltip already states it's a per-tick chance, not an on-kill guarantee. **Fixed in the 1 Oct 2026 beta build, for the casting part:** Drain Soul is now interrupted if the Warlock begins casting another spell. The notes say nothing about the shard part.
5. **"Demon Charge" spell leak.** Chadams: "A few warlocks have reported seeing the SoD Metamorphosis spell 'Demon Charge' in their spellbook", an apparent leftover/unintended spell-book entry from Season of Discovery. No replies recorded in the fetched excerpt.
6. **Destructive Reach / DoT range inconsistency.** Chadams notes community cites this as a bug (curse-spell range vs DoT-spell range don't match) but personally assesses it "seems to be working as intended", i.e. the compiler explicitly flags this one as probably not a real bug.
7. **Haste not affecting DoTs/channels**, see Interactions section above; confirmed by a reply as an intentional design choice, not a bug, though disputed as a *design* on its merits by poster "Poptart."
8. **Eureka! (Gnome racial) applying to the whole character rather than one spell**, see Interactions section; reply from "ZAU" calls this likely intended, a byproduct of removing damage snapshotting. **Changed by the 1 Oct 2026 beta notes:** Eureka! no longer benefits periodic effects at all; channeled spells still count.
9. **Fear range regression (24→20 yards) from Destructive Reach replacing Grim Reach**, separate thread, "Warlock Fear range reduced from 24 to 20 yards (Likely oversight)," poster "Niks", see Interactions section. Status: reported, unresolved as of the fetched content (no dev/community reply visible).
10. **Voidwalker Sacrifice scaling fix**, per the official Sept-24 dev notes (fetched directly): "Voidwalker Sacrifice now correctly scales with 10% of the Warlock's spell healing", implies it was previously scaling incorrectly; framed by Blizzard as a fix, not flagged by players as an open bug.

---

## 5. Sim tools

- **github.com/ElliotWood/Forever**, **data/sim tool**, README fetched directly. Description: "World of Warcraft Forever simulations," a fork of the wowsims/classic project, aiming to "provide a framework that makes it easy to build a DPS sim for any class/spec, with a polished UI and accurate results." Search-summary (not independently verified against a specific PR diff) states the Warlock port uses the Forever talent trees (17/19/16-point tree caps) and implements Incinerate, Drain Hope, Bane of Havoc, Decimation, Demonic Pact, Shadow and Flame, Malediction, and Pandemic, with spell values (damage range, coefficients, DoT ticks, cast time, cost, cooldown) "from the Forever beta client." Notably, per one search result, talent tooltip data for the project was originally extracted from "the BlizzCon 2026 day 1 stream using a vision model to read each frame" before the beta client was available, i.e. the sim predates actual beta-client access for part of its data. Direct README fetch found no warlock-specific performance conclusions in the accessible text (repo shows only 2 stars / 7 forks, low community uptake so far).
- **wowforeversim.com/sim/warlock**, **data/sim tool**, live simulator UI built on the ElliotWood/Forever engine per search results. Direct fetch of the page returned only the page title with no numeric output or methodology text accessible to the fetch, could not verify its conclusions independently.
- **github.com/laurencestokes/foreversim**, "WoW Forever Sims," found via search, not independently fetched/read.
- **github.com/nikftw/Forever**, a fork of ElliotWood/Forever described as adding "locked guild racials and tools/rank_races for forever-race-rankings," found via search, not independently fetched/read.
- No spreadsheet-based (Google Sheets/Excel) community theorycraft tool for Warlock specifically was found in this search pass; all located tooling is sim-engine based (wowsims-lineage).

---

## 6. Sources (URLs)

**wowforeverbuilds.com** (fetched directly unless noted):
- https://wowforeverbuilds.com/guide/beta-20-affliction-warlock-leveling
- https://wowforeverbuilds.com/guide/affliction-drain-tank-warlock-leveling
- https://wowforeverbuilds.com/classes/warlock
- https://wowforeverbuilds.com/guides/warlock
- https://wowforeverbuilds.com/guides/warlock/affliction
- https://wowforeverbuilds.com/guide/affliction-warlock-pve-guide
- https://wowforeverbuilds.com/guide/demonology-warlock-pve-guide
- https://wowforeverbuilds.com/guide/destruction-warlock-pve-guide
- https://wowforeverbuilds.com/guide/affliction-warlock-pvp-guide
- https://wowforeverbuilds.com/guide/demonology-warlock-pvp-guide
- https://wowforeverbuilds.com/guide/destruction-warlock-pvp-guide
- https://wowforeverbuilds.com/guide/demonology-voidwalker-warlock-leveling
- https://wowforeverbuilds.com/guide/destruction-shadow-bolt-warlock-leveling
- https://wowforeverbuilds.com/guide/shadow-cleave-affliction-warlock-dungeon-leveling
- (linked but not fetched this pass: /guide/shadow-cleave-demonology-warlock-dungeon-leveling, /guide/hybrid-cleave-destruction-warlock-dungeon-leveling, /guide/hunter-warlock-pet-duo-demonology-warlock-group-leveling, /guide/warlock-shadow-priest-dot-duo-affliction-warlock-group-leveling, /leveling/warlock, /pvp/warlock, /talents/warlock)

**icy-veins.com** (all 403'd on direct fetch; via WebSearch snippets only):
- https://www.icy-veins.com/wow-forever/affliction-warlock-ranged-dps-pve-guide
- https://www.icy-veins.com/wow-forever/demonology-warlock-ranged-dps-pve-guide
- https://www.icy-veins.com/wow-forever/destruction-warlock-ranged-dps-pve-guide
- https://www.icy-veins.com/wow-forever/warlock-class-overview
- https://www.icy-veins.com/wow-forever/warlock-talent-calculator

**mobalytics.gg** (403'd on direct fetch; via WebSearch snippets only):
- https://mobalytics.gg/wow-forever/classes/affliction-warlock-guide
- https://mobalytics.gg/wow-forever/classes/demonology-warlock-guide
- https://mobalytics.gg/wow-forever/classes/destruction-warlock-guide
- https://mobalytics.gg/wow-forever/guides/warlock-class-overview

**expcarry.com** (fetched directly):
- https://expcarry.com/wow-forever-warlock-guide

**mmogah.com** (403'd on direct fetch; via WebSearch snippets only):
- https://www.mmogah.com/news/wow-forever/wow-forever-warlock-leveling-guide-best-affliction-build-talents-rotation

**ssegold.com** (not fetched directly, WebSearch snippet only):
- https://www.ssegold.com/wow-forever-warlock-leveling-guide

**mmoexp.com** (WebSearch snippet only):
- https://www.mmoexp.com/News/wow-forever-warlock-talents-affliction-looks-insane-demonology-gets-major-changes.html
- https://www.mmoexp.com/News/wow-forever-dps-tier-list-2026-best-dps-specs-for-pve-raids-leveling.html
- https://www.mmoexp.com/News/wow-forever-2026-dps-tier-list-beta-best-specs-for-raids-dungeons-leveling.html

**foreverwisp.com** (fetched directly):
- https://www.foreverwisp.com/guides/wow-forever-warlock-leveling-talents
- (search only, not fetched: https://www.foreverwisp.com/guides/wow-forever-warlock-beta-levelling-changes)

**lfcarry.com** (fetched directly):
- https://lfcarry.com/guides/wow-forever-warlock, **note:** this page's own text states "Blizzard has not published the Warlock kit yet" / "Warlock talent names" are "absent from Forever posts," which contradicts every other source in this survey (all of which cite specific talent names/points). Likely explanation: a stale or templated placeholder page that predates the BlizzCon 2026 reveal and hasn't been refreshed, rather than evidence the other sites invented content. Flagged, not resolved.

**skycoach.gg** (WebSearch snippet only, no dedicated warlock guide page found, only a class tier list page referenced it):
- https://skycoach.gg/blog/wow-forever/articles/forever-class-tier-list

**warcrafttavern.com/forever** (403'd on direct fetch; via WebSearch snippet only):
- https://www.warcrafttavern.com/forever/guides/warlock/

**Blizzard official forums** (fetched directly):
- https://us.forums.blizzard.com/en/wow/t/bugs-surrounding-warlock-compiled-from-personal-and-community-experience/2359915
- https://us.forums.blizzard.com/en/wow/t/warlock-feels-so-bad/2363196
- https://us.forums.blizzard.com/en/wow/t/warlock-devs-please-listen-spellstone/2362161
- https://us.forums.blizzard.com/en/wow/t/wow-forever-warlock-guide-all-the-changes-you-didnt-notice/2359459
- https://us.forums.blizzard.com/en/wow/t/warlock-wow-forever-support-caster-affliction/2364592
- https://us.forums.blizzard.com/en/wow/t/wow-forever-beta-development-notes-–-updated-september-24/2360696/1
- https://us.forums.blizzard.com/en/wow/t/warlock-fear-range-reduced-from-24-to-20-yards-likely-oversight/2353872
- https://us.forums.blizzard.com/en/wow/t/warlock-1-20-feedback/2362831
- https://eu.forums.blizzard.com/en/wow/t/hunter-feels-like-forever-–-warlock-feels-like-vanilla/631912
- (found, not fetched: https://us.forums.blizzard.com/en/wow/t/warlock-fear-range-reduced-from-24-to-20-yards-likely-oversight/2353921 [second/duplicate thread], https://eu.forums.blizzard.com/en/wow/t/the-world-of-warcraft-forever-beta-now-live/629287)

**Sim tools:**
- https://github.com/ElliotWood/Forever (fetched directly)
- https://wowforeversim.com/sim/warlock (fetched directly, minimal content returned)
- https://github.com/laurencestokes/foreversim (search only)
- https://github.com/nikftw/Forever (search only)

**Other sites surfaced during search but outside the requested list (used only for cross-checking, not primary citations):** wowhead.com/forever (talent calculator page), barrens.chat (forum, search snippet only), leprestore.com, classicwow.gg/forever, zockify.com/forever, wowforevertalents.com, wowforever.games, misti.services, overgear.com, conquestcapped.com, classicwowforever.com, wow.gg.

**YouTube (titles/descriptions only, not watched, per task scope):**
- "WoW Forever Beta Leveling Warlock" (channel appears to be Raxxanterax per search snippet)
- "WoW Forever Warlock: EVERYTHING You Need to Know"
- "Leveling Warlock in WoW Forever, What I've Learned So Far"
- "I Played Warlock for 12 Hours in WoW Forever BEFORE BETA"
- "I Turned my Warlock into a Literal Raid Boss in Wow Forever...."
- "WOW Forever BETA testing! We're going undead Warlock!"
- "WoW Forever NEW Beta Build - HUGE Changes"
- "The New WoW Forever Beta Build: What Actually Happened?"

**Reddit:** r/classicwow and r/wow searches for "WoW Forever" + warlock terms returned no on-topic threads through WebSearch (results were dominated by unrelated Classic/SoD/retail content), and direct reddit.com fetch is blocked for this tool. No reddit content could be verified or cited for this survey, this is a gap, not an absence-of-discussion finding.
