# Thunder Herd — buffalo-style slot emulator

Original 5x4, 1,024-ways slot with the mechanics of the classic Vegas buffalo games. Play-money demo only.

- **Play:** open `index.html` in a browser (no build, no dependencies). Space = spin.
- **Maths:** `engine.js` (pure logic, shared by browser and Node). Wild ×2/×3/×5 multipliers stack in free spins; 🪙 scatter 3/4/5 = 8/15/20 spins, retriggerable; 5,000× max-win cap.
- **RTP check:** `node sim.js 10000000 [seed]` — measured ≈ 94.6% over 30M rounds, ~55% hit rate, feature ≈ 1 in 145 spins.
- **Tuning:** edit `PAY`, the `W_BASE`/`W_FREE` weights or `BET_DIV` in `engine.js`, then re-run `sim.js`.

Symbols are emoji/CSS, so no trademarked art. Not affiliated with Aristocrat or any commercial title.
