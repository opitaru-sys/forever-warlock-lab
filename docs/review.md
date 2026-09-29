# Adversarial review: WoW Forever Warlock theorycraft model

> This review was written by a separate Claude session, working adversarially from its own code. "The brief" means the instructions it was given. File names it cites are mapped in `history/README.md`.


Reviewer recompute: `review_check.py` (independent steady-state model, own multipliers, own mana solver, plus a discrete-event rotation sim) and `level_check.py` (per-level scan of the leveling sim with a corrected rest model and a Nightfall bound). Both files are in this folder. Baseline everywhere unless stated: SP 500, crit 10%, Life Tap 840 (x1.2 only where the build has Improved Life Tap).

Note on file state: lock_sim.py, model.py, filler.py and robust.py were edited at 23:22 during this review (more policies, Amplify Curse off, new lock_sim_nf.py). Claim 6 is reviewed against the edited versions.

## Verdicts

| # | Claim | Verdict | Key number |
|---|---|---|---|
| 1 | BoD beats BoA on fights over 60s in every spec | CONFIRMED WITH CAVEAT | Steady state: BoD ahead in all specs at SP 300-1200. Pure BoD loses on most fight lengths, and the "higher base per second" reason fails for Affliction above ~576 SP |
| 2 | Succubus sac + Incinerate beats Imp sac + Shadow Bolt by ~7% | CONFIRMED WITH CAVEAT | 7.0% as modelled. 4.1% once the SB version also casts Shadowburn. Flips to SB (-1.4%) if ISB lasts 60s |
| 3 | Affliction filler: Wrack > Shadow Bolt > Drain Life | CONFIRMED WITH CAVEAT | Wrack first in all 24 Life-Tap-limited cells. SB vs DL order not robust. Without a mana limit, SB ties or beats Wrack |
| 4 | Keep Succubus over Imp sac once Succubus >= ~15% of total | CONFIRMED WITH CAVEAT | Breakeven is 15.0% of the warlock's own damage, which is 13.0% of total. Destro's breakeven is 8.4% of total |
| 5 | Demo top if Succubus >= ~15%, else Destro (Incinerate); Affliction last | CONFIRMED WITH CAVEAT | Model's own crossover is ~8.5%, not 15%. With Demo's 5% hit gap, Demo needs ~21% and Destro-keep-Succubus holds the middle band. Affliction last is robust |
| 6 | Leveling: DoTs+wand to ~38, Drain Life from ~40, SB never | CONFIRMED WITH CAVEAT | The switch is at L34 (L31-33 at high SP), not ~38-40. SB never wins (0 of 612 scans) |

## Validation of the core algebra

The Life Tap budget in raid.py:116, `f = (1 - time_used - GCD*mana_rate/lt) / (1 + GCD*fil_mana/lt)`, is algebraically correct for "Life Tap is the only mana source". I derived it independently: time `1 = A + f + GCD*LTrate`, mana `M + f*m_f = LTrate*lt`. A discrete-event rotation sim (Destro Incinerate, BoA, 20,000s, mana starting at 0) gives **494.2 DPS vs 493.0 analytic**. The filler share differs (0.328 vs 0.275) because priority collisions delay cooldowns in the sim (Shadowburn every 18.5s instead of 15s). That is scheduling loss, not an algebra error. My independent model reproduces the author's raid2 baseline within about 1 DPS on every spec (Destro Incinerate 519.8 vs 520, Destro SB 485.6 vs 486, Demo lock-only 476.0 vs 476, Aff SB 411.9 vs 413).

Structural caveat that applies to every raid ranking: the model has no mana pool, no regen, no raid mana buffs and no potions. Destro and Demo spend about 20% of the fight Life Tapping, Affliction/Wrack about 11%. Richer mana helps Destro and Demo more than Affliction.

## Claim 1: Bane of Doom vs Bane of Agony

Arithmetic in the claim is right: 4.0/60 = 1.596/24 = 0.0667 SP per second, raw base 29.0/s vs 23.0/s, and 1 GCD per 60s vs per 24s (2.5x).

Steady-state BoD minus BoA (DPS):

| SP | Aff (Wrack) | Aff (SB) | Destro | Demo (lock) |
|---|---|---|---|---|
| 300 | +11.9 | +10.9 | +21.9 | +22.2 |
| 500 | +13.0 | +11.7 | +26.8 | +26.2 |
| 1000 | +15.9 | +13.7 | +39.0 | +36.3 |
| 1200 | +17.1 | +14.5 | +43.9 | +40.3 |

Caveats:
1. **The stated reason is wrong for Affliction.** Improved Bane of Agony (+10%) applies to BoA only. Above **~576 SP**, BoA does more damage per second than BoD in Affliction (SP 1000: 98.5/s vs 95.7/s). Affliction's BoD edge then comes only from saved GCDs and mana, about 3%.
2. **Pure BoD loses on most finite fights.** Bane damage only, Affliction multipliers, SP 500: at T=90s BoA 8,120 vs BoD 5,456; at T=150s 13,533 vs 10,912. The correct rule is "BoD while at least 60s of fight remain, then BoA for the tail". With that rule BoD-first wins at every T >= 60.
3. **The 4.0 coefficient carries the claim.** BoD and BoA tie at a coefficient of about **2.9 (Aff), 2.1 (Demo), 1.3 (Destro)**. Wowhead shows no coefficient. If the real value is closer to 2, Affliction should use BoA and Demo is a coin flip.

## Claim 2: Destruction 9/11/31, Incinerate vs Shadow Bolt

| Variant (BoD, SP500, crit 10%) | DPS | Incinerate edge |
|---|---|---|
| SB, Imp sac, ISB as coded (SB only, n = 3.6) | 485.6 | +7.0% |
| SB, ISB on all Shadow damage, n from actual SB rate | 487.4 | +6.6% |
| **SB + Shadowburn on cooldown, ISB fixed** | **499.4** | **+4.1%** |
| SB + Shadowburn, ISB lasting 60s | 527.1 | **-1.4%** |
| Incinerate, Succubus sac (as coded) | 519.8 | n/a |
| Incinerate, 5 dead ISB points moved to Aftermath 5/5 | 533.0 | +6.7% vs fair SB |

Across SP 300-1000 and crit 5-20%, the fair SB comparison gives **+2.2% to +5.3%**. The edge shrinks as crit rises, because ISB uptime rises.

Caveats:
1. **The SB version was denied Shadowburn** (raid2.py:29-31). Shadowburn out-damages SB per cast-second (about 320/s vs 279/s raw) and turns on the Fire half of Shadow and Flame for Immolate and Conflagrate. Any SB player casts it. This accounts for about 3 of the 7 points.
2. **ISB duration.** The brief says 12s. The wowforeverbuilds guide quoted in warlock-community.md:42 and :68 says 60s. At 60s duration and crit of 10% or more, SB wins unless the Incinerate build respecs its dead ISB points (then +1.1% at 10% crit, -2.0% at 20%).
3. **The Incinerate version wastes 5 points** in Improved Shadow Bolt. Aftermath 5/5 (+50% Immolate initial damage) is reachable without breaking tier gating and adds about 13 DPS.
4. Immolate coefficient ambiguity: warlock-mechanics.md:40 labels the coefficients ".2 (DoT) / .13 (initial)", the reverse of the brief. Swapping them gives +4.3% (fair comparison). It does not flip the result.

Net: Incinerate wins in most plausible scenarios. The margin is 1-7% depending on ISB duration and respec, not a firm 7%.

## Claim 3: Affliction filler

Rank per cell, BoD, filler DPS as whole-spec DPS:

- **Life Tap 840 (Life Tap-limited):** Wrack first in 12/12 cells. SB second in 10/12. **Drain Life beats SB at SP 300 with 10-20% crit.**
- **Life Tap 530:** Wrack first in 12/12. Drain Life beats SB in 4/12 (all SP 300 cells, and SP 500 at 20% crit).
- **Mana not binding:** SB ties or beats Wrack in 7/12 cells (SP 500, crit 10%: SB 476 vs Wrack 473).

Why: per second of cast time, SB (89.7 + 0.286 SP raw, x1.075 crit) out-damages Wrack (37 + 0.143 SP, x1.83 from drains, Malediction and Pandemic) even after counting Wrack's +10% DoT amplification. Wrack wins on mana: 33 mana/s vs 127 mana/s for SB.

Fixes that change magnitude, not order:
- Nightfall proc sources (raid.py:119-122): Wrack and Drain Life ticks also proc Nightfall. Correct accounting raises Wrack 425.6 to 434.2 and DL 392.1 to 402.8. SB is unchanged at 411.9.
- If Improved Drains and Soul Siphon stack additively (1.56, not 1.632): Wrack 426.8, still first.
- Affliction should also keep Immolate up (see bugs): Wrack 447.6, SB 430.6.

Verdict: Wrack first holds whenever Life Tap is the main mana source, provided Wrack really has no cooldown. "SB ahead of Drain Life" is fragile.

## Claim 4: Keep Succubus vs sacrifice Imp

Affliction breakeven Succubus DPS: 43 / 57 / 70 at SP 300 / 500 / 700. That is **15.0% of the warlock's own damage and 13.0% of total**, the same at every SP. The claim says "15% of total". The right number is 13% of total. The raid2 parameter `pet_share` is a fraction of the warlock's damage, not of total (raid.py:125). For Destruction (keep vs Succubus sac), breakeven is **8.4% of total**. The 15% figure is Affliction-specific.

Unit note for the BlizzCon figure: "Succubus 23-25% of total" corresponds to `pet_share` 0.30-0.33, not 0.25.

## Claim 5: Top raid spec

Model's own crossover (raid2 code, pet_share scanned in 0.005 steps): Demo becomes top at pet_share **0.085 at SP 500 / crit 10%** (8.9% of Demo total). It ranges from 0.065 to 0.185 across SP 300-700 and crit 5-15%. The "~15%" comes from the grid at raid2.py:56, which tests pet_share 0, 0.15, 0.25, 0.33 and nothing in between. Only the SP 300 / crit 5% corner reaches ~17%.

With the pet modelled as absolute DPS (the same Succubus in every spec) and my fixes:

| SP500 | Top spec by Succubus base DPS (P0) |
|---|---|
| Hit equal | Destro Succ-sac below P0 31 (6.9% of total), Demo above |
| **Demo 5% hit short** | Destro Succ-sac below 44; **Destro keep-Succubus from 44 to 103**; Demo only above 103 (**20.6% of Demo total**) |

Demo 0/31/20 has no Suppression. Affliction 40/11/0 and Destro 9/11/31 both have 5/5. "Hit assumed capped" gives Demo a free 5% unless gear alone reaches the 16% cap. Forever's unified hit may make that easy, but that is unverified.

Affliction last: robust. At SP 500, Affliction is 434 (448 with Immolate) vs Demo lock-only 484 and Destro 520. Affliction keeping the Succubus trails Destro keeping it by about 98 DPS at any pet value.

Verdict: the ordering is right. The threshold is wrong, about 7-9% with hit equal and about 21% with the hit gap. The middle band's top spec, Destruction keeping the Succubus, is missing from the claim.

## Claim 6: Leveling filler (current filler.py / lock_sim.py)

Winner per level, SP = 1.0 x level: wand policies L14-L32, Drain Life policies L34-L60. The first Drain Life win is **L34** at SP 0.5x and 1.0x, and **L31** at 2.0x. The switch lines up with Soul Siphon (+36%, talent points at L32-34). filler.py only samples L20/30/40/50/60, so "~38 / ~40" was never tested.

- **Shadow Bolt never wins:** 0 of 612 scans (L10-60 x 3 SP levels x 4 variants: original, split food/drink rest, Nightfall off, proper Nightfall from lock_sim_nf.py). SB trails the best policy by 5-10s per kill.
- **Margins near the switch are thin:** Drain Life beats wand by 2.9% at L34, 4.5% at L38, 10% at L40, 12-18% at L50-60.
- **If wands scale with spell power** (a Forever change the community reports; model.py:66 does not model it), wand still wins at L36 and Drain Life takes over at L40. Probe: wand DPS + 0.25 x SP.
- **Scope:** the sim has no Bane, Improved Shadow Bolt or Ruin. "SB never best" is proven only for the Affliction talent path, not for a Destruction leveling build like the community's 17/0/34.

## Bugs

| File:line | Bug | Effect | Corrected result |
|---|---|---|---|
| raid2.py:29-31 | Imp-sac SB Destro spec never casts Shadowburn, though the build has it and it out-damages SB per GCD | Inflates claim 2 | Incinerate edge 7.0% -> 4.1% |
| raid.py:61-62, raid.py:176-179, raid2.py:44-45 | ISB (+20% Shadow damage taken from you) applied only to Shadow Bolt, not Corruption, Banes or Shadowburn; uptime uses a fixed 3.6 SB per 12s, but the real rate is 2.0 (Destro) and 3.2 (Demo) | Small, and in opposite directions | Destro SB +1.8 DPS; Demo 476.0 -> 484.2 |
| raid.py:124-126 | Pet = pet_share x warlock's own total. The Succubus gets stronger in high-DPS specs (93 DPS under Affliction vs 119 under Destro at the same SP) | Makes cross-spec pet thresholds meaningless | Use absolute pet DPS; thresholds in the claim 5 section |
| raid2.py:56 | Sensitivity grid has no pet_share between 0 and 0.15 | Produces the "~15%" threshold | True crossover 0.085 at baseline |
| raid.py:118-122 | Nightfall procs counted from Corruption ticks only; Wrack and Drain Life ticks also proc. Per-proc value assumes the displaced filler is SB and ignores the SB's 380 mana | Understates Wrack and DL | Wrack +8.6, DL +10.7 DPS; order unchanged |
| raid2.py:12-13, 18-20 | Affliction and Demo never maintain Immolate. It is baseline and beats their filler per effective second | Understates both | Aff +13 to 19 DPS, Demo +15 DPS; lowers Demo's pet threshold to ~4% |
| raid2.py:18-20 | Demo 0/31/20 has no Suppression but is treated as hit-capped like the others | Favors Demo by up to 5% | Demo needs ~21% pet share with the gap |
| raid2.py:20 | Master Demonologist applied to all Succubus damage (should be Shadow/Lash of Pain only). Improved Sayaad +30% and Demonic Knowledge pet spell power omitted | Net sign unknown | Unquantified, likely small |
| raid2.py:32-34 | Incinerate build keeps 5/5 Improved Shadow Bolt, which does nothing without SB | Understates Incinerate | +13 DPS with Aftermath 5/5 |
| raid.py:89-90 | Malediction (+periodic damage) also multiplies Immolate's direct hit | Trivial | about -0.3 DPS |
| raid.py:172 / :34 | raid.py defaults Life Tap to 840 x 1.2 for every spec, including Affliction, which has no Improved Life Tap (fixed in raid2) | raid.py output only | Use raid2 |
| raid.py:95 | `dot_dps_total` computed, never used | None | Delete |
| lock_sim.py:159-160, 171-172 | Nightfall credits a free Shadow Bolt per proc (no GCD, no mana). lock_sim_nf.py fixes it, but filler.py still imports lock_sim | No winner change at any level | Verified with lock_sim_nf |
| lock_sim.py:293-294 | Rest pools food and drink into one rate. When the deficit is mostly health, true rest is health deficit / food rate | Understates wand-policy rest from L36 (e.g. L40 Corr+BoA+Wand 3.2s -> 7.4s) | Winner unchanged; switch level unchanged |
| lock_sim.py:64, :16 | Base hit 0.96 (the sourced figure is a 3% miss, so 0.97); BoA R6 is 47/tick = 564, but the sourced total is 552 | Trivial | n/a |
| filler.py:19-29 | Samples only L20/30/40/50/60 | Mislocates the switch | Switch at L34, not ~38-40 |

## Data flags (not code bugs)

- ISB duration: 12s (brief) vs 60s (wowforeverbuilds, warlock-community.md:42, :68). This flips claim 2 at crit of 10% or more. Also unknown: whether Forever ISB still uses Classic's 4 charges. Charges would cut uptime sharply under DoT ticks.
- Immolate coefficients: labels in warlock-mechanics.md:40 are the reverse of the brief.
- BoD coefficient 4.0: two datamines, no Wowhead value. Claim 1 tips over below ~2-3.
- Wrack "no cooldown": claim 3 depends on it.
- Demonic Pact edge cases (pet death, dismiss) are flagged as untested by the guide that recommends it. Claim 5's Demo result depends on Pact working as described.

# Follow-up review: solo leveling claims 7-9

Scripts: `followup_check.py` (single mob HP, as the author ran it) and `followup_avg.py` (seconds per kill averaged over mob HP x0.80 to x1.20 in 9 steps). Both use lock_sim_nf.py and compute rest two ways: "pooled" (lock_sim's single combined rate) and "split" (rest = max(health deficit / food rate, (mana deficit + k x health deficit) / (drink + k x food))).

**Why averaging matters:** kill time is quantised to DoT and drain ticks (0.5 to 1s steps). For the same two builds at L60, the DK splash advantage over Deep Affliction swings from +2.8% to +6.9% when mob HP moves by only +-10%. Single-HP margins under about 2 percentage points, or about 0.7s per kill, are noise.

## Verdicts

| # | Claim | Verdict | Key number (HP-averaged, pooled / split rest) |
|---|---|---|---|
| 7 | DK splash 28/23/0 beats Deep Aff 38/13/0 and the drain tank by 5-6% s/kill, ~7% 120s damage | CONFIRMED WITH CAVEAT | +5.4% / +5.1% vs Deep Aff, +7.0% / +6.7% vs drain tank. Survives SP 3xL and a halved pet. Only +2.4% vs an Affliction build that takes Malevolence and Unholy Power |
| 8 | Affliction-first is best or tied to 55; the DK detour pays only at 60 | CONFIRMED WITH CAVEAT | Affliction-first is ahead L36-54 by 0.2 to 1.7s per kill. The DK path is ahead from **L56** (1.0 to 1.5s), not only at 60 |
| 9 | IF sacrifices stack under Pact with a Succubus out, ~11% faster than the DK splash | CONFIRMED WITH CAVEAT (conditional) | +9.3% / +8.7% averaged. Flips to -13.2% (split rest) if Soul Link's redirected damage must be healed back. The non-speculative Pact build (Imp sac only) is -0.5% / -3.8% |

**Does the rest fix flip any of them on its own? No.** Claim 7 stays at +2.8% or more in every cell. Claim 8's crossover does not move. Claim 9 stays at +8.7%. The rest fix bites only in combination: claim 9 with the Soul Link redirect paid back goes from +0.7% (pooled) to -13.2% (split), because the Succubus builds leave the warlock with a large health deficit that food alone must refill.

## Claim 7 detail

Tier validity of the recommended swap (drop Demonic Sacrifice 1, Master Summoner 2, Fel Domination 1; add Demonic Aegis 2, Demonic Energies 2):
- Demonology rows become [10, 10, 0, 0, 3]. Rows 0-3 total 20, so Demonic Knowledge (row 4) is reachable. Row 1 is full at 10/10. `valid()` returns True, and the layout in warlock-talents.md agrees (DK in row 5 of 7, one-indexed).
- **Damage-identical:** lock_sim_nf.py and model.py never read Aegis, Energies, Sacrifice (except via `_sac`), Master Summoner or Fel Domination. The swap changes spk by exactly 0. In the real game, Demonic Energies (pet heal, Life Tap mana to pet) is an unmodelled upside for a Voidwalker tank.

HP-averaged DK splash advantage (positive = DK faster), pooled / split:

| SP, pet | vs Deep Aff 38/13/0 | vs drain tank | vs Aff 42/9/0 (Malevolence + UP) |
|---|---|---|---|
| 1xL, pet x1 | +5.4 / +5.1 | +7.0 / +6.7 | +2.4 / +2.4 |
| 1xL, pet x0.5 | +4.7 / +2.8 | +6.0 / +4.1 | +1.9 / -0.1 |
| 2xL, pet x1 | +6.2 / +6.1 | +6.9 / +6.7 | +3.9 / +3.8 |
| 2xL, pet x0.5 | +4.5 / +4.2 | +6.2 / +6.0 | +1.6 / +1.7 |
| **3xL, pet x1** | **+6.0 / +5.8** | +7.0 / +6.7 | +2.9 / +2.9 |
| **3xL, pet x0.5** | **+5.2 / +5.0** | +5.8 / +5.7 | +2.8 / +2.6 |

120s damage, DK splash vs Deep Aff: +7.3% (1xL), +6.2% (2xL), +5.3% (3xL); pet halving changes this by at most 0.3 points. Versus Aff 42/9/0: +1.7%, +0.8%, 0.0%.

Caveat: **most of the 5-6% is the comparators, not Demonic Knowledge.** Deep Aff 38/13/0 spends 16 points on talents the model gives zero damage (Fel Concentration 3, Demonic Embrace 5, Improved Voidwalker 3, Fel Vitality 3, Demonic Aegis 2) and skips Malevolence. Aff 42/9/0 (IC5, Supp5, ILT2, Mal5, ID3, IBoA2, Pand3, Malev5, NF2, SL1, SS3, SM5, Wrack1, UP5, DE4; valid, 51 points) closes all but about 2-3% of the spk gap and all but 0-2% of the sustained damage gap. The claim is right as stated about those two builds. "DK is the key talent" is only a 2-3% effect.

Other notes: DK's pet spell power is not modelled, which is conservative for DK. solo60.py:28-29 skips every L50 comparison, so its L50 headers print with no rows.

## Claim 8 detail

HP-averaged, Affliction-first minus best DK path, seconds per kill (positive = DK path faster), pooled rest; split rest agrees within 0.2s:

| SP | L36 | L40 | L44 | L46 | L48 | L52 | L54 | L56 | L58 | L60 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1xL | -0.18 | -0.72 | -0.77 | +0.05 | -1.69 | -1.24 | -1.26 | **+1.07** | +1.35 | +1.67 |
| 2xL | -0.18 | -0.74 | -0.66 | +0.25 | -1.52 | -0.67 | -1.04 | **+1.34** | +1.19 | +1.84 |
| 3xL | -0.18 | -0.44 | -0.50 | +0.32 | -1.29 | -0.39 | -0.98 | **+1.44** | +1.32 | +1.69 |

- path.py samples every 5 levels at one mob HP. A single-HP per-level scan shows spurious DK wins at L36 and L46 (0.1 to 0.7s). After averaging, L36 flips back to Affliction and L46 shrinks to +0.05 to +0.37s, which is noise.
- **The DK detour pays from about L56, not only at 60.** DK_PATH gets Demonic Knowledge at L53, and by L56 it is 1.0 to 1.4s per kill faster. The practical rule becomes: level Affliction-first, respec into the DK splash around L55-56.

## Claim 9 detail

stack.py's Pact build is tier-valid: Demonology rows [10, 5, 5, 2, 4, 4, 1] = 31, with 30 in rows 0-5 before Demonic Pact. Prerequisites hold (Soul Link needs Demonic Sacrifice; Pact needs Soul Link; Fel Domination needs Master Summoner 2). It stays valid under the talents-file layout (Decimation in row 3). It wastes about 4 points: Improved Voidwalker 2 (dead with a Succubus), Fel Domination and Decimation 1 (no model effect, no Soul Fire).

HP-averaged, % faster than the DK splash, pooled / split:

| Variant | 1xL pet x1 | 1xL pet x0.5 | 3xL pet x1 | 3xL pet x0.5 |
|---|---|---|---|---|
| Pact, Imp sac only + Succubus | -0.5 / -3.8 | -4.3 / -4.4 | +0.9 / -1.7 | -3.6 / -3.1 |
| **Stack + Succubus (as coded)** | **+9.3 / +8.7** | +7.0 / +7.3 | +9.1 / +7.0 | +5.7 / +6.0 |
| Stack + sacrifice regen out of combat | +14.8 / +14.9 | +12.1 / +12.4 | +14.8 / +14.4 | +10.6 / +10.9 |
| Stack, Soul Link redirect paid back 1:1 | +0.7 / **-13.2** | -3.0 / -13.9 | +2.9 / -7.2 | -1.9 / -7.3 |
| Stack, redirect paid + out-of-combat regen | +6.4 / -3.7 | +2.4 / -5.2 | +9.2 / +3.1 | +4.1 / +1.8 |

Modelling issues, in order of weight:
1. **Soul Link's 30% redirect is free mitigation.** model.py:62-64 sets the warlock's damage taken to 1.0 x 0.7 with a Succubus out, and no pet health pool exists. At L60 that is about 38 DPS (0.3 x 126) into a Succubus with no self-heal, about 600 HP per kill, more than out-of-combat pet regen covers in 10s. Paying it back 1:1 (Health Funnel or rest) is the pessimistic bound; free is the optimistic one. The build lacks Demonic Energies 2/2 (pet healed for 15% of your spell damage), which would cover roughly half of it. Swapping in the 2 dead Improved Voidwalker points (same row) is a strict improvement.
2. **Sacrifice regen is counted only in combat.** lock_sim_nf.py:184-187 applies Felhunter 3% HP/4s and Voidwalker 2% mana/4s inside the fight loop only. These are 2-hour buffs, so they also run during travel and rest. Crediting them during travel alone raises the stack gain to about 15%. This bias is against the claim.
3. **No spell pushback is modelled.** The Succubus builds have the warlock tanking 70% of melee while channelling Drain Life, and the Pact build has no Fel Concentration. Real pushback would cost these variants channel ticks. The model cannot show it.
4. **The premise is unverified.** Pact's tooltip only says the buff is not cancelled by summoning a different demon. Whether a second sacrifice adds a second buff rather than replacing the first is untested, and the Pact guide itself flags pet edge cases as needing beta testing.

Net: the ~11% (about 9% averaged) holds only if stacking works AND the redirected damage is effectively free. With a pessimistic pet-healing assumption and split rest, the stacked build is 7-14% slower than the DK splash. The non-speculative Pact build (Imp sac only) does not beat the DK splash in 7 of 8 cells.
