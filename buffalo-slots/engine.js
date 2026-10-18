/* Thunder Herd — slot maths engine (5 reels x 4 rows, 1024 ways).
 * Pure logic, no DOM. Works in browser (window.Engine) and Node (module.exports).
 * Original game, Buffalo-style mechanics. Not affiliated with any commercial title. */
(function (root) {
  'use strict';

  const REELS = 5, ROWS = 4;

  // Symbol ids
  const SYM = ['BUF', 'EAG', 'COU', 'WOL', 'ELK', 'A', 'K', 'Q', 'J', 'WILD', 'COIN'];
  const WILD = 'WILD', COIN = 'COIN';

  // Pay per matching "way", in multiples of (totalBet / BET_DIV), keyed by reel count.
  const BET_DIV = 30.7;
  const PAY = {
    BUF: { 3: 10, 4: 40, 5: 150 },
    EAG: { 3: 6, 4: 24, 5: 80 },
    COU: { 3: 5, 4: 18, 5: 60 },
    WOL: { 3: 4, 4: 14, 5: 40 },
    ELK: { 3: 3, 4: 10, 5: 30 },
    A:   { 3: 1.5, 4: 5, 5: 16 },
    K:   { 3: 1.5, 4: 5, 5: 16 },
    Q:   { 3: 1, 4: 4, 5: 12 },
    J:   { 3: 1, 4: 4, 5: 12 }
  };

  // Scatter pays anywhere, x total bet, and awards free spins.
  const COIN_PAY = { 3: 2, 4: 10, 5: 100 };
  const FREE_SPINS = { 3: 8, 4: 15, 5: 20 };
  const MAX_WIN = 5000; // x total bet; a round is capped here
  const BUY_COST = 52;  // x total bet for Buy Feature (8 free spins). Measured value ≈ 49.7x incl. scatter -> ~95.5% RTP

  // ---- v3 features -------------------------------------------------------
  // Thunderstrike: base game only. With probability p, lightning turns 1-3 cells on reels 2-4 into wilds.
  const STRIKE = { p: 0.06, max: 3 };
  // Lightning Jackpot: random award on a paid spin (x total bet). Part of the RTP budget.
  const JACKPOT = { p: 1 / 2500, tiers: [
    { id: 'MINI', x: 20, w: 70 }, { id: 'MINOR', x: 50, w: 22 }, { id: 'MAJOR', x: 250, w: 7 }, { id: 'GRAND', x: 1000, w: 1 } ] };
  // Thunder Bet (ante): costs 1.25x, scatter weight is raised on base spins.
  const ANTE = { cost: 1.25, coin: 2.42 };
  // Free-spin "herds": player picks before the feature. Tuned to similar average return, very different shape.
  const MODES = {
    classic:  { label: 'Stampede', mul: 1,   wild: 6, mults: [{ v: 2, w: 55 }, { v: 3, w: 35 }, { v: 5, w: 10 }] },
    marathon: { label: 'Long Trail', mul: 1.5, wild: 5.5, mults: [{ v: 2, w: 70 }, { v: 3, w: 25 }, { v: 5, w: 5 }] },
    blitz:    { label: 'Thunderclap', mul: 0.5, wild: 4.85, mults: [{ v: 3, w: 60 }, { v: 5, w: 30 }, { v: 10, w: 10 }] }
  };

  // Cell weights per reel (wild only on reels 2-4, i.e. index 1..3).
  const W_BASE = [
    { BUF: 5, EAG: 7, COU: 8, WOL: 9, ELK: 10, A: 14, K: 14, Q: 15, J: 15, WILD: 0, COIN: 2 },
    { BUF: 5, EAG: 7, COU: 8, WOL: 9, ELK: 10, A: 14, K: 14, Q: 15, J: 15, WILD: 3, COIN: 2 },
    { BUF: 5, EAG: 7, COU: 8, WOL: 9, ELK: 10, A: 14, K: 14, Q: 15, J: 15, WILD: 3, COIN: 2 },
    { BUF: 5, EAG: 7, COU: 8, WOL: 9, ELK: 10, A: 14, K: 14, Q: 15, J: 15, WILD: 3, COIN: 2 },
    { BUF: 5, EAG: 7, COU: 8, WOL: 9, ELK: 10, A: 14, K: 14, Q: 15, J: 15, WILD: 0, COIN: 2 }
  ];
  // Free spins: more wilds, wilds carry 2x / 3x multipliers that multiply together.
  const freeWeights = (mode) => W_BASE.map((w, i) => Object.assign({}, w, { WILD: i >= 1 && i <= 3 ? mode.wild : 0 }));
  const modeWeights = (m) => m._w || (m._w = freeWeights(m)); // cached per mode (tuning scripts reset m._w)
  const W_ANTE = W_BASE.map((w) => Object.assign({}, w, { COIN: ANTE.coin }));

  function makeRng(seed) {
    if (seed == null) return Math.random;
    let a = seed >>> 0; // mulberry32
    return function () {
      a = (a + 0x6D2B79F5) >>> 0;
      let t = a;
      t = Math.imul(t ^ (t >>> 15), t | 1);
      t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  }

  function pickWeighted(table, rng) {
    let total = 0;
    for (const k in table) total += table[k];
    let r = rng() * total;
    for (const k in table) { r -= table[k]; if (r < 0) return k; }
    return Object.keys(table)[0];
  }

  function pickMult(rng, table) {
    let total = 0;
    for (const m of table) total += m.w;
    let r = rng() * total;
    for (const m of table) { r -= m.w; if (r < 0) return m.v; }
    return table[0].v;
  }

  /**
   * Generate grid[reel][row] of {s, m}. opts: { ante, mode }.
   * Base game may carry grid.strike = [{c, r, from}] (Thunderstrike wilds already applied to the grid).
   */
  function spinGrid(free, rng, opts) {
    opts = opts || {};
    const mode = MODES[opts.mode] || MODES.classic;
    const weights = free ? modeWeights(mode) : (opts.ante ? W_ANTE : W_BASE);
    const grid = [];
    for (let c = 0; c < REELS; c++) {
      const col = [];
      for (let r = 0; r < ROWS; r++) {
        const s = pickWeighted(weights[c], rng);
        col.push({ s, m: s === WILD && free ? pickMult(rng, mode.mults) : 1 });
      }
      grid.push(col);
    }
    if (!free && rng() < STRIKE.p) {
      const n = 1 + Math.floor(rng() * STRIKE.max), strike = [];
      for (let i = 0; i < n; i++) {
        const c = 1 + Math.floor(rng() * 3), r = Math.floor(rng() * ROWS);
        if (grid[c][r].s === WILD || strike.some((x) => x.c === c && x.r === r)) continue;
        strike.push({ c, r, from: grid[c][r].s }); grid[c][r] = { s: WILD, m: 1 };
      }
      if (strike.length) grid.strike = strike;
    }
    return grid;
  }

  /** Lightning Jackpot roll for a paid spin. Returns null or {id, x}. */
  function rollJackpot(rng) {
    if (rng() >= JACKPOT.p) return null;
    let total = 0; JACKPOT.tiers.forEach((t) => { total += t.w; });
    let r = rng() * total;
    for (const t of JACKPOT.tiers) { r -= t.w; if (r < 0) return { id: t.id, x: t.x }; }
    return { id: JACKPOT.tiers[0].id, x: JACKPOT.tiers[0].x };
  }

  const featureSpins = (n, mode) => Math.max(1, Math.round(FREE_SPINS[Math.min(n, 5)] * (MODES[mode] || MODES.classic).mul));

  /**
   * Evaluate a grid. Returns { total (x totalBet), wins: [...], coins, coinPay, fs }.
   * Ways: per symbol, count matching (or wild) cells on each consecutive reel from reel 1.
   * Wild multipliers (free spins only) multiply together across reels used in the win.
   */
  function evaluate(grid) {
    const wins = [];
    let total = 0;

    for (const sym of Object.keys(PAY)) {
      let ways = 1, mult = 1, reels = 0;
      const cells = [];
      for (let c = 0; c < REELS; c++) {
        let n = 0, reelMult = 1;
        for (let r = 0; r < ROWS; r++) {
          const cell = grid[c][r];
          if (cell.s === sym || cell.s === WILD) {
            n++; cells.push([c, r]);
            if (cell.s === WILD) reelMult *= cell.m; // multiple wilds on a reel stack their multiplier
          }
        }
        if (n === 0) break;
        ways *= n; mult *= reelMult; reels++;
      }
      if (reels >= 3) {
        const pay = PAY[sym][reels] * ways * mult / BET_DIV;
        total += pay;
        wins.push({ sym, reels, ways, mult, pay, cells });
      }
    }

    let coins = 0; const coinCells = [];
    for (let c = 0; c < REELS; c++) for (let r = 0; r < ROWS; r++) {
      if (grid[c][r].s === COIN) { coins++; coinCells.push([c, r]); }
    }
    const coinPay = COIN_PAY[Math.min(coins, 5)] || 0;
    total += coinPay;
    const fs = coins >= 3 ? FREE_SPINS[Math.min(coins, 5)] : 0;

    return { total, wins, coins, coinCells, coinPay, fs };
  }

  /** Run a free-spins feature from `spins` start. Returns x-bet total. */
  function playFeature(rng, spins, capRemaining, mode) {
    let total = 0, played = 0;
    while (spins > 0 && played < 500 && total < capRemaining) {
      spins--; played++;
      const e = evaluate(spinGrid(true, rng, { mode }));
      total += e.total; spins += Math.round(e.fs * (MODES[mode] || MODES.classic).mul) || 0;
    }
    return Math.min(total, capRemaining);
  }

  /** Play a whole paid spin including jackpot and free-spin feature. opts: { ante, mode }. Results in x of base bet. */
  function playRound(rng, opts) {
    opts = opts || {};
    const g = spinGrid(false, rng, opts), base = evaluate(g);
    const jp = rollJackpot(rng);
    let total = base.total + (jp ? jp.x : 0), played = 0, spins = base.fs ? featureSpins(base.coins, opts.mode) : 0;
    const startTotal = total;
    while (spins > 0 && played < 500 && total < MAX_WIN) {
      spins--; played++;
      const e = evaluate(spinGrid(true, rng, { mode: opts.mode }));
      total += e.total; spins += e.fs ? featureSpins(e.coins, opts.mode) : 0;
    }
    if (total > MAX_WIN) total = MAX_WIN;
    return { total, baseTotal: base.total, jackpot: jp, struck: !!g.strike, triggered: base.fs > 0, freeSpinsPlayed: played, freeTotal: total - startTotal };
  }

  const api = {
    REELS, ROWS, MAX_WIN, BUY_COST, SYM, WILD, COIN, PAY, BET_DIV, COIN_PAY, FREE_SPINS,
    STRIKE, JACKPOT, ANTE, MODES, featureSpins, rollJackpot,
    makeRng, spinGrid, evaluate, playRound, playFeature
  };
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  else root.Engine = api;
})(typeof window !== 'undefined' ? window : globalThis);
