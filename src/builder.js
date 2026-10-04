  // ================================================================ talent builder
  // Positions, ranks and prerequisites from the Wowhead Forever calculator. Per-rank values from its rank tooltips.
  // scored: 'yes' counts in the leveling score, 'utility' is real but outside the damage and time math.
  const TREES = ['Affliction', 'Demonology', 'Destruction'];
  const TALENTS = [
    // Affliction
    { k: 'ImprovedLifeTap', n: 'Improved Life Tap', t: 0, r: 0, c: 0, m: 2, s: 'yes', d: 'Life Tap gives {a} more mana.', a: ['10%', '20%'] },
    { k: 'Suppression', n: 'Suppression', t: 0, r: 0, c: 1, m: 5, s: 'yes', d: '+{a} hit and {b} less threat.', a: ['1%', '2%', '3%', '4%', '5%'], b: ['4%', '8%', '12%', '16%', '20%'] },
    { k: 'ImprovedCorruption', n: 'Improved Corruption', t: 0, r: 0, c: 2, m: 5, s: 'yes', d: 'Corruption casts {a} sec faster and deals {b} more. Instant at 5/5.', a: ['0.4', '0.8', '1.2', '1.6', '2.0'], b: ['2%', '4%', '6%', '8%', '10%'] },
    { k: 'Malediction', n: 'Malediction', t: 0, r: 1, c: 0, m: 5, s: 'yes', d: '+{a} damage from all your periodic spells.', a: ['1%', '2%', '3%', '4%', '5%'] },
    { k: 'SoulHarvesting', n: 'Soul Harvest', t: 0, r: 1, c: 1, m: 2, s: 'yes', d: 'After a Drain Soul kill, +{a} mana regen for 10 sec. Scored when the best rotation finishes with Drain Soul.', a: ['50%', '100%'] },
    { k: 'ImprovedDrains', n: 'Improved Drains', t: 0, r: 1, c: 2, m: 3, s: 'yes', d: 'Drain Life, Drain Soul and Wrack deal {a} more.', a: ['7%', '14%', '20%'] },
    { k: 'ImprovedBoA', n: 'Improved Bane of Agony', t: 0, r: 2, c: 0, m: 2, s: 'yes', d: 'Bane of Agony deals {a} more.', a: ['5%', '10%'] },
    { k: 'FelConcentration', n: 'Fel Concentration', t: 0, r: 2, c: 1, m: 3, s: 'utility', d: '{a} chance to avoid pushback while draining.', a: ['23%', '47%', '70%'] },
    { k: 'AmplifyCurse', n: 'Amplify Curse', t: 0, r: 2, c: 2, m: 1, s: 'yes', d: 'Your next Bane of Agony or Curse of Weakness is 50% stronger. 3 min cooldown.' },
    { k: 'Pandemic', n: 'Pandemic', t: 0, r: 2, c: 3, m: 3, s: 'yes', d: 'Crits from DoTs and drains deal {a} more bonus damage.', a: ['33%', '67%', '100%'] },
    { k: 'Malevolence', n: 'Malevolence', t: 0, r: 3, c: 0, m: 5, s: 'yes', d: '+{a} crit on Shadow spells.', a: ['1%', '2%', '3%', '4%', '5%'] },
    { k: 'Nightfall', n: 'Nightfall', t: 0, r: 3, c: 1, m: 2, s: 'yes', d: 'Corruption and drain ticks have a {a} chance to make your next Shadow Bolt instant.', a: ['2%', '4%'] },
    { k: 'CurseOfExhaustion', n: 'Curse of Exhaustion', t: 0, r: 3, c: 2, m: 1, s: 'utility', d: 'Curse: slows the target by 30% for 12 sec.' },
    { k: 'SiphonLife', n: 'Siphon Life', t: 0, r: 4, c: 1, m: 1, s: 'yes', d: 'A DoT that heals you for the damage it deals.' },
    { k: 'SoulSiphon', n: 'Soul Siphon', t: 0, r: 4, c: 2, m: 3, s: 'yes', d: 'Drains deal {a} more per other Affliction effect on the target, up to 3.', a: ['4%', '8%', '12%'] },
    { k: 'ShadowMastery', n: 'Shadow Mastery', t: 0, r: 5, c: 2, m: 5, s: 'yes', d: '+{a} Shadow damage.', a: ['1%', '2%', '3%', '4%', '5%'] },
    { k: 'Wrack', n: 'Wrack', t: 0, r: 6, c: 1, m: 1, s: 'yes', req: ['SiphonLife', 1], d: 'A 6-sec channel. Your other Shadow DoTs deal 10% more while it runs. Usable from level 40.' },
    // Demonology
    { k: 'ImprovedHealthFunnel', n: 'Improved Health Funnel', t: 1, r: 0, c: 0, m: 2, s: 'utility', d: 'Health Funnel heals your demon {a} more and costs less.', a: ['20%', '40%'] },
    { k: 'ImprovedImp', n: 'Improved Imp', t: 1, r: 0, c: 1, m: 3, s: 'yes', d: "The Imp's Firebolt and Fire Shield are {a} stronger.", a: ['10%', '20%', '30%'] },
    { k: 'DemonicEmbrace', n: 'Demonic Embrace', t: 1, r: 0, c: 2, m: 5, s: 'yes', d: '+{a} Stamina.', a: ['3%', '6%', '9%', '12%', '15%'] },
    { k: 'UnholyPower', n: 'Unholy Power', t: 1, r: 0, c: 3, m: 5, s: 'yes', d: 'Your demon deals {a} more damage.', a: ['2%', '4%', '6%', '8%', '10%'] },
    { k: 'DemonicAegis', n: 'Demonic Aegis', t: 1, r: 1, c: 0, m: 2, s: 'utility', d: 'Demon Skin and Demon Armor are {a} stronger.', a: ['15%', '30%'] },
    { k: 'ImprovedVoidwalker', n: 'Improved Voidwalker', t: 1, r: 1, c: 1, m: 3, s: 'utility', d: "The Voidwalker's abilities are {a} stronger.", a: ['10%', '20%', '30%'] },
    { k: 'FelVitality', n: 'Fel Vitality', t: 1, r: 1, c: 2, m: 3, s: 'yes', d: 'Your demon gets {a} more health and mana, and you get {a} more mana.', a: ['5%', '10%', '15%'] },
    { k: 'DemonicEnergies', n: 'Demonic Energies', t: 1, r: 1, c: 3, m: 2, s: 'utility', d: 'Your spells heal your demon for {a} of their damage, and it gets {b} of your Life Tap mana.', a: ['8%', '15%'], b: ['50%', '100%'] },
    { k: 'ImprovedSayaad', n: 'Improved Sayaad', t: 1, r: 2, c: 0, m: 3, s: 'yes', d: "The Succubus's Lash of Pain is {a} stronger and Seduction lasts longer. Scored assuming Lash of Pain is 40% of her damage.", a: ['10%', '20%', '30%'] },
    { k: 'DemonicSacrifice', n: 'Demonic Sacrifice', t: 1, r: 2, c: 1, m: 1, s: 'yes', d: 'Sacrifice your demon for a 2-hour buff: Imp +15% Shadow, Voidwalker 2% mana every 4 sec, Succubus +15% Fire, Felhunter 3% health every 4 sec. Pick it in the Sacrifice menu.' },
    { k: 'MasterSummoner', n: 'Master Summoner', t: 1, r: 2, c: 2, m: 2, s: 'utility', d: 'Summons cast {a} sec faster and cost {b} less.', a: ['2', '4'], b: ['20%', '40%'] },
    { k: 'Decimation', n: 'Decimation', t: 1, r: 3, c: 0, m: 2, s: 'yes', d: 'Soul Fire cooldown {a} shorter, and a fast free Soul Fire on targets under 35%. Scored as a free Soul Fire finisher.', a: ['45%', '90%'] },
    { k: 'FelDomination', n: 'Fel Domination', t: 1, r: 3, c: 2, m: 1, s: 'utility', req: ['MasterSummoner', 2], d: 'Your next summon is 5.5 sec faster and half price. 5 min cooldown.' },
    { k: 'DemonicBrand', n: 'Demonic Brand', t: 1, r: 3, c: 3, m: 3, s: 'utility', d: "Searing Pain makes {a} less threat and brands the target. Your pet's next 3 attacks on it generate high threat. Try the 'pet holds aggro' box.", a: ['17%', '33%', '50%'] },
    { k: 'ImprovedFelhunter', n: 'Improved Felhunter', t: 1, r: 4, c: 0, m: 3, s: 'utility', d: "The Felhunter's abilities are {a} stronger and Spell Lock comes back {b} sec sooner.", a: ['10%', '20%', '30%'], b: ['2', '4', '6'] },
    { k: 'SoulLink', n: 'Soul Link', t: 1, r: 4, c: 1, m: 1, s: 'yes', req: ['DemonicSacrifice', 1], d: '30% of the damage you take goes to your demon, and you both deal 3% more.' },
    { k: 'DemonicKnowledge', n: 'Demonic Knowledge', t: 1, r: 4, c: 2, m: 3, s: 'yes', d: 'Spell damage equal to {a} of your level, for you and your demon, while a demon is out.', a: ['33%', '67%', '100%'] },
    { k: 'MasterDemonologist', n: 'Master Demonologist', t: 1, r: 5, c: 2, m: 5, s: 'yes', d: 'A buff by demon: Imp +{a} Fire, Voidwalker less Physical taken, Succubus +{a} Shadow for you both, Felhunter less Magic taken. Scored for the Imp and the Succubus.', a: ['2%', '4%', '6%', '8%', '10%'] },
    { k: 'DemonicPact', n: 'Demonic Pact', t: 1, r: 6, c: 1, m: 1, s: 'yes', req: ['SoulLink', 1], d: 'Your sacrifice buff survives summoning a different demon.' },
    // Destruction
    { k: 'DestructiveReach', n: 'Destructive Reach', t: 2, r: 0, c: 0, m: 2, s: 'utility', d: 'Damaging spells reach {a} farther.', a: ['10%', '20%'] },
    { k: 'ImprovedShadowBolt', n: 'Improved Shadow Bolt', t: 2, r: 0, c: 1, m: 5, s: 'yes', d: 'Shadow Bolt crits make the target take {a} more Shadow damage from you for 12 sec.', a: ['4%', '8%', '12%', '16%', '20%'] },
    { k: 'Bane', n: 'Bane', t: 2, r: 0, c: 2, m: 5, s: 'yes', d: 'Shadow Bolt, Immolate and Incinerate cast {a} sec faster, Soul Fire {b} sec.', a: ['0.1', '0.2', '0.3', '0.4', '0.5'], b: ['0.4', '0.8', '1.2', '1.6', '2.0'] },
    { k: 'MoltenSkin', n: 'Molten Skin', t: 2, r: 1, c: 0, m: 5, s: 'yes', d: 'You take {a} less damage.', a: ['2%', '4%', '6%', '8%', '10%'] },
    { k: 'Cataclysm', n: 'Cataclysm', t: 2, r: 1, c: 1, m: 3, s: 'yes', d: 'Destruction spells cost {a} less mana.', a: ['3%', '7%', '10%'] },
    { k: 'Aftermath', n: 'Aftermath', t: 2, r: 1, c: 2, m: 5, s: 'yes', d: "Immolate's first hit deals {a} more, and Conflagrate can daze.", a: ['10%', '20%', '30%', '40%', '50%'] },
    { k: 'Ruin', n: 'Ruin', t: 2, r: 2, c: 1, m: 5, s: 'yes', d: 'Destruction crits deal {a} more bonus damage.', a: ['20%', '40%', '60%', '80%', '100%'] },
    { k: 'Shadowburn', n: 'Shadowburn', t: 2, r: 2, c: 2, m: 1, s: 'yes', d: 'An instant Shadow hit on a 15-sec cooldown that refunds a Soul Shard on a kill.' },
    { k: 'Intensity', n: 'Intensity', t: 2, r: 3, c: 0, m: 3, s: 'utility', d: '{a} chance to avoid pushback on Destruction spells.', a: ['23%', '47%', '70%'] },
    { k: 'AgonizingFlames', n: 'Agonizing Flames', t: 2, r: 3, c: 1, m: 3, s: 'yes', d: 'Destruction spells deal {a} more, and Searing Pain crits more.', a: ['3%', '7%', '10%'] },
    { k: 'Conflagrate', n: 'Conflagrate', t: 2, r: 3, c: 2, m: 1, s: 'yes', d: 'An instant Fire hit on a target with Immolate. 10-sec cooldown.' },
    { k: 'Pyroclasm', n: 'Pyroclasm', t: 2, r: 4, c: 0, m: 2, s: 'utility', req: ['Intensity', 3], d: 'Soul Fire, Rain of Fire and Hellfire have a {a} chance to stun.', a: ['13%', '26%'] },
    { k: 'BaneOfHavoc', n: 'Bane of Havoc', t: 2, r: 4, c: 1, m: 1, s: 'utility', d: '15% of your damage to other targets is copied to this one.' },
    { k: 'FireAndBrimstone', n: 'Fire and Brimstone', t: 2, r: 4, c: 2, m: 3, s: 'yes', req: ['Conflagrate', 1], d: 'Conflagrate has {a} more crit chance.', a: ['8%', '17%', '25%'] },
    { k: 'ShadowAndFlame', n: 'Shadow and Flame', t: 2, r: 5, c: 2, m: 5, s: 'yes', d: 'Conflagrate gives +{a} Shadow damage and Shadowburn +{a} Fire damage for 20 sec.', a: ['2%', '4%', '6%', '8%', '10%'] },
    { k: 'Incinerate', n: 'Incinerate', t: 2, r: 6, c: 1, m: 1, s: 'yes', req: ['BaneOfHavoc', 1], d: 'A Fire nuke that deals 25% more to targets with Immolate. Usable from level 40.' },
  ];
  const TALENT_ICON = {"Wrack": "ability_deathknight_hemorrhagicfever", "ShadowMastery": "spell_shadow_shadetruesight", "SoulSiphon": "spell_shadow_lifedrain02", "SiphonLife": "spell_shadow_requiem", "CurseOfExhaustion": "spell_shadow_grimward", "Nightfall": "spell_shadow_twilight", "AmplifyCurse": "spell_shadow_contagion", "Pandemic": "spell_shadow_unstableaffliction_2", "FelConcentration": "spell_shadow_fingerofdeath", "ImprovedBoA": "spell_shadow_curseofsargeras", "ImprovedDrains": "spell_shadow_haunting", "ImprovedLifeTap": "spell_shadow_burningspirit", "SoulHarvesting": "inv_elemental_primal_shadow", "Malediction": "spell_shadow_curseofachimonde", "ImprovedCorruption": "spell_shadow_abominationexplosion", "Suppression": "spell_shadow_unsummonbuilding", "Malevolence": "spell_shadow_focusedpower", "DemonicPact": "inv_ability_soulharvesterwarlock_demonicsoul", "MasterDemonologist": "spell_shadow_shadowpact", "SoulLink": "spell_shadow_gathershadows", "DemonicKnowledge": "spell_shadow_improvedvampiricembrace", "ImprovedFelhunter": "spell_shadow_summonfelhunter", "FelDomination": "spell_nature_removecurse", "DemonicBrand": "ability_demonhunter_chaoticimprint_fire", "Decimation": "spell_fire_fireball02", "MasterSummoner": "spell_shadow_impphaseshift", "DemonicEnergies": "spell_shadow_felmending", "DemonicSacrifice": "spell_shadow_psychicscream", "ImprovedSayaad": "ability_warlock_randomizesuccubusincubus", "DemonicAegis": "spell_shadow_ragingscream", "FelVitality": "spell_shadow_demonictactics", "ImprovedVoidwalker": "spell_shadow_summonvoidwalker", "ImprovedHealthFunnel": "spell_shadow_lifedrain", "UnholyPower": "spell_shadow_shadowworddominate", "DemonicEmbrace": "spell_shadow_metamorphosis", "ImprovedImp": "spell_shadow_summonimp", "Incinerate": "spell_fire_burnout", "ShadowAndFlame": "spell_fire_playingwithfire", "BaneOfHavoc": "ability_warlock_baneofhavoc", "FireAndBrimstone": "spell_fire_meteorstorm", "Pyroclasm": "spell_fire_volcano", "AgonizingFlames": "spell_fire_soulburn", "Conflagrate": "spell_fire_fireball", "DestructiveReach": "spell_shadow_corpseexplode", "Intensity": "spell_fire_lavaspawn", "Ruin": "spell_shadow_shadowwordpain", "Shadowburn": "spell_shadow_scourgebuild", "MoltenSkin": "ability_mage_moltenarmor", "Aftermath": "spell_fire_fire", "Cataclysm": "spell_fire_windsofwoe", "Bane": "spell_shadow_deathpact", "ImprovedShadowBolt": "spell_shadow_shadowbolt"};
  const TBY = Object.fromEntries(TALENTS.map(x => [x.k, x]));
  const TBYNAME = Object.fromEntries(TALENTS.map(x => [x.n, x]));
  // soft hyphens (U+00AD) give long words a clean break point inside the small talent cells
  const SHY = { Suppression: 'Suppres­sion', Corruption: 'Corrup­tion', Malediction: 'Male­diction',
    Concentration: 'Concen­tration', Malevolence: 'Male­volence', Voidwalker: 'Void­walker', Sacrifice: 'Sacri­fice',
    Decimation: 'Deci­mation', Domination: 'Domi­nation', Felhunter: 'Fel­hunter', Knowledge: 'Know­ledge',
    Demonologist: 'Demono­logist', Destructive: 'Destruc­tive', Cataclysm: 'Cata­clysm', Aftermath: 'After­math',
    Shadowburn: 'Shadow­burn', Conflagrate: 'Confla­grate', Agonizing: 'Agoniz­ing', Brimstone: 'Brim­stone',
    Pyroclasm: 'Pyro­clasm', Incinerate: 'Incin­erate', Nightfall: 'Night­fall', Summoner: 'Summon­er', Intensity: 'Inten­sity' };
  const short = n => n.replace('Improved ', 'Imp. ').replace('Curse of Exhaustion', 'Curse of Exhaust.').split(' ').map(w => SHY[w] || w).join(' ');

  const ORDER_WFB = seq([['Improved Corruption', 5], ['Improved Life Tap', 2], ['Improved Drains', 3], ['Soul Harvest', 2], ['Fel Concentration', 3],
    ['Suppression', 2], ['Amplify Curse', 1], ['Nightfall', 2], ['Siphon Life', 1], ['Demonic Embrace', 5], ['Improved Voidwalker', 3],
    ['Soul Siphon', 3], ['Improved Bane of Agony', 2], ['Shadow Mastery', 5], ['Wrack', 1], ['Malediction', 5], ['Curse of Exhaustion', 1],
    ['Suppression', 3], ['Fel Vitality', 2]]);
  const ORDER_531 = seq([['Improved Corruption', 5], ['Demonic Embrace', 5], ['Unholy Power', 5], ['Fel Vitality', 3], ['Improved Voidwalker', 2],
    ['Demonic Sacrifice', 1], ['Master Summoner', 2], ['Improved Sayaad', 2], ['Fel Domination', 1], ['Demonic Brand', 1],
    ['Soul Link', 1], ['Demonic Knowledge', 3], ['Master Demonologist', 4], ['Demonic Pact', 1],
    ['Suppression', 3], ['Improved Drains', 3], ['Malediction', 5], ['Pandemic', 3], ['Improved Bane of Agony', 2]]);
  // The page's group spec, 5/31/15 at 60: the spec card and demoDeep() in model.js. Below 60 it takes Demonology to Pact
  // first (Imp sacrificed from level 40), then Suppression, then Improved Shadow Bolt, Bane and Ruin: the fastest-leveling
  // of the legal orders tried, by the builder's own score averaged over levels 10 to 59.
  const ORDER_GROUP = seq([['Unholy Power', 5], ['Fel Vitality', 3], ['Demonic Energies', 2], ['Improved Sayaad', 3],
    ['Demonic Sacrifice', 1], ['Master Summoner', 2], ['Decimation', 2], ['Demonic Brand', 3], ['Soul Link', 1],
    ['Demonic Knowledge', 3], ['Master Demonologist', 5], ['Demonic Pact', 1], ['Suppression', 5],
    ['Improved Shadow Bolt', 5], ['Bane', 5], ['Ruin', 5]]);
  const PRESETS = [
    ['plan', 'Page plan'], ['solo', 'Solo 28/23/0'], ['531', 'Demonology to Pact'], ['group', 'Group 5/31/15'], ['wfb', 'wowforeverbuilds drain tank'],
    ['imm', 'Immolate build'], ['d34', '17/0/34 Destruction'], ['speed', 'Speedrun-style'], ['clear', 'Clear'],
  ];
  const PT_STEP = { Corr: 'Corruption', BoA: 'Agony', SL: 'Siphon Life', DoTs: 'Corruption, Agony, Siphon Life', Imm: 'Immolate', Wrack: 'Wrack' };
  const PT_FILL = { Wand: 'wand', DrainLife: 'Drain Life', DL: 'Drain Life', SB: 'Shadow Bolt', ShadowBolt: 'Shadow Bolt', SP: 'Searing Pain', Incin: 'Incinerate' };
  const PT_MOD = { 'Curse of the Elements': 'Curse of the Elements at the pull', 'Drain Soul finish': 'Drain Soul to finish',
    'Shadowburn finish': 'Shadowburn to finish', 'Soul Fire finish': 'Soul Fire under 35%', 'Death Coil': 'Death Coil when it is ready' };
  // The model names a rotation after the first policy that casts the same spells, so below level 4, before
  // Corruption, 'Corr+SB' means Shadow Bolt alone: drop the step that level cannot cast.
  function policyText(name, L) {
    const [base, ...mods] = String(name).split(' +');
    const parts = base.split('+').filter(p => L >= 4 || p !== 'Corr'), fill = PT_FILL[parts[parts.length - 1]];
    const head = (fill ? parts.slice(0, -1) : parts).map(p => PT_STEP[p] || p).join(', ');
    const text = head ? head + (fill ? ', then ' + fill : '') : fill.charAt(0).toUpperCase() + fill.slice(1);
    return [text].concat(mods.map(m => PT_MOD[m] || m)).join('. ');
  }
  const PETS_B = [['voidwalker', 'Voidwalker'], ['succubus', 'Succubus'], ['felhunter', 'Felhunter'], ['imp', 'Imp'], ['none', 'No demon']];
  const SACS = [['', 'None'], ['imp', 'Imp (+15% Shadow)'], ['succubus', 'Succubus (+15% Fire)'], ['voidwalker', 'Voidwalker (mana regen)'], ['felhunter', 'Felhunter (health regen)']];

  const bsaved = store.get('builder', {}) || {};
  const B = {
    ranks: Object.fromEntries(TALENTS.map(x => [x.k, 0])),
    pet: PETS_B.some(p => p[0] === bsaved.pet) ? bsaved.pet : 'voidwalker',
    sac: SACS.some(p => p[0] === bsaved.sac) ? bsaved.sac : '',
    aggro: bsaved.aggro === true, gear: bsaved.gear === 2 ? 2 : 1,
    preset: typeof bsaved.preset === 'string' ? bsaved.preset : null,   // a loaded preset follows the level until you edit it
    sel: 'ImprovedCorruption', tree: 0,
  };
  if (bsaved.ranks && typeof bsaved.ranks === 'object') TALENTS.forEach(x => { B.ranks[x.k] = Math.round(clamp(bsaved.ranks[x.k], 0, x.m, 0)); });
  const saveB = () => store.set('builder', { ranks: B.ranks, pet: B.pet, sac: B.sac, aggro: B.aggro, gear: B.gear, preset: B.preset });

  const spent = r => Object.values(r).reduce((a, b) => a + b, 0);
  const treeSpent = (r, t) => TALENTS.filter(x => x.t === t).reduce((a, x) => a + r[x.k], 0);
  function buildOk(r, level) {
    if (spent(r) > Math.max(0, level - 9)) return false;
    for (let t = 0; t < 3; t++) {
      const rows = [0, 0, 0, 0, 0, 0, 0];
      TALENTS.filter(x => x.t === t).forEach(x => { rows[x.r] += r[x.k]; });
      for (let i = 0; i < 7; i++) { let below = 0; for (let j = 0; j < i; j++) below += rows[j]; if (rows[i] && below < 5 * i) return false; }
    }
    return TALENTS.every(x => !r[x.k] || !x.req || r[x.req[0]] >= x.req[1]);
  }
  const canAdd = x => { if (B.ranks[x.k] >= x.m) return false; const r = Object.assign({}, B.ranks); r[x.k] += 1; return buildOk(r, state.level); };
  const canRemove = x => { if (!B.ranks[x.k]) return false; const r = Object.assign({}, B.ranks); r[x.k] -= 1; return buildOk(r, 60); };
  function lockReason(x) {
    if (B.ranks[x.k] >= x.m) return 'Maxed.';
    if (spent(B.ranks) >= Math.max(0, state.level - 9)) return 'No points left at level ' + state.level + '.';
    const below = TALENTS.filter(y => y.t === x.t && y.r < x.r).reduce((a, y) => a + B.ranks[y.k], 0);
    if (below < 5 * x.r) return 'Needs ' + 5 * x.r + ' points in ' + TREES[x.t] + ' first.';
    if (x.req && B.ranks[x.req[0]] < x.req[1]) return 'Needs ' + x.req[1] + ' in ' + TBY[x.req[0]].n + '.';
    return '';
  }
  function fromOrder(order, level) {
    const r = Object.fromEntries(TALENTS.map(x => [x.k, 0]));
    for (const name of order.slice(0, Math.max(0, level - 9))) { const x = TBYNAME[name]; if (x) r[x.k] += 1; }
    return r;
  }
  // Destruction leveling builds from the v8 tests (analysis/destro_leveling.py): a reader's Immolate build, the community
  // 17/0/34 with its row-gating fix, and a speedrun-style Shadowburn then Soul Harvest path
  const ORDER_IMM = seq([['Improved Corruption', 5], ['Bane', 5], ['Aftermath', 5], ['Shadowburn', 1], ['Ruin', 4], ['Conflagrate', 1],
    ['Ruin', 1], ['Agonizing Flames', 3], ['Cataclysm', 3], ['Fire and Brimstone', 3], ['Shadow and Flame', 5], ['Bane of Havoc', 1],
    ['Incinerate', 1], ['Suppression', 5], ['Improved Life Tap', 2], ['Malediction', 5], ['Molten Skin', 1]]);
  const ORDER_D34 = seq([['Improved Corruption', 5], ['Improved Shadow Bolt', 5], ['Bane', 5], ['Improved Life Tap', 2], ['Molten Skin', 3],
    ['Ruin', 5], ['Shadowburn', 1], ['Cataclysm', 3], ['Conflagrate', 1], ['Agonizing Flames', 3], ['Shadow and Flame', 5], ['Intensity', 3],
    ['Suppression', 5], ['Malediction', 3], ['Nightfall', 2]]);
  const ORDER_SPEED = seq([['Bane', 5], ['Cataclysm', 3], ['Aftermath', 2], ['Shadowburn', 1], ['Improved Corruption', 5], ['Soul Harvest', 2],
    ['Suppression', 3], ['Improved Drains', 3], ['Malediction', 5], ['Improved Bane of Agony', 2], ['Pandemic', 2], ['Siphon Life', 1],
    ['Soul Siphon', 3], ['Nightfall', 2], ['Shadow Mastery', 5], ['Wrack', 1], ['Pandemic', 1], ['Fel Concentration', 3], ['Improved Life Tap', 2]]);
  function setPresetRanks(id, L) {
    if (id === 'plan') { B.ranks = fromOrder(L >= 56 ? SOLO56 : TAL_ORDER, L); B.pet = 'voidwalker'; B.sac = ''; B.aggro = false; }
    if (id === 'solo') { B.ranks = fromOrder(SOLO56, L); B.pet = 'voidwalker'; B.sac = ''; B.aggro = false; }
    if (id === '531') { B.ranks = fromOrder(ORDER_531, L); B.pet = 'succubus'; B.sac = B.ranks.DemonicPact ? 'imp' : ''; }
    if (id === 'group') { B.ranks = fromOrder(ORDER_GROUP, L); B.pet = 'succubus'; B.sac = B.ranks.DemonicPact ? 'imp' : ''; }
    if (id === 'wfb') { B.ranks = fromOrder(ORDER_WFB, L); B.pet = 'voidwalker'; B.sac = ''; B.aggro = false; }
    if (id === 'imm') { B.ranks = fromOrder(ORDER_IMM, L); B.pet = 'voidwalker'; B.sac = ''; B.aggro = false; }
    if (id === 'd34') { B.ranks = fromOrder(ORDER_D34, L); B.pet = 'voidwalker'; B.sac = ''; B.aggro = false; }
    if (id === 'speed') { B.ranks = fromOrder(ORDER_SPEED, L); B.pet = 'voidwalker'; B.sac = ''; B.aggro = false; }
  }
  function builderFollowLevel() {
    if (!B.preset) return;
    const pet = B.pet, aggro = B.aggro;   // keep the demon you picked; only the points follow the level
    setPresetRanks(B.preset, state.level); B.pet = pet; B.aggro = aggro; saveB();
  }
  function applyPreset(id) {
    const L = state.level;
    B.preset = id === 'clear' ? null : id;
    setPresetRanks(id, L);
    if (id === 'clear') { B.ranks = Object.fromEntries(TALENTS.map(x => [x.k, 0])); B.sac = ''; }
    saveB(); renderBuilder(); announce('Preset loaded. ' + $('bSummary').textContent);
  }

  // model input from builder state, with the rules the model does not check itself
  function modelTalents(notes) {
    const tal = {};
    TALENTS.forEach(x => { if (B.ranks[x.k]) tal[x.k] = B.ranks[x.k]; });
    let pet = B.pet, sac = B.sac;
    if (sac && !B.ranks.DemonicSacrifice) { sac = ''; notes.push('Sacrifice needs the Demonic Sacrifice talent, so it is ignored.'); }
    if (sac && !B.ranks.DemonicPact && pet !== 'none') { pet = 'none'; notes.push('Without Demonic Pact, sacrificing leaves you with no demon, so this is scored with no pet.'); }
    if (sac && B.ranks.DemonicPact && sac === pet) { sac = ''; notes.push('Summoning the demon you sacrificed cancels the buff, so the sacrifice is ignored.'); }
    if (sac) tal._sac = sac;
    return { tal, pet };
  }

  function renderBuilder() {
    const L = state.level, pts = Math.max(0, L - 9), used = spent(B.ranks);
    $('bLevel').textContent = L;
    $('bPts').textContent = used + ' of ' + pts + ' points';
    // trees
    for (let t = 0; t < 3; t++) {
      const grid = $('bTree' + t); grid.textContent = '';
      $('bTreeHead' + t).textContent = TREES[t] + ' ' + treeSpent(B.ranks, t);
      TALENTS.filter(x => x.t === t).forEach(x => {
        const b = document.createElement('button');
        b.type = 'button'; b.className = 'tal s-' + x.s; b.dataset.k = x.k;
        b.style.gridRow = String(x.r + 1); b.style.gridColumn = String(x.c + 1);
        const rk = B.ranks[x.k];
        if (rk >= x.m) b.classList.add('max'); else if (rk) b.classList.add('some');
        if (!rk && !canAdd(x)) b.classList.add('locked'); else if (rk < x.m && canAdd(x)) b.classList.add('avail');
        if (x.k === B.sel) b.classList.add('sel');
        const icw = document.createElement('span'); icw.className = 'icw';
        const rr = document.createElement('span'); rr.className = 'tr'; rr.textContent = rk + '/' + x.m;
        icw.append(icon(TALENT_ICON[x.k], '', ''), rr);
        const nm = document.createElement('span'); nm.className = 'tn'; nm.textContent = short(x.n);
        b.append(icw, nm);
        b.setAttribute('aria-label', x.n + ', ' + rk + ' of ' + x.m + (x.s === 'yes' ? '' : ', utility') + '. Press to add a point, Shift press to remove one.');
        b.addEventListener('click', e => { B.sel = x.k; if (e.shiftKey) step(x, -1); else step(x, +1); });
        b.addEventListener('contextmenu', e => { e.preventDefault(); B.sel = x.k; step(x, -1); });
        b.addEventListener('focus', () => { if (B.sel !== x.k) { B.sel = x.k; renderInfo(); markSel(); } });
        grid.appendChild(b);
      });
    }
    document.querySelectorAll('#bTabs button').forEach(b => b.setAttribute('aria-pressed', String(Number(b.dataset.t) === B.tree)));
    document.querySelectorAll('.btree').forEach(el => el.classList.toggle('on', Number(el.dataset.t) === B.tree));
    $('bPet').value = B.pet; $('bSac').value = B.sac; $('bAggro').checked = B.aggro; $('bGear').value = String(B.gear);
    $('bAggroWrap').hidden = !(B.pet === 'succubus' || B.pet === 'felhunter' || B.pet === 'imp');
    renderInfo(); renderScore();
  }
  function markSel() { document.querySelectorAll('.tal').forEach(b => b.classList.toggle('sel', b.dataset.k === B.sel)); }
  function step(x, dir) {
    if (dir > 0 && canAdd(x)) { B.ranks[x.k] += 1; B.preset = null; }
    else if (dir < 0 && canRemove(x)) { B.ranks[x.k] -= 1; B.preset = null; }
    else { renderInfo(); markSel(); announce(x.n + ': ' + (dir > 0 ? lockReason(x) || 'cannot add.' : 'cannot remove, other talents depend on it.')); return; }
    saveB(); renderBuilder(); announce(x.n + ' ' + B.ranks[x.k] + ' of ' + x.m + '. ' + $('bSummary').textContent);
    const again = document.querySelector('.tal[data-k="' + x.k + '"]'); if (again) again.focus({ preventScroll: true });
  }
  function fill(x, rk) {
    if (!x.a) return x.d;
    const i = Math.max(0, Math.min(x.m - 1, rk - 1));
    return x.d.replace(/\{a\}/g, x.a[i]).replace(/\{b\}/g, x.b ? x.b[i] : '');
  }
  function renderInfo() {
    const x = TBY[B.sel], rk = B.ranks[x.k];
    $('bInfoName').textContent = x.n;
    const ii = $('bInfoIco'); if (ICONS[TALENT_ICON[x.k]]) { ii.src = ICONS[TALENT_ICON[x.k]]; ii.hidden = false; } else ii.hidden = true;
    $('bInfoRank').textContent = 'Rank ' + rk + '/' + x.m + ' · ' + TREES[x.t];
    $('bInfoNow').textContent = rk ? fill(x, rk) : 'Not taken.';
    $('bInfoNext').textContent = rk < x.m ? 'Next rank: ' + fill(x, rk + 1) : '';
    $('bInfoTag').textContent = x.s === 'yes' ? 'Counts in the score' : 'Utility, not in the score';
    $('bInfoTag').className = 'chip ' + (x.s === 'yes' ? 'c-proof' : x.s === 'utility' ? 'c-known' : 'c-test');
    const why = lockReason(x);
    $('bInfoLock').textContent = rk < x.m && why ? why : '';
    $('bMinus').disabled = !canRemove(x); $('bPlus').disabled = !canAdd(x);
  }
  const HP_MULTS = [0.9, 1.0, 1.1];   // mob health 90%, 100% and 110%: kill time snaps to DoT ticks otherwise
  function renderScore() {
    const L = state.level, notes = [];
    const { tal, pet } = modelTalents(notes);
    const mine = LevelingModel.evaluate(L, tal, pet, B.gear, { aggro: B.aggro, hpMults: HP_MULTS });
    const planR = fromOrder(L >= 56 ? SOLO56 : TAL_ORDER, L), planTal = {};
    TALENTS.forEach(x => { if (planR[x.k]) planTal[x.k] = planR[x.k]; });
    const plan = LevelingModel.evaluate(L, planTal, 'voidwalker', B.gear, { hpMults: HP_MULTS });
    const perHour = n => Math.round(3600 / n);
    $('bSpk').textContent = mine.spk.toFixed(1) + ' s';
    $('bKph').textContent = perHour(mine.spk) + ' kills an hour';
    $('bSplit').textContent = mine.ttk.toFixed(1) + ' s fighting, 8 s walking, ' + mine.rest.toFixed(1) + ' s resting';
    const diff = (plan.spk / mine.spk - 1) * 100;
    const same = Math.abs(diff) < 0.5;
    $('bVs').textContent = same ? 'About the same as the page plan at level ' + L + '.'
      : (diff > 0 ? diff.toFixed(1) + '% faster' : (-diff).toFixed(1) + '% slower') + ' than the page plan at level ' + L + ' (' + plan.spk.toFixed(1) + ' s per kill with a Voidwalker).';
    $('bVs').className = 'bvs ' + (same ? '' : diff > 0 ? 'up' : 'down');
    $('bRot').textContent = policyText(mine.policy, L);
    const unscored = TALENTS.filter(x => B.ranks[x.k] && x.s !== 'yes').map(x => x.n);
    if (unscored.length) notes.push('Not in the score: ' + unscored.join(', ') + '.');
    if (B.aggro && $('bAggroWrap').hidden === false) notes.push('Assumes your pet holds the mob like a Voidwalker. Test 6 checks whether Demonic Brand makes that true.');
    const nl = $('bNotes'); nl.textContent = '';
    notes.forEach(n => { const li = document.createElement('li'); li.textContent = n; nl.appendChild(li); });
    $('bSummary').textContent = mine.spk.toFixed(1) + ' seconds per kill, ' + $('bVs').textContent;
    $('bLink').value = location.href.split('#')[0] + '#' + encodeBuild();
  }

  // share links: #b-<level>-<ranks in talent order>-<pet><sac><aggro><gear>
  const PET_CODE = { voidwalker: 'v', succubus: 's', felhunter: 'f', imp: 'i', none: 'n' };
  const SAC_CODE = { '': 'x', imp: 'i', succubus: 's', voidwalker: 'v', felhunter: 'f' };
  const inv = o => Object.fromEntries(Object.entries(o).map(([a, b]) => [b, a]));
  function encodeBuild() {
    return 'b-' + state.level + '-' + TALENTS.map(x => B.ranks[x.k]).join('') + '-' + PET_CODE[B.pet] + SAC_CODE[B.sac] + (B.aggro ? '1' : '0') + B.gear;
  }
  function decodeBuild(h) {
    const m = h.match(/^b-(\d{1,2})-([0-5]{52})-([vsfin])([xisvf])([01])([12])$/);
    if (!m) return false;
    const L = Math.round(clamp(m[1], 10, 60, 60));
    const r = {}; TALENTS.forEach((x, i) => { r[x.k] = Math.min(x.m, Number(m[2][i])); });
    if (!buildOk(r, L)) return false;
    B.ranks = r; B.pet = inv(PET_CODE)[m[3]]; B.sac = inv(SAC_CODE)[m[4]]; B.aggro = m[5] === '1'; B.gear = Number(m[6]); B.preset = null;
    saveB(); setLevel(L, false);
    return true;
  }

  // wiring
  (function wireBuilder() {
    const pr = $('bPresets');
    PRESETS.forEach(([id, label]) => { const b = document.createElement('button'); b.type = 'button'; b.textContent = label; b.addEventListener('click', () => applyPreset(id)); pr.appendChild(b); });
    const ps = $('bPet'); PETS_B.forEach(([v, l]) => { const o = document.createElement('option'); o.value = v; o.textContent = l; ps.appendChild(o); });
    const ss = $('bSac'); SACS.forEach(([v, l]) => { const o = document.createElement('option'); o.value = v; o.textContent = l; ss.appendChild(o); });
    ps.addEventListener('change', e => { B.pet = e.target.value; saveB(); renderBuilder(); announce($('bSummary').textContent); });
    ss.addEventListener('change', e => { B.sac = e.target.value; saveB(); renderBuilder(); announce($('bSummary').textContent); });
    $('bAggro').addEventListener('change', e => { B.aggro = e.target.checked; saveB(); renderBuilder(); announce($('bSummary').textContent); });
    $('bGear').addEventListener('change', e => { B.gear = Number(e.target.value) === 2 ? 2 : 1; saveB(); renderBuilder(); announce($('bSummary').textContent); });
    $('bMinus').addEventListener('click', () => step(TBY[B.sel], -1));
    $('bPlus').addEventListener('click', () => step(TBY[B.sel], +1));
    $('bLvlDown').addEventListener('click', () => setLevel(state.level - 1, true));
    $('bLvlUp').addEventListener('click', () => setLevel(state.level + 1, true));
    document.querySelectorAll('#bTabs button').forEach(b => b.addEventListener('click', () => { B.tree = Number(b.dataset.t); renderBuilder(); }));
    $('bCopy').addEventListener('click', () => {
      const v = $('bLink').value;
      const done = ok => { $('bCopy').textContent = ok ? 'Copied' : 'Select and copy'; setTimeout(() => { $('bCopy').textContent = 'Copy link'; }, 1600); };
      try { navigator.clipboard.writeText(v).then(() => done(true), () => { $('bLink').select(); done(false); }); }
      catch (e) { $('bLink').select(); done(false); }
    });
    if (!spent(B.ranks)) B.ranks = fromOrder(state.level >= 56 ? SOLO56 : TAL_ORDER, state.level);
  })();
