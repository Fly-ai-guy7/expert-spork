# Thunder Herd — buffalo-style slot emulator

Original 5×4, 1,024-ways slot with the mechanics of the classic Vegas buffalo games. **Play-money demo only.**

## Play
Open `index.html` in any modern browser (no build, no dependencies), or `npm start` and visit http://localhost:8080.
Space = spin / quick-stop. Works on phone and desktop.

## Features
- 1,024 ways, 3+ symbols from reel 1 · hand-drawn SVG symbols (no trademarked art)
- Physics-style reels with bounce, scatter anticipation (glow + tension sound) on reels 4–5
- 🌅 Wild on reels 2–4; in free spins wilds carry ×2/×3/×5 and **multiply together** across reels
- 🪙 Scatter 3/4/5 → 8/15/20 free spins, retriggerable
- Rolling win counters, coin showers, Big / Mega / Epic win tiers (20× / 50× / 200× bet), 5,000× max-win cap
- Buy Feature (62× bet, ≈58× average return), autoplay (10–∞, stop-on-feature / big-win), turbo, music + synthesised SFX
- Session stats (spins, wagered, won, session RTP, biggest win, last rounds) saved in the browser

## Maths
| | |
|---|---|
| Simulated RTP | ≈ 94.6% (30M rounds), buy feature ≈ 93.5% |
| Hit frequency | ≈ 55% |
| Feature trigger | ≈ 1 in 145 spins |
| Max win | 5,000× bet |

Files: `engine.js` (pure logic, browser + Node) · `app.js` (UI/flow) · `symbols.js` · `style.css`.

```
npm test          # 8 engine unit tests (ways, wilds, multipliers, scatter, cap)
npm run sim       # RTP / volatility simulation, e.g. node sim.js 10000000 [seed]
npm run sim:feature
```
Tune `PAY`, `W_BASE`, `W_FREE`, `BET_DIV` in `engine.js`, then re-run the sim.

Reels draw each cell from weighted odds (not fixed physical strips), via `crypto.getRandomValues` in the browser. Not affiliated with Aristocrat or any commercial title.
