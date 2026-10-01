#!/usr/bin/env node
/* RTP / volatility simulator.  Usage: node sim.js [rounds=5000000] [seed=1] */
const E = require('./engine');

const N = parseInt(process.argv[2] || '5000000', 10);
const rng = E.makeRng(parseInt(process.argv[3] || '1', 10));

let sum = 0, sumSq = 0, baseSum = 0, hits = 0, trig = 0, freeSum = 0, freeSpins = 0, max = 0, bigWins = 0;
for (let i = 0; i < N; i++) {
  const r = E.playRound(rng);
  sum += r.total; sumSq += r.total * r.total; baseSum += r.baseTotal;
  if (r.baseTotal > 0) hits++;
  if (r.triggered) { trig++; freeSum += r.freeTotal; freeSpins += r.freeSpinsPlayed; }
  if (r.total > max) max = r.total;
  if (r.total >= 20) bigWins++;
}
const mean = sum / N, sd = Math.sqrt(sumSq / N - mean * mean);
const pct = (x) => (x * 100).toFixed(2) + '%';
console.log(`Rounds:            ${N.toLocaleString()}`);
console.log(`RTP (total):       ${pct(mean)}   (±${pct(1.96 * sd / Math.sqrt(N))} @95%)`);
console.log(`  base game:       ${pct(baseSum / N)}`);
console.log(`  free spins:      ${pct(freeSum / N)}`);
console.log(`Hit frequency:     ${pct(hits / N)} (base game)`);
console.log(`Feature trigger:   1 in ${(N / trig).toFixed(0)}  (avg ${(freeSpins / trig).toFixed(1)} spins, avg pay ${(freeSum / trig).toFixed(1)}x bet)`);
console.log(`Std dev:           ${sd.toFixed(2)}x bet / spin`);
console.log(`Wins >= 20x bet:   1 in ${(N / bigWins).toFixed(0)}`);
console.log(`Max win seen:      ${max.toFixed(0)}x bet`);
