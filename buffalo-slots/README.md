# Thunder Herd — buffalo-style slot emulator

Original 5×4, 1,024-ways slot with the mechanics of the classic Vegas buffalo games. **Play-money demo only.**

## Play
Private by design — not hosted publicly. Open `index.html` in any modern browser (no build, no dependencies), or `npm start` and visit http://localhost:8080.
Space = spin / quick-stop. Works on phone and desktop.

## Features
- 1,024 ways, 3+ symbols from reel 1 · hand-drawn SVG symbols (no trademarked art)
- Physics-style reels with bounce, scatter anticipation (glow + tension sound) on reels 4–5
- 🌅 Wild on reels 2–4; in free spins wilds carry multipliers that **multiply together** across reels
- 🪙 Scatter 3/4/5 → free spins, retriggerable
- **⚡ Thunderstrike** (≈6% of base spins): lightning turns 1–3 cells on reels 2–4 into wilds
- **Lightning Jackpot** (≈1 in 2,500 paid spins): Mini 20× · Minor 50× · Major 250× · Grand 1,000× with a wheel reveal
- **Thunder Bet**: +25% stake, scatters land ≈1.6× as often (RTP-balanced)
- **Choose your herd** before free spins: Stampede (8 spins, wilds ×2/3/5), Long Trail (12 spins, ×2/3/5 skewed low), Thunderclap (4 spins, ×3/5/10). Tuned to similar average return, very different swings
- **Gamble**: double or nothing on card colour, up to 3 times (fair 50/50)
- Buy Feature (52× bet), autoplay with stop-on-feature / big-win and **loss / win limits**, turbo
- Big / Mega / Epic win tiers (20× / 50× / 200×), rolling counters, coin showers, 5,000× max-win cap
- 16 achievements, balance-over-time chart, top-5 wins, session net and timer, 30-minute reality check
- English / Arabic (عربي) UI toggle, keyboard shortcuts (Space, ↑↓, M, Q, B, A, T, S, I)
- **Practice tools** in Settings: force free spins, a big win, Thunderstrike or a Major jackpot for the next spin (not counted in stats)
- Starts with 1,000,000 credits; bets from 40 to 250,000

## Maths
| | |
|---|---|
| Simulated RTP, standard bet | ≈ 94.8% (≈18M rounds) |
| Simulated RTP, Thunder Bet (on 1.25× stake) | ≈ 95.6% |
| Buy feature (52× bet, 8 spins) | ≈ 95.5% |
| Herd value (each, 8-spin equivalent) | 47.4× – 49.4× bet |
| Max win | 5,000× bet |

Files: `engine.js` (pure logic, browser + Node) · `app.js` (UI/flow) · `symbols.js` · `style.css`.

```
npm test          # 12 engine unit tests (ways, wilds, multipliers, scatter, cap, strike, jackpot, herds, ante)
npm run sim       # RTP / volatility simulation, e.g. node sim.js 10000000 [seed]
npm run sim:feature   # feature value; sim.js args: rounds seed [ante] [classic|marathon|blitz]
```
Tune `PAY`, `W_BASE`, `W_FREE`, `BET_DIV` in `engine.js`, then re-run the sim.

Reels draw each cell from weighted odds (not fixed physical strips), via `crypto.getRandomValues` in the browser. Not affiliated with Aristocrat or any commercial title.
