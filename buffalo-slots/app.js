(function () {
'use strict';
const E = window.Engine, SY = window.SYMBOLS, NAMES = window.SYMBOL_NAMES;
const $ = (id) => document.getElementById(id);
const BETS = [40, 80, 200, 400, 1000, 2000, 5000, 10000, 25000, 50000, 100000, 250000];
const START_BAL = 1000000;
const TIER = { big: 20, mega: 50, epic: 200 };          // x bet
const fmt = (n) => Math.round(n).toLocaleString('en-GB');

/* ---------------- storage / state ---------------- */
const store = {
  get(k, d) { try { const v = localStorage.getItem('th_' + k); return v == null ? d : JSON.parse(v); } catch (e) { return d; } },
  set(k, v) { try { localStorage.setItem('th_' + k, JSON.stringify(v)); } catch (e) { /* private mode */ } }
};
const freshLife = () => ({ strikes: 0, jackpots: 0, features: 0, gambleWon: 0, gambleLost: 0, hist: [], top: [], herds: {} });
// v3 economy: balance and stats restart at 1,000,000
if (store.get('ver', 1) < 3) { store.set('bal', START_BAL); store.set('bet', 1); store.set('stats', { spins: 0, wagered: 0, won: 0, biggest: 0, features: 0, hist: [] }); store.set('life', freshLife()); store.set('ver', 3); }
const st = {
  bal: store.get('bal', START_BAL), betIdx: store.get('bet', 1),
  busy: false, quick: false, autoLeft: 0, free: false, fsLeft: 0, fsWin: 0, practice: false, forceJackpot: null,
  ante: false, mode: store.get('mode', 'classic'), featMode: 'classic',
  sound: store.get('sound', true), music: false, turbo: store.get('turbo', false),
  stopF: store.get('stopF', true), stopB: store.get('stopB', true), gamble: store.get('gamble', true),
  lang: store.get('lang', 'en'), lossPct: store.get('lossPct', 0), winPct: store.get('winPct', 0),
  stats: store.get('stats', { spins: 0, wagered: 0, won: 0, biggest: 0, features: 0, hist: [] }),
  life: Object.assign(freshLife(), store.get('life', {})), ach: store.get('ach', {}),
  t0: Date.now(), startBal: 0, autoBase: 0
};
st.startBal = st.bal;
if (!(st.bal > 0)) st.bal = START_BAL;
if (!BETS[st.betIdx]) st.betIdx = 1;
if (!E.MODES[st.mode]) st.mode = 'classic';
const bet = () => BETS[st.betIdx];
const stakeOf = () => Math.round(bet() * (st.ante ? E.ANTE.cost : 1));
const AUTO_STEPS = [0, 10, 25, 50, 100, Infinity];
const LOSS_STEPS = [0, 10, 25, 50], WIN_STEPS = [0, 25, 50, 100];

/* ---------------- i18n (English / Egyptian-friendly Arabic) ---------------- */
const AR = {
  'BALANCE': 'الرصيد', 'BET': 'الرهان', 'WIN': 'الربح', 'Spin': 'لفّ', 'Stop': 'وقف', 'Auto': 'تلقائي', 'Max bet': 'أقصى رهان',
  'Buy feature': 'اشترِ الجولة', 'Stats': 'إحصائيات', 'Thunder Bet': 'رهان الرعد', 'TAP TO CONTINUE': 'المس للمتابعة',
  'Good luck…': 'بالتوفيق…', 'No win — spin again': 'مفيش ربح — لفّ تاني', 'No win': 'مفيش ربح', 'Big win': 'فوز كبير', 'Mega win': 'فوز ضخم', 'Epic win': 'فوز أسطوري',
  'Free spins win': 'ربح اللفات المجانية', 'free spins': 'لفات مجانية', 'Gamble': 'ضاعف', 'Red': 'أحمر', 'Black': 'أسود', 'Collect': 'استلم',
  'Lightning Jackpot': 'جاكبوت البرق', 'Thunderstrike': 'ضربة الرعد', 'Choose your herd': 'اختار قطيعك', 'Press SPIN or hit Space': 'اضغط لفّ أو المسطرة',
  'Practice': 'تجربة', 'Achievement unlocked': 'إنجاز جديد', 'SPINS LEFT': 'لفات متبقية', 'Out of credits — reset the balance in Settings.': 'الرصيد خلص — صفّر الرصيد من الإعدادات.'
};
const t = (k) => (st.lang === 'ar' && AR[k]) || k;
function applyLang() {
  document.documentElement.lang = st.lang;
  document.querySelectorAll('[data-i18n]').forEach((el) => { el.textContent = t(el.dataset.i18n); });
}

/* RNG: crypto-grade in the browser; tests / practice tools can queue forced grids */
const rng = () => { const a = new Uint32Array(1); crypto.getRandomValues(a); return a[0] / 4294967296; };
const forced = [];
window.ThunderHerd = { st, force: (g) => forced.push(g), E, parts: () => parts };
function nextGrid(free) { return forced.length ? forced.shift() : E.spinGrid(free, rng, { ante: !free && st.ante, mode: st.featMode }); }

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
  const t0 = a.currentTime + (delay || 0), o = a.createOscillator(), g = a.createGain();
  o.type = type || 'sine'; o.frequency.setValueAtTime(f, t0);
  if (slideTo) o.frequency.exponentialRampToValueAtTime(slideTo, t0 + d);
  g.gain.setValueAtTime(vol || 0.06, t0); g.gain.exponentialRampToValueAtTime(0.0001, t0 + d);
  o.connect(g); g.connect(master); o.start(t0); o.stop(t0 + d + 0.02);
}
function noise(d, type, f0, f1, vol, q) {
  const a = audio(); if (!a) return;
  const t0 = a.currentTime, s = a.createBufferSource(), f = a.createBiquadFilter(), g = a.createGain();
  s.buffer = noiseBuf; s.loop = true; f.type = type; f.Q.value = q || 0.8;
  f.frequency.setValueAtTime(f0, t0); f.frequency.exponentialRampToValueAtTime(f1, t0 + d);
  g.gain.setValueAtTime(0.0001, t0); g.gain.exponentialRampToValueAtTime(vol, t0 + Math.min(0.1, d / 3)); g.gain.exponentialRampToValueAtTime(0.0001, t0 + d);
  s.connect(f); f.connect(g); g.connect(master); s.start(t0); s.stop(t0 + d + 0.05);
}
const whoosh = (d) => noise(d, 'bandpass', 300, 1800, 0.1);
const sfx = {
  stop: () => { tone(150, 0.14, 'sine', 0.16, 0, 60); tone(900, 0.04, 'square', 0.02); },
  coin: () => { tone(988, 0.1, 'triangle', 0.09); tone(1568, 0.28, 'triangle', 0.09, 0.08); },
  win: (n) => { const sc = [523, 587, 659, 784, 880, 1047, 1175, 1319]; for (let i = 0; i < Math.min(3 + n, 8); i++) tone(sc[i], 0.18, 'triangle', 0.07, i * 0.07); },
  tick: () => tone(1400 + Math.random() * 300, 0.03, 'square', 0.02),
  fanfare: (lvl) => { const sc = [392, 523, 659, 784, 1047, 1319, 1568]; for (let i = 0; i < 5 + lvl * 2; i++) { tone(sc[i % 7] * (i > 6 ? 2 : 1), 0.35, 'triangle', 0.08, i * 0.11); tone(sc[i % 7] / 2, 0.35, 'sawtooth', 0.025, i * 0.11); } },
  tension: (d) => tone(200, d, 'sawtooth', 0.03, 0, 900),
  thunder: () => { noise(1.2, 'lowpass', 900, 80, 0.5, 0.5); tone(55, 0.9, 'sine', 0.3, 0, 30); noise(0.08, 'highpass', 3000, 6000, 0.25); },
  siren: () => { for (let i = 0; i < 8; i++) tone(i % 2 ? 660 : 880, 0.18, 'square', 0.04, i * 0.2); },
  flip: () => { tone(300, 0.05, 'square', 0.05); tone(500, 0.06, 'square', 0.05, 0.06); },
  ach: () => { [784, 988, 1175, 1568].forEach((f, i) => tone(f, 0.25, 'triangle', 0.07, i * 0.09)); }
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
const randSym = () => E.SYM[Math.floor(Math.random() * E.SYM.length)];
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
    }, durs[c - 1]));
    timers.push(setTimeout(() => $('anticip').classList.remove('on'), durs[c] - 30));
  });
  await Promise.all(anims.map((a, c) => a.finished.then(() => {
    cols[c].el.classList.remove('moving'); setStatic(c, grid[c]); a.cancel(); sfx.stop();
    grid[c].forEach((x, r) => { if (x.s === 'COIN') { cellEl(c, r).classList.add('bump'); sfx.coin(); } });
  })));
  timers.forEach(clearTimeout); $('anticip').classList.remove('on'); anims = [];
}
function quickStop() { if (st.busy && anims.length && !st.quick) { st.quick = true; anims.forEach((a) => { a.playbackRate = 6; }); } }

/* Thunderstrike: reels land showing the original symbols, then lightning swaps cells for wilds */
const viewOf = (grid) => {
  const v = grid.map((col) => col.map((x) => ({ s: x.s, m: x.m })));
  (grid.strike || []).forEach((k) => { v[k.c][k.r] = { s: k.from, m: 1 }; });
  return v;
};
async function strikeFX(grid) {
  const s = grid.strike; if (!s || !s.length) return;
  msg('⚡ ' + t('Thunderstrike') + ' — ' + s.length + ' wild' + (s.length > 1 ? 's' : '') + '!');
  $('flash').classList.add('on'); sfx.thunder(); setTimeout(() => $('flash').classList.remove('on'), 520);
  await wait(260);
  s.forEach(({ c, r }) => {
    const tmp = document.createElement('div'); tmp.innerHTML = tileHTML(grid[c][r], 4);
    const n = tmp.firstChild; n.classList.add('zap'); cellEl(c, r).replaceWith(n);
  });
  new Set(s.map((k) => k.c)).forEach((c) => { cols[c].cur = grid[c]; });
  await wait(950);
}

/* ---------------- win presentation ---------------- */
function mark(cells) {
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
function msg(m) { $('msg').textContent = m; }
function saveAll() { store.set('bal', st.bal); store.set('bet', st.betIdx); store.set('stats', st.stats); store.set('life', st.life); store.set('ach', st.ach); store.set('mode', st.mode); }
const multsText = (mode) => E.MODES[mode].mults.map((m) => '×' + m.v).join(' ');
const multsShort = (mode) => '×' + E.MODES[mode].mults.map((m) => m.v).join('/');
function sessionText() {
  const net = st.bal - st.startBal, mins = Math.floor((Date.now() - st.t0) / 60000);
  return (net >= 0 ? '+' : '−') + fmt(Math.abs(net)) + ' · ' + mins + ' min';
}
function render() {
  $('bal').textContent = fmt(st.bal); $('betv').textContent = fmt(bet());
  $('stake').textContent = st.ante ? 'stake ' + fmt(stakeOf()) : '';
  $('net').textContent = sessionText();
  $('net').className = st.bal - st.startBal >= 0 ? 'up' : 'down';
  document.body.classList.toggle('free', st.free);
  $('fsLeft').textContent = t('SPINS LEFT') + ' ' + st.fsLeft; $('fsWin').textContent = fmt(st.fsWin);
  $('multChip').textContent = 'WILD ' + multsText(st.featMode);
  $('betDn').disabled = $('betUp').disabled = $('max').disabled = $('buy').disabled = $('ante').disabled = st.busy;
  const auto = st.autoLeft > 0;
  $('spin').textContent = st.busy ? (auto ? t('Stop') : '···') : t('Spin');
  $('spin').disabled = st.busy && !auto && !anims.length;
  $('auto').textContent = t('Auto') + ' \u200E▸ ' + (auto ? (st.autoLeft === Infinity ? '∞' : st.autoLeft) : 'off');
  $('auto').classList.toggle('on', auto);
  $('ante').classList.toggle('on', st.ante);
  $('ante').textContent = '⚡ ' + t('Thunder Bet') + ' \u200E' + (st.ante ? '+25% · on' : '+25%');
  $('buy').textContent = t('Buy feature') + ' \u200E· ' + fmt(E.BUY_COST * bet());
  saveAll();
}
function roll(el, from, to, ms, tick) {
  return new Promise((res) => {
    const t0 = performance.now(); let last = 0;
    const stepf = (tt) => {
      const k = Math.min(1, (tt - t0) / ms), v = from + (to - from) * (1 - Math.pow(1 - k, 2.2));
      el.textContent = fmt(v);
      if (tick && tt - last > 70) { sfx.tick(); last = tt; }
      if (k < 1 && !roll.skip) requestAnimationFrame(stepf); else { el.textContent = fmt(to); res(); }
    };
    roll.skip = false; requestAnimationFrame(stepf);
  });
}
function toast(text, cls) {
  const d = document.createElement('div'); d.className = 'toast ' + (cls || ''); d.textContent = text;
  $('toasts').appendChild(d); setTimeout(() => d.classList.add('out'), 3600); setTimeout(() => d.remove(), 4100);
}

/* ---------------- overlay (win screens, choices) ---------------- */
let ovResolve = null, ovToken = 0, ovLocked = false;
function overlay(o) {
  return new Promise((res) => {
    const tok = ++ovToken; ovLocked = !!o.lock;
    $('ovTitle').textContent = o.title || ''; $('ovTitle').classList.toggle('sm', (o.title || '').length > 13); $('ovNum').textContent = o.num != null ? o.num : ''; $('ovSub').textContent = o.sub || '';
    $('ovBtns').innerHTML = ''; $('ovTap').style.display = o.lock ? 'none' : '';
    $('overlay').classList.add('show'); ovResolve = () => { $('overlay').classList.remove('show'); ovResolve = null; ovLocked = false; res(); };
    if (o.ms) setTimeout(() => { if (tok === ovToken && ovResolve) ovResolve(); }, st.turbo ? o.ms * 0.5 : o.ms);
  });
}
function closeOverlay() { if (ovResolve) ovResolve(); }
$('overlay').addEventListener('click', () => {
  if (ovLocked) return;
  if (roll.skip === false && $('ovNum').dataset.rolling === '1') roll.skip = true; else if (ovResolve) ovResolve();
});
/** Show a choice screen; resolves with the chosen key. The overlay stays open for the caller to reuse or close. */
function choose(o) {
  overlay({ title: o.title, num: o.num, sub: o.sub, lock: true });
  const box = $('ovBtns');
  box.innerHTML = o.buttons.map((b) => `<button class="ob ${b.cls || ''}" data-k="${b.key}">${b.html}</button>`).join('');
  return new Promise((res) => { box.querySelectorAll('button').forEach((b) => { b.onclick = (e) => { e.stopPropagation(); res(b.dataset.k); }; }); });
}

async function celebrate(amount, label) {
  const x = amount / bet();
  const lvl = x >= TIER.epic ? 3 : x >= TIER.mega ? 2 : x >= TIER.big ? 1 : 0;
  const title = label || t(['', 'Big win', 'Mega win', 'Epic win'][lvl]);
  const dur = [1800, 2600, 4200, 6500][lvl];
  sfx.fanfare(lvl);
  const p = overlay({ title, num: 0, sub: fmt(x) + '× bet' });
  $('ovNum').dataset.rolling = '1';
  const rain = setInterval(() => spawnCoins(4 + lvl * 4), 120);
  spawnCoins(20, { x: $('cab').clientWidth / 2, y: $('cab').clientHeight * 0.6, up: true, spread: 10 });
  await roll($('ovNum'), 0, amount, st.turbo ? dur * 0.5 : dur, true);
  clearInterval(rain); $('ovNum').dataset.rolling = '0';
  await Promise.race([p, new Promise((r) => setTimeout(r, st.turbo ? 700 : 1800))]);
  closeOverlay();
}

/* ---------------- achievements ---------------- */
const ACH = [
  { id: 'first', n: 'First Stampede', d: 'Trigger free spins', f: (c) => c.featured },
  { id: 'big', n: 'Thunder Hands', d: 'Win 20× your bet', f: (c) => c.x >= 20 },
  { id: 'mega', n: 'Herd Leader', d: 'Win 50× your bet', f: (c) => c.x >= 50 },
  { id: 'epic', n: 'Spirit of the Plains', d: 'Win 200× your bet', f: (c) => c.x >= 200 },
  { id: 'jp', n: 'Struck Gold', d: 'Hit any Lightning Jackpot', f: (c) => !!c.jp },
  { id: 'grand', n: 'Grand Chief', d: 'Hit the GRAND jackpot', f: (c) => c.jp && c.jp.id === 'GRAND' },
  { id: 'strike3', n: 'Triple Bolt', d: 'Thunderstrike adds 3 wilds', f: (c) => c.strikeN >= 3 },
  { id: 'mult30', n: 'Wild Math', d: 'A single win with wild ×30 or more', f: (c) => c.maxMult >= 30 },
  { id: 'herds', n: 'Three Trails', d: 'Finish free spins in all three herds', f: () => Object.keys(st.life.herds).length >= 3 },
  { id: 'gamble3', n: 'Cold Nerves', d: 'Win 3 gambles in a row', f: (c) => c.gambleStreak >= 3 },
  { id: 'anteWin', n: 'Charged Up', d: 'Win a feature on Thunder Bet', f: (c) => c.featured && c.ante },
  { id: 'buy', n: 'Skipped the Queue', d: 'Buy a feature', f: (c) => c.buy },
  { id: 'hundred', n: 'Centurion', d: 'Play 100 spins', f: () => st.stats.spins >= 100 },
  { id: 'thousand', n: 'Long Haul', d: 'Play 1,000 spins', f: () => st.stats.spins >= 1000 },
  { id: 'roller', n: 'High Roller', d: 'Bet 100,000 or more', f: (c) => c.bet >= 100000 },
  { id: 'double', n: 'Double Up', d: 'Reach 2,000,000 credits', f: () => st.bal >= 2000000 }
];
function checkAch(ctx) {
  ACH.forEach((a) => {
    if (st.ach[a.id]) return;
    let ok = false; try { ok = a.f(ctx); } catch (e) { ok = false; }
    if (ok) { st.ach[a.id] = Date.now(); toast('🏆 ' + t('Achievement unlocked') + ': ' + a.n, 'ach'); sfx.ach(); }
  });
}

/* ---------------- features: jackpot, herd pick, gamble ---------------- */
async function jackpotShow(jp, amount) {
  const tiers = E.JACKPOT.tiers, idx = tiers.findIndex((x) => x.id === jp.id);
  overlay({ title: t('Lightning Jackpot'), num: '', sub: '', lock: true });
  $('ovBtns').innerHTML = tiers.map((x) => `<div class="plate" data-id="${x.id}"><b>${x.id}</b><span>${x.x}×</span></div>`).join('');
  const plates = $('ovBtns').querySelectorAll('.plate');
  sfx.siren(); $('flash').classList.add('on'); setTimeout(() => $('flash').classList.remove('on'), 500);
  let n = 14 + ((idx - 14 % 4 + 4) % 4), i = 0;
  for (let k = 0; k <= n; k++) { plates.forEach((p) => p.classList.remove('lit')); plates[i % 4].classList.add('lit'); sfx.tick(); await wait(70 + k * 16); i++; }
  plates[idx].classList.add('hit'); sfx.fanfare(3);
  $('ovNum').dataset.rolling = '1';
  const rain = setInterval(() => spawnCoins(10), 100);
  await roll($('ovNum'), 0, amount, st.turbo ? 1200 : 2600, true);
  $('ovNum').dataset.rolling = '0'; $('ovSub').textContent = jp.id + ' · ' + jp.x + '× bet';
  await wait(1700); clearInterval(rain); closeOverlay();
}
async function pickHerd(coins) {
  if (st.autoLeft > 0) return st.mode;
  const btn = (k) => {
    const m = E.MODES[k], sp = E.featureSpins(coins, k), flavour = { classic: 'Balanced', marathon: 'More spins, calmer wilds', blitz: 'Few spins, huge wilds' }[k];
    return { key: k, cls: 'herd' + (k === st.mode ? ' cur' : ''), html: `<b>${m.label}</b><span>${sp} spins</span><span>wilds ${multsShort(k)}</span><i>${flavour}</i>` };
  };
  const k = await choose({ title: t('Choose your herd'), sub: coins + ' scatters', buttons: ['classic', 'marathon', 'blitz'].map(btn) });
  st.mode = k; closeOverlay(); return k;
}
async function gambleLoop(amount, cap) {
  let a = amount, streak = 0;
  while (streak < 3 && a * 2 <= cap) {
    const pick = await choose({ title: t('Gamble'), num: fmt(a), sub: 'Double or nothing · ' + (3 - streak) + ' left',
      buttons: [{ key: 'R', cls: 'red', html: '♥ ♦ ' + t('Red') }, { key: 'B', cls: 'blk', html: '♣ ♠ ' + t('Black') }, { key: 'C', cls: 'col', html: t('Collect') + ' ' + fmt(a) }] });
    if (pick === 'C') break;
    const win = rng() < 0.5, side = win ? pick : (pick === 'R' ? 'B' : 'R');
    const suit = side === 'R' ? ['♥', '♦'][Math.floor(rng() * 2)] : ['♣', '♠'][Math.floor(rng() * 2)];
    sfx.flip(); $('ovBtns').innerHTML = `<div class="pcard ${side === 'R' ? 'red' : 'blk'}">${suit}</div>`;
    await wait(1100);
    if (win) { a *= 2; streak++; st.life.gambleWon++; sfx.win(4); $('ovNum').textContent = fmt(a); $('ovSub').textContent = 'You win!'; await wait(700); }
    else { a = 0; st.life.gambleLost++; sfx.stop(); $('ovNum').textContent = '0'; $('ovSub').textContent = 'Lost'; await wait(900); break; }
  }
  closeOverlay();
  return { amount: a, streak };
}

/* ---------------- game flow ---------------- */
function recordRound(wag, win, buy, kind, x) {
  const s = st.stats; s.spins++; s.wagered += wag; s.won += win; s.biggest = Math.max(s.biggest, win);
  s.hist.unshift({ bet: bet(), win, x: win / bet(), buy: !!buy }); s.hist = s.hist.slice(0, 18);
  if (win > 0) { st.life.top.push({ win, x, bet: bet(), kind, t: Date.now() }); st.life.top.sort((p, q) => q.win - p.win); st.life.top = st.life.top.slice(0, 5); }
}
async function paySpin(free) {
  const grid = nextGrid(free);
  await spinReels(viewOf(grid));
  if (!free && grid.strike) await strikeFX(grid);
  const res = E.evaluate(grid), credits = Math.round(res.total * bet());
  return { res, credits, grid };
}
function describe(r, credits, free) {
  const top = r.wins.slice().sort((a, b) => b.pay - a.pay)[0];
  if (!top && r.coinPay) return `SCATTER ×${r.coins}  =  ${fmt(credits)}`;
  const mx = Math.max(1, ...r.wins.map((w) => w.mult));
  return `WIN ${fmt(credits)}  ·  ${NAMES[top.sym]} ×${top.reels}${r.wins.length > 1 ? '  +' + (r.wins.length - 1) + ' more' : ''}${free && mx > 1 ? '  ·  wild ×' + mx : ''}`;
}

async function runFeature(startSpins, mode, roundSoFar, cap) {
  st.featMode = mode; st.free = true; st.fsLeft = startSpins; st.fsWin = 0; setMusic(st.music); render();
  sfx.fanfare(1);
  await overlay({ title: startSpins + ' ' + t('free spins'), sub: E.MODES[mode].label + ' — wilds ' + multsText(mode) + ', multipliers stack', ms: 2600 });
  let total = 0, played = 0, maxMult = 1;
  while (st.fsLeft > 0 && roundSoFar + total < cap) {
    st.fsLeft--; played++; st.quick = false; render();
    const f = await paySpin(true);
    total += f.credits; st.fsWin += f.credits;
    f.res.wins.forEach((w) => { maxMult = Math.max(maxMult, w.mult); });
    $('win').textContent = fmt(Math.min(roundSoFar + total, cap));
    msg(f.credits ? describe(f.res, f.credits, true) : t('No win'));
    render();
    await showWins(f.res);
    if (f.res.fs > 0) { const add = E.featureSpins(f.res.coins, mode); st.fsLeft += add; render(); sfx.fanfare(0); await overlay({ title: '+' + add + ' ' + t('free spins'), ms: 1500 }); }
  }
  st.free = false; st.featMode = mode; setMusic(st.music);
  return { total: Math.min(total, cap - roundSoFar), played, maxMult };
}

async function playRound(buy) {
  if (st.busy) return;
  const cost = buy ? E.BUY_COST * bet() : stakeOf();
  if (st.bal < cost) { msg('Not enough credits — lower your bet or reset in settings.'); st.autoLeft = 0; render(); return; }
  st.busy = true; st.quick = false; st.bal -= cost; st.fsLeft = 0; st.fsWin = 0; st.featMode = st.mode;
  if (!st.autoBase || st.autoLeft === 0) st.autoBase = st.bal + cost;
  $('win').textContent = '0'; msg(buy ? 'Feature purchased!' : t('Good luck…')); render();
  audio();
  const cap = E.MAX_WIN * bet(), practice = st.practice;
  let round = 0, featured = false, jp = null, strikeN = 0, maxMult = 1, mode = st.mode, kind = 'Base game';

  if (buy) {
    round += Math.round(E.COIN_PAY[3] * bet()); featured = true; kind = 'Bought feature';
    $('win').textContent = fmt(round);
    mode = await pickHerd(3);
    const f = await runFeature(E.featureSpins(3, mode), mode, round, cap); round += f.total; maxMult = f.maxMult;
  } else {
    const r = await paySpin(false);
    strikeN = (r.grid.strike || []).length; if (strikeN && !practice) st.life.strikes++;
    round += r.credits; $('win').textContent = fmt(Math.min(round, cap));
    msg(r.credits ? describe(r.res, r.credits, false) : t('No win — spin again'));
    await showWins(r.res);
    jp = st.forceJackpot ? { id: st.forceJackpot, x: E.JACKPOT.tiers.find((x) => x.id === st.forceJackpot).x } : E.rollJackpot(rng);
    st.forceJackpot = null;
    if (jp) {
      const amt = Math.round(jp.x * bet()); round += amt; kind = 'Jackpot ' + jp.id; if (!practice) st.life.jackpots++;
      await jackpotShow(jp, amt); $('win').textContent = fmt(Math.min(round, cap));
    }
    if (r.res.fs > 0) {
      featured = true; kind = jp ? kind + ' + feature' : 'Free spins';
      mode = await pickHerd(r.res.coins);
      const f = await runFeature(E.featureSpins(r.res.coins, mode), mode, round, cap); round += f.total; maxMult = f.maxMult;
    }
  }
  round = Math.min(round, cap);
  const x = round / bet();
  $('win').textContent = fmt(round);
  if (featured) msg(`Feature paid ${fmt(round)} credits (${x.toFixed(1)}× bet)`);
  if (featured && x >= TIER.big) await celebrate(round);
  else if (featured) await celebrate(round, t('Free spins win'));
  else if (x >= TIER.big) await celebrate(round);
  else if (round === 0) msg(t('No win — spin again'));

  // optional gamble (manual play only)
  let gambleStreak = 0;
  if (st.gamble && st.autoLeft === 0 && round >= bet() && round * 2 <= cap) {
    const g = await gambleLoop(round, cap); gambleStreak = g.streak;
    if (g.amount !== round) msg(g.amount ? `Gamble paid ${fmt(g.amount)}` : 'Gamble lost — better luck next time');
    round = g.amount;
  }

  st.bal += round; st.quick = false;
  st.life.hist.push(st.bal); if (st.life.hist.length > 400) st.life.hist.shift();
  if (!practice) {
    if (featured) { st.stats.features++; st.life.features++; st.life.herds[mode] = (st.life.herds[mode] || 0) + 1; }
    recordRound(cost, round, buy, kind, x);
    checkAch({ x: round / bet(), featured, jp, strikeN, maxMult, gambleStreak, ante: st.ante && !buy, buy, bet: bet() });
  }
  $('win').textContent = fmt(round);
  st.practice = false; st.busy = false; st.fsLeft = 0; render();

  // autoplay bookkeeping + loss / win limits
  if (st.autoLeft > 0) {
    if (st.autoLeft !== Infinity) st.autoLeft--;
    const stop = (featured && st.stopF) || (x >= TIER.big && st.stopB) || st.bal < stakeOf()
      || (st.lossPct && st.bal <= st.autoBase * (1 - st.lossPct / 100)) || (st.winPct && st.bal >= st.autoBase * (1 + st.winPct / 100));
    if (stop) { st.autoLeft = 0; if (st.lossPct || st.winPct) toast('Autoplay stopped · ' + sessionText()); }
  }
  render();
  if (st.bal <= 0) msg(t('Out of credits — reset the balance in Settings.'));
  if (st.autoLeft > 0) { await wait(450); if (st.autoLeft > 0) playRound(false); }
}

/* ---------------- balance chart (single series) ---------------- */
let sparkHover = -1;
function drawSpark() {
  const cv = $('spark'); if (!cv.clientWidth) return;
  const W = cv.clientWidth, H = cv.clientHeight, d = window.devicePixelRatio || 1; cv.width = W * d; cv.height = H * d;
  const c = cv.getContext('2d'); c.setTransform(d, 0, 0, d, 0, 0); c.clearRect(0, 0, W, H);
  const data = st.life.hist.length ? st.life.hist : [st.bal];
  const lo = Math.min(START_BAL, ...data), hi = Math.max(START_BAL, ...data), span = (hi - lo) || 1;
  const L = 46, R = 12, T = 12, B = 14, pw = W - L - R, ph = H - T - B;
  const X = (i) => L + (data.length === 1 ? pw / 2 : (i / (data.length - 1)) * pw), Y = (v) => T + ph - ((v - lo) / span) * ph;
  const ink = getComputedStyle(document.body).color;
  c.font = '10px system-ui,sans-serif'; c.fillStyle = ink; c.globalAlpha = 0.55; c.textAlign = 'right';
  [lo, (lo + hi) / 2, hi].forEach((v) => { c.fillText(shortNum(v), L - 6, Y(v) + 3); });
  c.globalAlpha = 0.12; c.strokeStyle = ink; c.lineWidth = 1;
  [lo, (lo + hi) / 2, hi].forEach((v) => { c.beginPath(); c.moveTo(L, Y(v)); c.lineTo(W - R, Y(v)); c.stroke(); });
  c.globalAlpha = 0.5; c.setLineDash([4, 4]); c.beginPath(); c.moveTo(L, Y(START_BAL)); c.lineTo(W - R, Y(START_BAL)); c.stroke(); c.setLineDash([]);
  c.globalAlpha = 0.6; c.textAlign = 'left'; c.fillText('start', L + 4, Y(START_BAL) - 4); c.globalAlpha = 1;
  const g = c.createLinearGradient(0, T, 0, T + ph); g.addColorStop(0, 'rgba(255,200,61,.22)'); g.addColorStop(1, 'rgba(255,200,61,0)');
  c.beginPath(); data.forEach((v, i) => { i ? c.lineTo(X(i), Y(v)) : c.moveTo(X(i), Y(v)); }); c.lineTo(X(data.length - 1), T + ph); c.lineTo(X(0), T + ph); c.closePath(); c.fillStyle = g; c.fill();
  c.beginPath(); data.forEach((v, i) => { i ? c.lineTo(X(i), Y(v)) : c.moveTo(X(i), Y(v)); });
  c.strokeStyle = '#ffc83d'; c.lineWidth = 2; c.lineJoin = 'round'; c.stroke();
  const e = data.length - 1; c.beginPath(); c.arc(X(e), Y(data[e]), 4.5, 0, 6.3); c.fillStyle = '#ffc83d'; c.fill(); c.lineWidth = 2; c.strokeStyle = getComputedStyle(document.body).backgroundColor || '#120803'; c.stroke();
  if (sparkHover >= 0 && sparkHover < data.length) {
    const hx = X(sparkHover), hy = Y(data[sparkHover]);
    c.globalAlpha = 0.4; c.strokeStyle = ink; c.beginPath(); c.moveTo(hx, T); c.lineTo(hx, T + ph); c.stroke(); c.globalAlpha = 1;
    c.beginPath(); c.arc(hx, hy, 4, 0, 6.3); c.fillStyle = '#ffc83d'; c.fill();
  }
  $('spTip').textContent = sparkHover >= 0 && data[sparkHover] != null ? `Round ${sparkHover + 1}: ${fmt(data[sparkHover])} credits` : `${data.length} round${data.length > 1 ? 's' : ''} · now ${fmt(data[data.length - 1])} · dashed line = starting balance`;
}
function shortNum(v) { return v >= 1e6 ? (v / 1e6).toFixed(2).replace(/\.?0+$/, '') + 'M' : v >= 1e3 ? Math.round(v / 1e3) + 'k' : Math.round(v) + ''; }
$('spark').addEventListener('pointermove', (e) => {
  const r = e.currentTarget.getBoundingClientRect(), n = st.life.hist.length; if (n < 2) return;
  sparkHover = Math.max(0, Math.min(n - 1, Math.round(((e.clientX - r.left - 46) / (r.width - 58)) * (n - 1)))); drawSpark();
});
$('spark').addEventListener('pointerleave', () => { sparkHover = -1; drawSpark(); });

/* ---------------- controls ---------------- */
function spinPressed() {
  if (st.busy) { if (st.autoLeft > 0 && !anims.length) { st.autoLeft = 0; render(); } else quickStop(); return; }
  playRound(false);
}
$('spin').onclick = spinPressed;
$('reels').onclick = () => { if (st.busy) quickStop(); };
const setBet = (i) => { if (st.busy) return; st.betIdx = Math.max(0, Math.min(BETS.length - 1, i)); render(); };
$('betUp').onclick = () => setBet(st.betIdx + 1);
$('betDn').onclick = () => setBet(st.betIdx - 1);
$('max').onclick = () => setBet(BETS.length - 1);
$('ante').onclick = () => { if (st.busy) return; st.ante = !st.ante; render(); };
$('auto').onclick = () => {
  if (st.autoLeft > 0) { st.autoLeft = 0; render(); return; }
  const cur = AUTO_STEPS.indexOf(st.autoLeft), next = AUTO_STEPS[(cur + 1) % AUTO_STEPS.length];
  st.autoLeft = next; st.autoBase = st.bal; render(); if (!st.busy && next > 0) playRound(false);
};
const dialogOpen = () => document.querySelector('dialog[open]');
document.addEventListener('keydown', (e) => {
  if (e.repeat || dialogOpen() || e.ctrlKey || e.metaKey) return;
  if (e.code === 'Space') { e.preventDefault(); if ($('overlay').classList.contains('show')) { if (!ovLocked) $('overlay').click(); } else spinPressed(); return; }
  if ($('overlay').classList.contains('show')) return;
  const k = e.key.toLowerCase();
  if (k === 'arrowup') setBet(st.betIdx + 1); else if (k === 'arrowdown') setBet(st.betIdx - 1);
  else if (k === 'm') setBet(BETS.length - 1); else if (k === 'q' && !st.busy) $('ante').click();
  else if (k === 'b' && !st.busy) $('buy').click(); else if (k === 'a') $('auto').click();
  else if (k === 't') $('tTurbo').click(); else if (k === 's') $('stats').click(); else if (k === 'i') $('btnPay').click();
});

$('buy').onclick = () => { const c = E.BUY_COST * bet(); $('buyCost').textContent = fmt(c); $('buyX').textContent = E.BUY_COST; $('buyGo').disabled = st.bal < c; $('buyDlg').showModal(); };
$('buyGo').onclick = () => { $('buyDlg').close(); playRound(true); };

$('btnPay').onclick = () => {
  const b = bet(); let h = '<tr><th>SYMBOL</th><th>3 REELS</th><th>4 REELS</th><th>5 REELS</th></tr>';
  Object.keys(E.PAY).forEach((s) => { const p = E.PAY[s]; h += `<tr><td>${tileHTML({ s, m: 1 }, 1)}</td>${[3, 4, 5].map((n) => '<td>' + fmt(p[n] * b / E.BET_DIV) + '</td>').join('')}</tr>`; });
  h += `<tr><td>${tileHTML({ s: 'COIN', m: 1 }, 1)}</td>${[3, 4, 5].map((n) => '<td>' + fmt(E.COIN_PAY[n] * b) + '<br><small>' + E.FREE_SPINS[n] + ' spins</small></td>').join('')}</tr>`;
  h += `<tr><td>${tileHTML({ s: 'WILD', m: 1 }, 1)}</td><td colspan="3" style="text-align:left;font-size:13px">Reels 2–4. Substitutes for all but scatter. In free spins wilds carry multipliers that multiply together.</td></tr>`;
  $('payTbl').innerHTML = h;
  $('payFeat').innerHTML = `<li><b>⚡ Thunderstrike</b> — about ${(E.STRIKE.p * 100).toFixed(0)}% of base spins: lightning turns 1–${E.STRIKE.max} cells on reels 2–4 into wilds.</li>
    <li><b>Lightning Jackpot</b> — random on any paid spin, about 1 in ${fmt(1 / E.JACKPOT.p)}. ${E.JACKPOT.tiers.map((x) => x.id + ' ' + x.x + '×').join(' · ')}.</li>
    <li><b>Thunder Bet</b> — stake +25%, scatters land about 1.6× as often.</li>
    <li><b>Choose your herd</b> — ${Object.keys(E.MODES).map((k) => E.MODES[k].label + ' (' + E.featureSpins(3, k) + ' spins, wilds ' + multsText(k) + ')').join('; ')}. Similar average return, different swings.</li>
    <li><b>Gamble</b> — double or nothing on a card colour, up to 3 times (fair 50/50).</li>`;
  $('payNote').textContent = `Credits per way at bet ${fmt(b)}; multiply by ways and wild multipliers. Max win per round ${E.MAX_WIN}× bet (${fmt(E.MAX_WIN * b)}). Simulated RTP ≈ 95% (30M+ rounds, see sim.js); Buy Feature ${E.BUY_COST}× ≈ 95%.`;
  $('payDlg').showModal();
};

function bindToggle(id, key, onChange, labels) {
  const b = $(id), paint = () => { b.textContent = labels ? labels[st[key] ? 0 : 1] : (st[key] ? 'on' : 'off'); b.classList.toggle('on', !!st[key]); };
  b.onclick = () => { st[key] = !st[key]; paint(); store.set(key, st[key]); onChange && onChange(); }; paint();
}
bindToggle('tSound', 'sound'); bindToggle('tTurbo', 'turbo'); bindToggle('tStopF', 'stopF'); bindToggle('tStopB', 'stopB'); bindToggle('tGamble', 'gamble');
bindToggle('tMusic', 'music', () => { audio(); setMusic(st.music); });
$('tLang').textContent = st.lang === 'ar' ? 'عربي' : 'English';
$('tLang').onclick = () => { st.lang = st.lang === 'ar' ? 'en' : 'ar'; store.set('lang', st.lang); $('tLang').textContent = st.lang === 'ar' ? 'عربي' : 'English'; applyLang(); if (!st.busy) msg(t('Press SPIN or hit Space')); render(); };
const cycle = (id, key, steps, label) => { const b = $(id); const paint = () => { b.textContent = st[key] ? label(st[key]) : 'off'; }; b.onclick = () => { st[key] = steps[(steps.indexOf(st[key]) + 1) % steps.length]; store.set(key, st[key]); paint(); }; paint(); };
cycle('bLoss', 'lossPct', LOSS_STEPS, (v) => '−' + v + '%'); cycle('bWin', 'winPct', WIN_STEPS, (v) => '+' + v + '%');
$('btnSet').onclick = () => $('setDlg').showModal();
$('bReset').onclick = () => { if (st.busy) return; st.bal = START_BAL; st.startBal = START_BAL; st.life.hist = []; render(); msg('Balance reset to ' + fmt(START_BAL)); $('setDlg').close(); };

/* practice tools: queue a forced outcome for the next spin (not recorded in stats) */
function practiceRun(setup) {
  if (st.busy) return; $('setDlg').close(); st.practice = true; setup(); msg(t('Practice')); playRound(false);
}
const C = (s, m) => ({ s, m: m || 1 });
$('pFree').onclick = () => practiceRun(() => forced.push(Array.from({ length: 5 }, (_, c) => [C(c < 3 ? 'COIN' : 'J'), C('Q'), C('K'), C('A')])));
$('pBig').onclick = () => practiceRun(() => forced.push(Array.from({ length: 5 }, (_, c) => c < 3 ? [C('BUF'), C('BUF'), C('BUF'), C('BUF')] : [C('J'), C('Q'), C('J'), C('Q')])));
$('pJack').onclick = () => practiceRun(() => { st.forceJackpot = 'MAJOR'; });
$('pStrike').onclick = () => practiceRun(() => {
  const g = Array.from({ length: 5 }, (_, c) => [C(c % 2 ? 'EAG' : 'COU'), C('Q'), C('K'), C('A')]);
  g[0] = [C('WOL'), C('WOL'), C('J'), C('Q')]; g[1] = [C('WILD'), C('WOL'), C('J'), C('Q')]; g[2] = [C('WOL'), C('WILD'), C('Q'), C('J')]; g[3] = [C('WOL'), C('K'), C('WILD'), C('Q')];
  g.strike = [{ c: 1, r: 0, from: 'K' }, { c: 2, r: 1, from: 'EAG' }, { c: 3, r: 2, from: 'J' }]; forced.push(g);
});

function showStats() {
  const s = st.stats, rtp = s.wagered ? (s.won / s.wagered * 100).toFixed(1) + '%' : '—', net = st.bal - START_BAL;
  const cell = (k, v, cls) => `<div class="box"><b>${k}</b><span class="${cls || ''}">${v}</span></div>`;
  $('statGrid').innerHTML = cell('SPINS', fmt(s.spins)) + cell('SESSION RTP', rtp) + cell('NET VS 1M START', (net >= 0 ? '+' : '−') + fmt(Math.abs(net)), net >= 0 ? 'up' : 'down') + cell('BIGGEST WIN', fmt(s.biggest))
    + cell('FEATURES', st.life.features) + cell('THUNDERSTRIKES', st.life.strikes) + cell('JACKPOTS', st.life.jackpots) + cell('GAMBLES W/L', st.life.gambleWon + ' / ' + st.life.gambleLost);
  $('topWins').innerHTML = st.life.top.length ? st.life.top.map((w, i) => `<li><span>${i + 1}</span><b>${fmt(w.win)}</b><i>${w.x.toFixed(0)}× @ ${fmt(w.bet)} · ${w.kind}</i></li>`).join('') : '<li class="mut">Nothing yet</li>';
  $('achGrid').innerHTML = ACH.map((a) => `<div class="ach ${st.ach[a.id] ? 'got' : ''}" title="${a.d}"><b>${st.ach[a.id] ? '🏆' : '🔒'} ${a.n}</b><span>${a.d}</span></div>`).join('');
  $('achCount').textContent = Object.keys(st.ach).length + ' / ' + ACH.length;
  $('hist').innerHTML = s.hist.map((h) => `<span>${h.buy ? 'BUY ' : ''}${fmt(h.bet)}</span><span>${h.win ? '<i>+' + fmt(h.win) + '</i>' : '<u>0</u>'}</span><span>${h.x.toFixed(1)}×</span>`).join('') || '<span>No rounds yet</span>';
  if (!$('statDlg').open) $('statDlg').showModal();
  sparkHover = -1; drawSpark();
}
$('stats').onclick = showStats;
$('bClearStats').onclick = () => { st.stats = { spins: 0, wagered: 0, won: 0, biggest: 0, features: 0, hist: [] }; st.life = freshLife(); st.ach = {}; saveAll(); showStats(); };

setInterval(() => { if (!document.hidden) $('net').textContent = sessionText(); }, 20000);
setInterval(() => { toast('Reality check: ' + sessionText() + ' this session'); }, 30 * 60000);

applyLang(); fxResize(); render();
})();
