(function () {
'use strict';
const E = window.Engine, SY = window.SYMBOLS, NAMES = window.SYMBOL_NAMES;
const $ = (id) => document.getElementById(id);
const BETS = [40, 80, 200, 400, 1000, 2000, 4000, 10000];
const START_BAL = 10000;
const TIER = { big: 20, mega: 50, epic: 200 };          // x bet
const fmt = (n) => Math.round(n).toLocaleString('en-GB');

/* ---------------- storage / state ---------------- */
const store = {
  get(k, d) { try { const v = localStorage.getItem('th_' + k); return v == null ? d : JSON.parse(v); } catch (e) { return d; } },
  set(k, v) { try { localStorage.setItem('th_' + k, JSON.stringify(v)); } catch (e) { /* private mode */ } }
};
const st = {
  bal: store.get('bal', START_BAL), betIdx: store.get('bet', 1),
  busy: false, quick: false, autoLeft: 0, free: false, fsLeft: 0, fsWin: 0,
  sound: store.get('sound', true), music: false, turbo: store.get('turbo', false),
  stopF: store.get('stopF', true), stopB: store.get('stopB', true),
  stats: store.get('stats', { spins: 0, wagered: 0, won: 0, biggest: 0, features: 0, hist: [] })
};
if (!(st.bal > 0) && !st.busy) st.bal = START_BAL;
if (!BETS[st.betIdx]) st.betIdx = 1;
const bet = () => BETS[st.betIdx];
const AUTO_STEPS = [0, 10, 25, 50, 100, Infinity];

/* RNG: crypto-grade in the browser; tests can queue forced grids */
const rng = () => { const a = new Uint32Array(1); crypto.getRandomValues(a); return a[0] / 4294967296; };
const forced = [];
window.ThunderHerd = { st, force: (g) => forced.push(g), E, parts: () => parts };
function nextGrid(free) { return forced.length ? forced.shift() : E.spinGrid(free, rng); }

const wait = (ms) => new Promise((r) => setTimeout(r, st.turbo ? ms * 0.35 : ms));

/* ---------------- audio (all synthesised) ---------------- */
let ac = null, master = null, noiseBuf = null;
function audio() {
  if (!st.sound) return null;
  try {
    if (!ac) {
      ac = new (window.AudioContext || window.webkitAudioContext)();
      master = ac.createGain(); master.gain.value = 0.9; master.connect(ac.destination);
      noiseBuf = ac.createBuffer(1, ac.sampleRate, ac.sampleRate);
      const d = noiseBuf.getChannelData(0); for (let i = 0; i < d.length; i++) d[i] = Math.random() * 2 - 1;
    }
    if (ac.state === 'suspended') ac.resume();
    return ac;
  } catch (e) { return null; }
}
function tone(f, d, type, vol, delay, slideTo) {
  const a = audio(); if (!a) return;
  const t = a.currentTime + (delay || 0), o = a.createOscillator(), g = a.createGain();
  o.type = type || 'sine'; o.frequency.setValueAtTime(f, t);
  if (slideTo) o.frequency.exponentialRampToValueAtTime(slideTo, t + d);
  g.gain.setValueAtTime(vol || 0.06, t); g.gain.exponentialRampToValueAtTime(0.0001, t + d);
  o.connect(g); g.connect(master); o.start(t); o.stop(t + d + 0.02);
}
function whoosh(d) {
  const a = audio(); if (!a) return;
  const t = a.currentTime, s = a.createBufferSource(), f = a.createBiquadFilter(), g = a.createGain();
  s.buffer = noiseBuf; s.loop = true; f.type = 'bandpass'; f.Q.value = 0.8;
  f.frequency.setValueAtTime(300, t); f.frequency.exponentialRampToValueAtTime(1800, t + d * 0.5); f.frequency.exponentialRampToValueAtTime(500, t + d);
  g.gain.setValueAtTime(0.0001, t); g.gain.exponentialRampToValueAtTime(0.1, t + 0.1); g.gain.exponentialRampToValueAtTime(0.0001, t + d);
  s.connect(f); f.connect(g); g.connect(master); s.start(t); s.stop(t + d + 0.05);
}
const sfx = {
  stop: () => { tone(150, 0.14, 'sine', 0.16, 0, 60); tone(900, 0.04, 'square', 0.02); },
  coin: () => { tone(988, 0.1, 'triangle', 0.09); tone(1568, 0.28, 'triangle', 0.09, 0.08); },
  win: (n) => { const sc = [523, 587, 659, 784, 880, 1047, 1175, 1319]; for (let i = 0; i < Math.min(3 + n, 8); i++) tone(sc[i], 0.18, 'triangle', 0.07, i * 0.07); },
  tick: () => tone(1400 + Math.random() * 300, 0.03, 'square', 0.02),
  fanfare: (lvl) => { const sc = [392, 523, 659, 784, 1047, 1319, 1568]; for (let i = 0; i < 5 + lvl * 2; i++) { tone(sc[i % 7] * (i > 6 ? 2 : 1), 0.35, 'triangle', 0.08, i * 0.11); tone(sc[i % 7] / 2, 0.35, 'sawtooth', 0.025, i * 0.11); } },
  tension: (d) => tone(200, d, 'sawtooth', 0.03, 0, 900)
};
let musicTimer = null, beat = 0;
function setMusic(on) {
  st.music = on; clearInterval(musicTimer); if (!on) return;
  const pent = [220, 261.6, 293.7, 329.6, 392];
  musicTimer = setInterval(() => {
    if (!audio()) return; beat++;
    if (beat % 4 === 0) { tone(70, 0.3, 'sine', 0.22, 0, 40); }
    if (beat % 4 === 2) tone(70, 0.2, 'sine', 0.12, 0, 40);
    if (Math.random() < 0.7) tone(pent[Math.floor(Math.random() * 5)] * (Math.random() < 0.3 ? 2 : 1), 0.5, 'triangle', 0.025);
  }, st.free ? 260 : 380);
}

/* ---------------- particles ---------------- */
const fx = $('fx'), fctx = fx.getContext('2d'); let parts = [], fxRun = false;
function fxResize() { const cab = $('cab'), d = window.devicePixelRatio || 1; fx.width = cab.clientWidth * d; fx.height = cab.clientHeight * d; fctx.setTransform(d, 0, 0, d, 0, 0); }
window.addEventListener('resize', fxResize);
function spawnCoins(n, o) {
  o = o || {}; const w = $('cab').clientWidth;
  for (let i = 0; i < n; i++) parts.push({
    x: o.x != null ? o.x : Math.random() * w, y: o.y != null ? o.y : -20 - Math.random() * 200,
    vx: (Math.random() - 0.5) * (o.spread || 3), vy: o.up ? -(4 + Math.random() * 8) : Math.random() * 2,
    g: 0.28, r: 7 + Math.random() * 7, ph: Math.random() * 6, vph: 0.15 + Math.random() * 0.2,
    c: Math.random() < 0.18 ? '#fff6c0' : '#ffc83d', life: 1
  });
  if (!fxRun) { fxRun = true; requestAnimationFrame(fxLoop); }
}
function fxLoop() {
  const h = $('cab').clientHeight, w = $('cab').clientWidth;
  fctx.clearRect(0, 0, w, h);
  parts = parts.filter((p) => p.y < h + 30);
  for (const p of parts) {
    p.vy += p.g; p.x += p.vx; p.y += p.vy; p.ph += p.vph;
    if (p.x < 6 || p.x > w - 6) { p.vx = -p.vx; p.x = Math.min(w - 6, Math.max(6, p.x)); }
    const sx = Math.abs(Math.cos(p.ph));
    fctx.save(); fctx.translate(p.x, p.y); fctx.scale(Math.max(sx, 0.12), 1);
    fctx.beginPath(); fctx.arc(0, 0, p.r, 0, 6.3); fctx.fillStyle = p.c; fctx.fill();
    fctx.lineWidth = 2; fctx.strokeStyle = '#a8660d'; fctx.stroke();
    fctx.beginPath(); fctx.arc(0, 0, p.r * 0.55, 0, 6.3); fctx.strokeStyle = '#fff3'; fctx.stroke(); fctx.restore();
  }
  if (parts.length) requestAnimationFrame(fxLoop); else fxRun = false;
}

/* ---------------- reels ---------------- */
const reelsEl = $('reels'), cols = [];
const isCard = (s) => 'AKQJ'.includes(s);
function tileHTML(cell, n) {
  const s = cell.s, cls = s === 'WILD' ? 'wild' : s === 'COIN' ? 'coin' : isCard(s) ? 'card' : 'animal' + (s === 'BUF' ? ' t1' : '');
  return `<div class="cell" style="height:${100 / n}%"><div class="tile ${cls}">${SY[s]}${cell.m > 1 ? `<span class="mbadge">×${cell.m}</span>` : ''}</div></div>`;
}
for (let c = 0; c < E.REELS; c++) {
  const el = document.createElement('div'); el.className = 'reel';
  const strip = document.createElement('div'); strip.className = 'strip'; el.appendChild(strip); reelsEl.appendChild(el);
  cols.push({ el, strip, cur: [] });
}
const randSym = () => { const k = Math.random(); return E.SYM[Math.floor(k * E.SYM.length)]; };
function setStatic(c, cells) { const col = cols[c]; col.cur = cells; col.strip.style.height = '100%'; col.strip.style.transform = ''; col.strip.innerHTML = cells.map((x) => tileHTML(x, 4)).join(''); }
for (let c = 0; c < E.REELS; c++) setStatic(c, Array.from({ length: 4 }, () => ({ s: ['A', 'K', 'Q', 'J', 'BUF', 'EAG', 'COU', 'WOL', 'ELK'][Math.floor(Math.random() * 9)], m: 1 })));
const cellEl = (c, r) => cols[c].strip.children[r];

let anims = [];
async function spinReels(grid) {
  const step = st.turbo ? 110 : 240, base = st.turbo ? 450 : 800;
  const durs = [], antic = []; let coins = 0;
  for (let c = 0; c < E.REELS; c++) {
    let d = c === 0 ? base : durs[c - 1] + step;
    if (c >= 3 && coins >= 2) { d = durs[c - 1] + (st.turbo ? 520 : 1200); antic.push(c); }
    durs.push(d); coins += grid[c].filter((x) => x.s === 'COIN').length;
  }
  whoosh(durs[4] / 1000);
  const timers = [];
  anims = cols.map((col, c) => {
    const d = durs[c], fill = Math.max(6, Math.round(d / 60) - 4);
    const seq = [...grid[c], ...Array.from({ length: fill }, () => ({ s: randSym(), m: 1 })), ...col.cur];
    const N = seq.length;
    col.strip.style.height = N * 25 + '%'; col.strip.innerHTML = seq.map((x) => tileHTML(x, N)).join('');
    col.el.classList.add('moving');
    timers.push(setTimeout(() => col.el.classList.remove('moving'), d * 0.8));
    return col.strip.animate(
      [{ transform: `translateY(${-((N - 4) / N) * 100}%)` }, { transform: 'translateY(0%)' }],
      { duration: d, easing: 'cubic-bezier(.35,.55,.3,1.08)', fill: 'forwards' });
  });
  antic.forEach((c) => {
    timers.push(setTimeout(() => {
      const a = $('anticip'), w = reelsEl.clientWidth - 10, cw = w / 5;
      a.style.left = 5 + c * (cw + 1) + 'px'; a.style.width = cw - 1 + 'px'; a.classList.add('on'); sfx.tension((durs[c] - durs[c - 1]) / 1000);
    }, durs[c - 1] * 1));
    timers.push(setTimeout(() => $('anticip').classList.remove('on'), durs[c] - 30));
  });
  await Promise.all(anims.map((a, c) => a.finished.then(() => {
    cols[c].el.classList.remove('moving'); setStatic(c, grid[c]); a.cancel(); sfx.stop();
    grid[c].forEach((x, r) => { if (x.s === 'COIN') { cellEl(c, r).classList.add('bump'); sfx.coin(); } });
  })));
  timers.forEach(clearTimeout); $('anticip').classList.remove('on'); anims = [];
}
function quickStop() { if (st.busy && anims.length && !st.quick) { st.quick = true; anims.forEach((a) => { a.playbackRate = 6; }); } }

/* ---------------- win presentation ---------------- */
function mark(cells, dim) {
  const set = new Set((cells || []).map(([c, r]) => c + ',' + r));
  for (let c = 0; c < E.REELS; c++) for (let r = 0; r < E.ROWS; r++) {
    const el = cellEl(c, r); el.classList.remove('win', 'dim');
    if (cells) el.classList.add(set.has(c + ',' + r) ? 'win' : 'dim');
  }
}
const lineText = (w) => `${NAMES[w.sym]} ×${w.reels} · ${w.ways} way${w.ways > 1 ? 's' : ''}${w.mult > 1 ? ' · wild ×' + w.mult : ''}  =  ${fmt(w.pay * bet())}`;
async function showWins(res) {
  if (!res.wins.length && !res.coinPay) return;
  const lines = res.wins.slice().sort((a, b) => b.pay - a.pay);
  const all = []; lines.forEach((w) => all.push(...w.cells)); res.coinCells.forEach((x) => all.push(x));
  mark(all); sfx.win(lines.length);
  await wait(950);
  if (lines.length > 1 && !st.quick) for (const w of lines.slice(0, 4)) { mark(w.cells); msg(lineText(w)); await wait(700); }
  mark(null);
}

/* ---------------- HUD ---------------- */
function msg(t) { $('msg').textContent = t; }
function saveAll() { store.set('bal', st.bal); store.set('bet', st.betIdx); store.set('stats', st.stats); }
function render() {
  $('bal').textContent = fmt(st.bal); $('betv').textContent = fmt(bet());
  document.body.classList.toggle('free', st.free);
  $('fsLeft').textContent = 'SPINS LEFT ' + st.fsLeft; $('fsWin').textContent = fmt(st.fsWin);
  $('betDn').disabled = $('betUp').disabled = $('max').disabled = $('buy').disabled = st.busy;
  const auto = st.autoLeft > 0;
  $('spin').textContent = st.busy ? (auto ? 'Stop' : '···') : 'Spin';
  $('spin').disabled = st.busy && !auto && !anims.length;
  $('auto').textContent = 'Auto ▸ ' + (auto ? (st.autoLeft === Infinity ? '∞' : st.autoLeft) : 'off');
  $('auto').classList.toggle('on', auto);
  $('buy').textContent = 'Buy feature · ' + fmt(E.BUY_COST * bet());
  saveAll();
}
function roll(el, from, to, ms, tick) {
  return new Promise((res) => {
    const t0 = performance.now(); let last = 0;
    const stepf = (t) => {
      const k = Math.min(1, (t - t0) / ms), v = from + (to - from) * (1 - Math.pow(1 - k, 2.2));
      el.textContent = fmt(v);
      if (tick && t - last > 70) { sfx.tick(); last = t; }
      if (k < 1 && !roll.skip) requestAnimationFrame(stepf); else { el.textContent = fmt(to); res(); }
    };
    roll.skip = false; requestAnimationFrame(stepf);
  });
}

/* ---------------- overlay ---------------- */
let ovResolve = null, ovToken = 0;
function overlay(o) {
  return new Promise((res) => {
    const tok = ++ovToken;
    $('ovTitle').textContent = o.title || ''; $('ovNum').textContent = o.num != null ? o.num : ''; $('ovSub').textContent = o.sub || '';
    $('overlay').classList.add('show'); ovResolve = () => { $('overlay').classList.remove('show'); ovResolve = null; res(); };
    if (o.ms) setTimeout(() => { if (tok === ovToken && ovResolve) ovResolve(); }, st.turbo ? o.ms * 0.5 : o.ms);
  });
}
$('overlay').addEventListener('click', () => { if (roll.skip === false && $('ovNum').dataset.rolling === '1') roll.skip = true; else if (ovResolve) ovResolve(); });

async function celebrate(amount, label) {
  const x = amount / bet();
  const lvl = x >= TIER.epic ? 3 : x >= TIER.mega ? 2 : x >= TIER.big ? 1 : 0;
  const title = label || ['', 'Big win', 'Mega win', 'Epic win'][lvl];
  const dur = [1800, 2600, 4200, 6500][lvl];
  sfx.fanfare(lvl);
  const p = overlay({ title, num: 0, sub: fmt(x) + '× bet' });
  $('ovNum').dataset.rolling = '1';
  const rain = setInterval(() => spawnCoins(4 + lvl * 4), 120);
  spawnCoins(20, { x: $('cab').clientWidth / 2, y: $('cab').clientHeight * 0.6, up: true, spread: 10 });
  await roll($('ovNum'), 0, amount, st.turbo ? dur * 0.5 : dur, true);
  clearInterval(rain); $('ovNum').dataset.rolling = '0';
  await Promise.race([p, new Promise((r) => setTimeout(r, st.turbo ? 700 : 1800))]);
  if (ovResolve) ovResolve();
}

/* ---------------- game flow ---------------- */
function recordRound(wag, win, buy) {
  const s = st.stats; s.spins++; s.wagered += wag; s.won += win; s.biggest = Math.max(s.biggest, win);
  s.hist.unshift({ bet: bet(), win, x: win / bet(), buy: !!buy }); s.hist = s.hist.slice(0, 18);
}
async function paySpin(free) {
  const grid = nextGrid(free);
  await spinReels(grid);
  const res = E.evaluate(grid), credits = Math.round(res.total * bet());
  return { res, credits, grid };
}
function describe(r, credits, free) {
  const top = r.wins.slice().sort((a, b) => b.pay - a.pay)[0];
  if (!top && r.coinPay) return `SCATTER ×${r.coins}  =  ${fmt(credits)}`;
  const mx = Math.max(1, ...r.wins.map((w) => w.mult));
  return `WIN ${fmt(credits)}  ·  ${NAMES[top.sym]} ×${top.reels}${r.wins.length > 1 ? '  +' + (r.wins.length - 1) + ' more' : ''}${free && mx > 1 ? '  ·  wild ×' + mx : ''}`;
}

async function runFeature(startSpins, roundSoFar, cap) {
  st.free = true; st.fsLeft = startSpins; st.fsWin = 0; setMusic(st.music); render();
  sfx.fanfare(1);
  await overlay({ title: startSpins + ' free spins', sub: 'Wilds carry ×2 ×3 ×5 — multipliers stack', ms: 2800 });
  let total = 0, played = 0;
  while (st.fsLeft > 0 && roundSoFar + total < cap) {
    st.fsLeft--; played++; st.quick = false; render();
    const f = await paySpin(true);
    total += f.credits; st.fsWin += f.credits;
    $('win').textContent = fmt(Math.min(roundSoFar + total, cap));
    msg(f.credits ? describe(f.res, f.credits, true) : 'No win');
    render();
    await showWins(f.res);
    if (f.res.fs > 0) { st.fsLeft += f.res.fs; render(); sfx.fanfare(0); await overlay({ title: '+' + f.res.fs + ' free spins', ms: 1500 }); }
  }
  st.free = false; setMusic(st.music);
  return { total: Math.min(total, cap - roundSoFar), played };
}

async function playRound(buy) {
  if (st.busy) return;
  const cost = buy ? E.BUY_COST * bet() : bet();
  if (st.bal < cost) { msg('Not enough credits — lower your bet or reset in settings.'); st.autoLeft = 0; render(); return; }
  st.busy = true; st.quick = false; st.bal -= cost; st.fsLeft = 0; st.fsWin = 0;
  $('win').textContent = '0'; msg(buy ? 'Feature purchased!' : 'Good luck…'); render();
  audio();
  const cap = E.MAX_WIN * bet(); let round = 0, featured = false;

  if (buy) {
    const sc = Math.round(E.COIN_PAY[3] * bet()); round += sc; featured = true;
    $('win').textContent = fmt(round);
    const f = await runFeature(E.FREE_SPINS[3], round, cap); round += f.total;
  } else {
    const r = await paySpin(false);
    round += r.credits; $('win').textContent = fmt(Math.min(round, cap));
    msg(r.credits ? describe(r.res, r.credits, false) : 'No win — spin again');
    await showWins(r.res);
    if (r.res.fs > 0) { featured = true; const f = await runFeature(r.res.fs, round, cap); round += f.total; }
  }
  round = Math.min(round, cap);
  st.bal += round; st.quick = false;
  if (featured) st.stats.features++;
  recordRound(cost, round, buy);
  $('win').textContent = fmt(round);
  const x = round / bet();
  if (featured) { msg(`Feature paid ${fmt(round)} credits (${x.toFixed(1)}× bet)`); await celebrate(round, x >= TIER.big ? null : 'Free spins win'); }
  else if (x >= TIER.big) await celebrate(round);
  else if (round === 0) msg('No win — spin again');
  st.busy = false; st.fsLeft = 0; render();

  // autoplay bookkeeping
  if (st.autoLeft > 0) {
    if (st.autoLeft !== Infinity) st.autoLeft--;
    if ((featured && st.stopF) || (x >= TIER.big && st.stopB) || st.bal < bet()) st.autoLeft = 0;
  }
  render();
  if (st.bal < bet() && st.bal <= 0) msg('Out of credits — reset the balance in Settings.');
  if (st.autoLeft > 0) { await wait(450); if (st.autoLeft > 0) playRound(false); }
}

/* ---------------- controls ---------------- */
function spinPressed() {
  if (st.busy) { if (st.autoLeft > 0 && !anims.length) { st.autoLeft = 0; render(); } else quickStop(); return; }
  playRound(false);
}
$('spin').onclick = spinPressed;
$('reels').onclick = () => { if (st.busy) quickStop(); };
$('betUp').onclick = () => { st.betIdx = Math.min(BETS.length - 1, st.betIdx + 1); render(); };
$('betDn').onclick = () => { st.betIdx = Math.max(0, st.betIdx - 1); render(); };
$('max').onclick = () => { st.betIdx = BETS.length - 1; render(); };
$('auto').onclick = () => {
  if (st.autoLeft > 0) { st.autoLeft = 0; render(); return; }
  const cur = AUTO_STEPS.indexOf(st.autoLeft), next = AUTO_STEPS[(cur + 1) % AUTO_STEPS.length];
  if (!st.busy && next > 0) { st.autoLeft = next; render(); playRound(false); }
  else { st.autoLeft = next; render(); }
};
document.addEventListener('keydown', (e) => {
  if (e.code === 'Space' && !e.repeat && !document.querySelector('dialog[open]')) { e.preventDefault(); if ($('overlay').classList.contains('show')) $('overlay').click(); else spinPressed(); }
});

$('buy').onclick = () => { const c = E.BUY_COST * bet(); $('buyCost').textContent = fmt(c); $('buyX').textContent = E.BUY_COST; $('buyGo').disabled = st.bal < c; $('buyDlg').showModal(); };
$('buyGo').onclick = () => { $('buyDlg').close(); playRound(true); };

$('btnPay').onclick = () => {
  const b = bet(); let h = '<tr><th>SYMBOL</th><th>3 REELS</th><th>4 REELS</th><th>5 REELS</th></tr>';
  Object.keys(E.PAY).forEach((s) => { const p = E.PAY[s]; h += `<tr><td>${tileHTML({ s, m: 1 }, 1)}</td>${[3, 4, 5].map((n) => '<td>' + fmt(p[n] * b / E.BET_DIV) + '</td>').join('')}</tr>`; });
  h += `<tr><td>${tileHTML({ s: 'COIN', m: 1 }, 1)}</td>${[3, 4, 5].map((n) => '<td>' + fmt(E.COIN_PAY[n] * b) + '<br><small>' + E.FREE_SPINS[n] + ' spins</small></td>').join('')}</tr>`;
  h += `<tr><td>${tileHTML({ s: 'WILD', m: 1 }, 1)}</td><td colspan="3" style="text-align:left;font-size:13px">Reels 2–4. Substitutes for all but scatter. Free spins: ×2/×3/×5, multiplied together.</td></tr>`;
  $('payTbl').innerHTML = h;
  $('payNote').textContent = `Credits per way at bet ${fmt(b)}; multiply by ways and wild multipliers. Max win per round ${E.MAX_WIN}× bet (${fmt(E.MAX_WIN * b)}). Simulated RTP ≈ 94.6% over 30M rounds (see sim.js).`;
  $('payDlg').showModal();
};

function bindToggle(id, key, onChange) {
  const b = $(id), paint = () => { b.textContent = st[key] ? 'on' : 'off'; b.classList.toggle('on', !!st[key]); };
  b.onclick = () => { st[key] = !st[key]; paint(); store.set(key, st[key]); onChange && onChange(); }; paint();
}
bindToggle('tSound', 'sound'); bindToggle('tTurbo', 'turbo'); bindToggle('tStopF', 'stopF'); bindToggle('tStopB', 'stopB');
bindToggle('tMusic', 'music', () => { audio(); setMusic(st.music); });
$('btnSet').onclick = () => $('setDlg').showModal();
$('bReset').onclick = () => { if (st.busy) return; st.bal = START_BAL; render(); msg('Balance reset to ' + fmt(START_BAL)); $('setDlg').close(); };

function showStats() {
  const s = st.stats, rtp = s.wagered ? (s.won / s.wagered * 100).toFixed(1) + '%' : '—';
  const cell = (k, v) => `<div class="box"><b>${k}</b><span>${v}</span></div>`;
  $('statGrid').innerHTML = cell('SPINS', fmt(s.spins)) + cell('SESSION RTP', rtp) + cell('WAGERED', fmt(s.wagered)) + cell('WON', fmt(s.won)) + cell('BIGGEST WIN', fmt(s.biggest)) + cell('FEATURES', s.features);
  $('hist').innerHTML = s.hist.map((h) => `<span>${h.buy ? 'BUY ' : ''}${fmt(h.bet)}</span><span>${h.win ? '<i>+' + fmt(h.win) + '</i>' : '<u>0</u>'}</span><span>${h.x.toFixed(1)}×</span>`).join('') || '<span>No rounds yet</span>';
  if (!$('statDlg').open) $('statDlg').showModal();
}
$('stats').onclick = showStats;
$('bClearStats').onclick = () => { st.stats = { spins: 0, wagered: 0, won: 0, biggest: 0, features: 0, hist: [] }; saveAll(); showStats(); };

fxResize(); render();
})();
