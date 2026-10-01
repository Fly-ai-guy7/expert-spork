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
  const BET_DIV = 26;
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
  const BUY_COST = 62;  // x total bet for Buy Feature (8 free spins). Measured value ≈ 58x -> ~93.5% RTP

  // Cell weights per reel (wild only on reels 2-4, i.e. index 1..3).
  const W_BASE = [
    { BUF: 5, EAG: 7, COU: 8, WOL: 9, ELK: 10, A: 14, K: 14, Q: 15, J: 15, WILD: 0, COIN: 2 },
    { BUF: 5, EAG: 7, COU: 8, WOL: 9, ELK: 10, A: 14, K: 14, Q: 15, J: 15, WILD: 3, COIN: 2 },
    { BUF: 5, EAG: 7, COU: 8, WOL: 9, ELK: 10, A: 14, K: 14, Q: 15, J: 15, WILD: 3, COIN: 2 },
    { BUF: 5, EAG: 7, COU: 8, WOL: 9, ELK: 10, A: 14, K: 14, Q: 15, J: 15, WILD: 3, COIN: 2 },
    { BUF: 5, EAG: 7, COU: 8, WOL: 9, ELK: 10, A: 14, K: 14, Q: 15, J: 15, WILD: 0, COIN: 2 }
  ];
  // Free spins: more wilds, wilds carry 2x / 3x multipliers that multiply together.
  const W_FREE = W_BASE.map((w, i) => Object.assign({}, w, { WILD: i >= 1 && i <= 3 ? 6 : 0 }));
  const WILD_MULT_TABLE = [{ v: 2, w: 55 }, { v: 3, w: 35 }, { v: 5, w: 10 }];

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

  function pickMult(rng) {
    let total = 0;
    for (const m of WILD_MULT_TABLE) total += m.w;
    let r = rng() * total;
    for (const m of WILD_MULT_TABLE) { r -= m.w; if (r < 0) return m.v; }
    return 2;
  }

  /** Generate a grid[reel][row] of {s: symbol, m: wildMultiplier}. */
  function spinGrid(free, rng) {
    const weights = free ? W_FREE : W_BASE;
    const grid = [];
    for (let c = 0; c < REELS; c++) {
      const col = [];
      for (let r = 0; r < ROWS; r++) {
        const s = pickWeighted(weights[c], rng);
        col.push({ s, m: s === WILD && free ? pickMult(rng) : 1 });
      }
      grid.push(col);
    }
    return grid;
  }

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

  /** Run a free-spins feature from `spins` start (used by Buy Feature and by playRound). Returns x-bet total. */
  function playFeature(rng, spins, capRemaining) {
    let total = 0, played = 0;
    while (spins > 0 && played < 500 && total < capRemaining) {
      spins--; played++;
      const e = evaluate(spinGrid(true, rng));
      total += e.total; spins += e.fs;
    }
    return Math.min(total, capRemaining);
  }

  /** Play a whole paid spin including any free-spin feature. Returns the x-bet result tree. */
  function playRound(rng) {
    const base = evaluate(spinGrid(false, rng));
    let total = base.total, spins = base.fs, played = 0;
    const free = [];
    while (spins > 0 && played < 500 && total < MAX_WIN) {
      spins--; played++;
      const g = spinGrid(true, rng);
      const e = evaluate(g);
      total += e.total;
      spins += e.fs;
      free.push(e.total);
    }
    if (total > MAX_WIN) total = MAX_WIN;
    return { total, baseTotal: base.total, triggered: base.fs > 0, freeSpinsPlayed: played, freeTotal: total - base.total };
  }

  const api = {
    REELS, ROWS, MAX_WIN, BUY_COST, SYM, WILD, COIN, PAY, BET_DIV, COIN_PAY, FREE_SPINS,
    makeRng, spinGrid, evaluate, playRound, playFeature
  };
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  else root.Engine = api;
})(typeof window !== 'undefined' ? window : globalThis);
