// Engine unit tests: node test.js
const assert = require('assert'); const E = require('./engine');
const g = (cols) => cols.map(col => col.map(s => typeof s === 'string' ? { s, m: 1 } : s));
const filler = ['Q', 'J', 'Q', 'J'];
let n = 0; const t = (name, fn) => { fn(); n++; console.log('ok -', name); };

t('3-of-a-kind, 1 way', () => {
  const r = E.evaluate(g([['BUF', 'J', 'Q', 'J'], ['BUF', 'Q', 'J', 'Q'], ['BUF', 'J', 'Q', 'J'], filler, filler]));
  const w = r.wins.find(x => x.sym === 'BUF'); assert(w && w.reels === 3 && w.ways === 1);
  assert.strictEqual(w.pay, E.PAY.BUF[3] / E.BET_DIV);
});
t('ways multiply across reels', () => {
  const r = E.evaluate(g([['EAG', 'EAG', 'J', 'Q'], ['EAG', 'EAG', 'EAG', 'Q'], ['EAG', 'J', 'Q', 'J'], filler, filler]));
  assert.strictEqual(r.wins.find(x => x.sym === 'EAG').ways, 2 * 3 * 1);
});
t('must start on reel 1', () => {
  const r = E.evaluate(g([filler, ['BUF', 'BUF', 'J', 'Q'], ['BUF', 'J', 'Q', 'J'], ['BUF', 'Q', 'J', 'Q'], filler]));
  assert(!r.wins.find(x => x.sym === 'BUF'));
});
t('wild substitutes, not for coin', () => {
  const r = E.evaluate(g([['WOL', 'J', 'Q', 'J'], ['WILD', 'Q', 'J', 'Q'], ['WOL', 'J', 'Q', 'J'], filler, filler]));
  assert(r.wins.find(x => x.sym === 'WOL' && x.reels === 3));
  assert.strictEqual(r.coins, 0);
});
t('free-spin wild multipliers multiply across reels', () => {
  const r = E.evaluate(g([['ELK', 'J', 'Q', 'J'], [{ s: 'WILD', m: 2 }, 'Q', 'J', 'Q'], [{ s: 'WILD', m: 3 }, 'J', 'Q', 'J'], filler, filler]));
  const w = r.wins.find(x => x.sym === 'ELK'); assert.strictEqual(w.mult, 6);
});
t('scatter pays and awards spins', () => {
  const r = E.evaluate(g([['COIN', 'J', 'Q', 'J'], ['COIN', 'Q', 'J', 'Q'], filler, ['COIN', 'J', 'Q', 'J'], filler]));
  assert.strictEqual(r.coins, 3); assert.strictEqual(r.fs, 8); assert.strictEqual(r.coinPay, E.COIN_PAY[3]);
});
t('wild never generated on reels 1 and 5', () => {
  const rng = E.makeRng(9);
  for (let i = 0; i < 20000; i++) { const gr = E.spinGrid(true, rng); assert(gr[0].every(c => c.s !== 'WILD') && gr[4].every(c => c.s !== 'WILD')); }
});
t('round never exceeds max win', () => {
  const rng = E.makeRng(5); for (let i = 0; i < 200000; i++) assert(E.playRound(rng).total <= E.MAX_WIN);
});
t('thunderstrike only on reels 2-4 and recorded consistently', () => {
  const rng = E.makeRng(3); let seen = 0;
  for (let i = 0; i < 40000; i++) {
    const gr = E.spinGrid(false, rng);
    if (gr.strike) { seen++; gr.strike.forEach((x) => { assert(x.c >= 1 && x.c <= 3); assert.strictEqual(gr[x.c][x.r].s, 'WILD'); assert.notStrictEqual(x.from, 'WILD'); }); }
  }
  assert(seen > 40000 * 0.04 && seen < 40000 * 0.08, 'strike rate ' + seen);
});
t('jackpot frequency and tiers', () => {
  const rng = E.makeRng(8); let hits = 0; const ids = {};
  for (let i = 0; i < 3000000; i++) { const j = E.rollJackpot(rng); if (j) { hits++; ids[j.id] = 1; } }
  assert(hits > 900 && hits < 1500, 'jackpot hits ' + hits); assert(ids.MINI && ids.MINOR);
});
t('herd spin counts', () => {
  assert.deepStrictEqual([3, 4, 5].map((n) => E.featureSpins(n, 'classic')), [8, 15, 20]);
  assert.strictEqual(E.featureSpins(3, 'marathon'), 12); assert.strictEqual(E.featureSpins(3, 'blitz'), 4);
});
t('thunder bet raises scatter frequency, no wilds in free-spin pool for reels 1/5 in any herd', () => {
  const rng = E.makeRng(4); let a = 0, b = 0;
  for (let i = 0; i < 30000; i++) { E.spinGrid(false, rng).forEach((c) => c.forEach((x) => { if (x.s === 'COIN') a++; })); E.spinGrid(false, rng, { ante: true }).forEach((c) => c.forEach((x) => { if (x.s === 'COIN') b++; })); }
  assert(b > a * 1.1, 'ante coins ' + b + ' vs ' + a);
  for (const m of Object.keys(E.MODES)) for (let i = 0; i < 3000; i++) { const g = E.spinGrid(true, rng, { mode: m }); assert(g[0].every((x) => x.s !== 'WILD') && g[4].every((x) => x.s !== 'WILD')); }
});
console.log(n + ' tests passed');
