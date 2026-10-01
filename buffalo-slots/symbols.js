/* Hand-drawn SVG symbols (100x100). Gradients live in <defs> in index.html. */
(function (root) {
  'use strict';
  const eye = (x, y, c) => `<ellipse cx="${x}" cy="${y}" rx="5.5" ry="4" fill="${c}"/><circle cx="${x}" cy="${y}" r="2.2" fill="#140a04"/><circle cx="${x - 1}" cy="${y - 1.2}" r=".9" fill="#fff"/>`;
  const card = (t, g, glow) => `<svg viewBox="0 0 100 100"><text x="50" y="74" text-anchor="middle" font-family="Georgia,'Times New Roman',serif" font-weight="900" font-size="${t.length > 1 ? 58 : 76}" fill="url(#${g})" stroke="${glow}" stroke-width="3" paint-order="stroke">${t}</text></svg>`;

  root.SYMBOLS = {
    BUF: `<svg viewBox="0 0 100 100"><path d="M16 34C4 30 2 16 14 8c-4 10 2 18 12 22z" fill="url(#gHorn)"/><path d="M84 34c12-4 14-18 2-26 4 10-2 18-12 22z" fill="url(#gHorn)"/>
      <path d="M50 8C72 6 90 20 91 44c1 24-12 46-41 50C21 90 8 68 9 44 10 20 28 6 50 8z" fill="#2c180a"/>
      <path d="M22 30c6-10 16-14 28-14s22 4 28 14c-6-3-16-6-28-6s-22 3-28 6z" fill="#46270f"/>
      <path d="M30 30c10-6 30-6 40 0 6 22 0 48-20 60-20-12-26-38-20-60z" fill="url(#gFurBrown)"/>
      <ellipse cx="50" cy="73" rx="15" ry="11" fill="#b07a44"/><ellipse cx="43.5" cy="73" rx="3" ry="4.5" fill="#2a1408"/><ellipse cx="56.5" cy="73" rx="3" ry="4.5" fill="#2a1408"/>
      ${eye(38, 46, '#f3d08a')}${eye(62, 46, '#f3d08a')}
      <path d="M32 40l12 4M68 40L56 44" stroke="#2a1408" stroke-width="3" stroke-linecap="round"/></svg>`,

    EAG: `<svg viewBox="0 0 100 100"><path d="M10 98C8 70 22 50 40 44h22c16 8 26 28 28 54z" fill="url(#gFeather)"/>
      <path d="M26 98c0-16 6-30 14-38M44 98c0-14 2-26 6-34M62 98c-2-14-2-24-6-34" stroke="#2b1708" stroke-width="2" fill="none" opacity=".5"/>
      <circle cx="50" cy="34" r="22" fill="#f8f3e6"/><path d="M30 40c4-14 14-22 26-20-10 4-16 12-18 22z" fill="#e6dcc4"/>
      <path d="M66 26c16-1 28 8 24 22-8-2-16-5-24-8z" fill="url(#gBeak)"/><path d="M66 38c8 0 16 2 24 8" stroke="#8a5a05" stroke-width="2" fill="none"/>
      <circle cx="58" cy="29" r="4.2" fill="#f2b312"/><circle cx="58.5" cy="29" r="2.2" fill="#140a04"/>
      <path d="M50 22l16 5" stroke="#3a2210" stroke-width="3.5" stroke-linecap="round"/></svg>`,

    COU: `<svg viewBox="0 0 100 100"><path d="M20 34L24 6l22 16zM80 34L76 6 54 22z" fill="#b87a3c"/><path d="M26 28l2-14 11 8zM74 28l-2-14-11 8z" fill="#e9a3a3"/>
      <ellipse cx="50" cy="56" rx="35" ry="33" fill="url(#gCat)"/>
      <path d="M18 56l10 2M18 64l10-1M82 56l-10 2M82 64l-10-1" stroke="#7a4a1c" stroke-width="3" stroke-linecap="round"/>
      <path d="M50 28v14" stroke="#8a5424" stroke-width="3"/>
      <ellipse cx="50" cy="70" rx="18" ry="13" fill="#f7ead2"/><path d="M43 60h14l-7 8z" fill="#c4606a"/>
      <path d="M50 68v6c-4 4-9 4-12 0M50 74c4 4 9 4 12 0" stroke="#5a2a14" stroke-width="2.2" fill="none" stroke-linecap="round"/>
      <path d="M26 46c4-6 14-6 18 0-4 5-14 5-18 0z" fill="#f4c430"/><path d="M74 46c-4-6-14-6-18 0 4 5 14 5 18 0z" fill="#f4c430"/>
      <rect x="33.5" y="42.5" width="3" height="8" rx="1.5" fill="#140a04"/><rect x="63.5" y="42.5" width="3" height="8" rx="1.5" fill="#140a04"/></svg>`,

    WOL: `<svg viewBox="0 0 100 100"><path d="M18 40L22 4l24 20zM82 40L78 4 54 24z" fill="#4e5864"/><path d="M26 30l2-16 12 10zM74 30l-2-16-12 10z" fill="#aab4be"/>
      <path d="M50 18c28 0 36 26 28 48-6 16-18 28-28 30-10-2-22-14-28-30-8-22 0-48 28-48z" fill="url(#gWolf)"/>
      <path d="M38 62c6-12 18-12 24 0-2 20-8 30-12 30s-10-10-12-30z" fill="#e1e6eb"/>
      <ellipse cx="50" cy="84" rx="7" ry="5" fill="#101418"/><path d="M50 88v5" stroke="#101418" stroke-width="2.5"/>
      <path d="M28 48c6-6 14-6 18 0-5 4-13 4-18 0z" fill="#ffb21a"/><path d="M72 48c-6-6-14-6-18 0 5 4 13 4 18 0z" fill="#ffb21a"/>
      <circle cx="38" cy="48" r="2.6" fill="#0e0a04"/><circle cx="62" cy="48" r="2.6" fill="#0e0a04"/>
      <path d="M26 40l14 6M74 40L60 46" stroke="#2a323a" stroke-width="3" stroke-linecap="round"/></svg>`,

    ELK: `<svg viewBox="0 0 100 100"><g stroke="#e9d3a0" stroke-width="5" stroke-linecap="round" fill="none"><path d="M36 36C26 26 22 14 14 4M27 27c-6-2-12-2-19-6M31 31c-4-14-2-20 0-28"/><path d="M64 36c10-10 14-22 22-32M73 27c6-2 12-2 19-6M69 31c4-14 2-20 0-28"/></g>
      <path d="M26 46L6 52l22 8zM74 46l20 6-22 8z" fill="#8a5224"/>
      <path d="M30 34c10-5 30-5 40 0 5 24-4 52-20 62C34 86 25 58 30 34z" fill="url(#gElk)"/>
      <ellipse cx="50" cy="80" rx="12" ry="10" fill="#e0c196"/><ellipse cx="50" cy="86" rx="6" ry="4" fill="#1e1208"/>
      ${eye(39, 52, '#e8c27a')}${eye(61, 52, '#e8c27a')}</svg>`,

    A: card('A', 'gRed', '#3a0b05'),
    K: card('K', 'gBlue', '#071a38'),
    Q: card('Q', 'gPurple', '#1e0638'),
    J: card('J', 'gGreen', '#062a14'),

    WILD: `<svg viewBox="0 0 100 100"><g stroke="#ffe27a" stroke-width="4" stroke-linecap="round">${Array.from({ length: 16 }, (_, i) => { const a = i * Math.PI / 8; return `<line x1="${50 + Math.cos(a) * 30}" y1="${46 + Math.sin(a) * 30}" x2="${50 + Math.cos(a) * 44}" y2="${46 + Math.sin(a) * 44}"/>`; }).join('')}</g>
      <circle cx="50" cy="46" r="27" fill="url(#gSun)" stroke="#fff3b0" stroke-width="2"/>
      <path d="M2 60h96v26H2z" fill="#8a1e0a" opacity=".92"/><path d="M2 60h96M2 86h96" stroke="#ffd552" stroke-width="2.5"/>
      <text x="50" y="81" text-anchor="middle" font-family="Georgia,serif" font-weight="900" font-size="25" fill="#ffe27a" stroke="#3a0b02" stroke-width="2" paint-order="stroke" letter-spacing="2">WILD</text></svg>`,

    COIN: `<svg viewBox="0 0 100 100"><circle cx="50" cy="50" r="44" fill="url(#gGold)" stroke="#8a5a05" stroke-width="3"/><circle cx="50" cy="50" r="35" fill="none" stroke="#fff1a8" stroke-width="2.5" stroke-dasharray="3 4"/>
      <circle cx="50" cy="50" r="30" fill="url(#gGoldIn)" stroke="#b8741a" stroke-width="2"/>
      <path d="M50 24l7.5 17 18 1.5-13.8 12 4.3 18L50 63.5 33.9 72.5l4.3-18L24.5 42.5l18-1.5z" fill="#fff7c8" stroke="#a8660d" stroke-width="2"/>
      <path d="M22 28a40 40 0 0 1 30-16" stroke="#fff" stroke-width="3.5" stroke-linecap="round" fill="none" opacity=".7"/></svg>`
  };

  root.SYMBOL_NAMES = { BUF: 'Buffalo', EAG: 'Eagle', COU: 'Cougar', WOL: 'Wolf', ELK: 'Elk', A: 'Ace', K: 'King', Q: 'Queen', J: 'Jack', WILD: 'Wild', COIN: 'Scatter' };
})(window);
