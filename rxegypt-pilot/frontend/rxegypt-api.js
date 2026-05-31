// RxEgypt shared API client — demo mode + live backend switching.
// Astra Intelligence Services (Misr) — AISE
//
// To point at a live backend, set this before loading the page (or edit here):
//   window.RXEGYPT_API_URL = 'http://localhost:8000/api/v1';
// If RXEGYPT_API_URL is unset, the client runs in DEMO mode against the bundled
// sample drug data — no backend required.

(function (global) {
  const API_URL = global.RXEGYPT_API_URL || null;
  const DEMO = !API_URL;

  // --- Demo dataset (subset of backend/seed/drugs_egypt.json) ---
  const DEMO_DRUGS = [
    { id: 1, name_en: 'Panadol Extra', name_ar: 'بنادول إكسترا', generic: 'Paracetamol + Caffeine', form: 'tablet', strength: '500mg/65mg', category: 'Analgesic', barcode: '6223000111014', price_egp: 28.0, rx: false },
    { id: 2, name_en: 'Brufen', name_ar: 'بروفين', generic: 'Ibuprofen', form: 'tablet', strength: '400mg', category: 'NSAID', barcode: '6223000111038', price_egp: 22.5, rx: false },
    { id: 3, name_en: 'Augmentin 1g', name_ar: 'أوجمنتين', generic: 'Amoxicillin + Clavulanic Acid', form: 'tablet', strength: '875mg/125mg', category: 'Antibiotic', barcode: '6223000111052', price_egp: 96.0, rx: true },
    { id: 4, name_en: 'Zithromax', name_ar: 'زيثروماكس', generic: 'Azithromycin', form: 'tablet', strength: '500mg', category: 'Antibiotic', barcode: '6223000111076', price_egp: 78.0, rx: true },
    { id: 5, name_en: 'Concor', name_ar: 'كونكور', generic: 'Bisoprolol', form: 'tablet', strength: '5mg', category: 'Cardiovascular', barcode: '6223000111106', price_egp: 60.0, rx: true },
    { id: 6, name_en: 'Glucophage', name_ar: 'جلوكوفاج', generic: 'Metformin', form: 'tablet', strength: '850mg', category: 'Antidiabetic', barcode: '6223000111144', price_egp: 32.0, rx: true },
    { id: 7, name_en: 'Claritine', name_ar: 'كلاريتين', generic: 'Loratadine', form: 'tablet', strength: '10mg', category: 'Antihistamine', barcode: '6223000111182', price_egp: 36.0, rx: false },
    { id: 8, name_en: 'Nexium', name_ar: 'نيكسيم', generic: 'Esomeprazole', form: 'capsule', strength: '40mg', category: 'Gastrointestinal', barcode: '6223000111205', price_egp: 110.0, rx: false },
    { id: 9, name_en: 'Vitamin C 1000', name_ar: 'فيتامين سي', generic: 'Ascorbic Acid', form: 'effervescent', strength: '1000mg', category: 'Supplement', barcode: '6223000111250', price_egp: 40.0, rx: false },
    { id: 10, name_en: 'ORS Sachet', name_ar: 'محلول معالجة الجفاف', generic: 'Oral Rehydration Salts', form: 'sachet', strength: '—', category: 'Electrolyte', barcode: '6223000111304', price_egp: 5.0, rx: false }
  ];

  async function http(path, options = {}) {
    const res = await fetch(API_URL + path, {
      headers: { 'Content-Type': 'application/json', ...authHeader(), ...(options.headers || {}) },
      ...options
    });
    if (!res.ok) {
      const detail = await res.json().catch(() => ({}));
      throw new Error(detail.detail || `HTTP ${res.status}`);
    }
    return res.status === 204 ? null : res.json();
  }

  function authHeader() {
    const t = global.localStorage ? localStorage.getItem('rxegypt_token') : null;
    return t ? { Authorization: `Bearer ${t}` } : {};
  }

  const api = {
    mode: DEMO ? 'demo' : 'live',

    async searchDrugs(query = '', opts = {}) {
      if (DEMO) {
        const q = query.trim().toLowerCase();
        return DEMO_DRUGS.filter((d) => {
          if (opts.rx !== undefined && d.rx !== opts.rx) return false;
          if (!q) return true;
          return [d.name_en, d.name_ar, d.generic].some((f) => f.toLowerCase().includes(q));
        });
      }
      const p = new URLSearchParams();
      if (query) p.set('q', query);
      if (opts.rx !== undefined) p.set('rx', String(opts.rx));
      return http(`/drugs?${p.toString()}`);
    },

    async lookupBarcode(barcode) {
      if (DEMO) {
        const d = DEMO_DRUGS.find((x) => x.barcode === barcode);
        if (!d) throw new Error('No drug found for barcode');
        return d;
      }
      return http(`/drugs/barcode/${encodeURIComponent(barcode)}`);
    },

    async createOrder(items) {
      if (DEMO) {
        const lines = items.map((i) => {
          const d = DEMO_DRUGS.find((x) => x.id === i.drug_id) || {};
          return { ...i, unit_price_egp: d.price_egp || 0, rx: !!d.rx };
        });
        const requires_rx = lines.some((l) => l.rx);
        const total = lines.reduce((s, l) => s + l.unit_price_egp * l.quantity, 0);
        return {
          id: Math.floor(Math.random() * 100000),
          status: requires_rx ? 'pending_rx_verification' : 'pending_payment',
          requires_rx_verification: requires_rx,
          total_egp: Math.round(total * 100) / 100,
          items: lines
        };
      }
      return http('/orders', { method: 'POST', body: JSON.stringify({ items }) });
    },

    async login(email, password) {
      if (DEMO) {
        localStorage.setItem('rxegypt_token', 'demo-token');
        return { access_token: 'demo-token', token_type: 'bearer' };
      }
      const body = new URLSearchParams({ username: email, password });
      const res = await fetch(API_URL + '/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body
      });
      if (!res.ok) throw new Error('Login failed');
      const data = await res.json();
      localStorage.setItem('rxegypt_token', data.access_token);
      return data;
    },

    async recordConsent(payload) {
      if (DEMO) {
        return { id: 1, ...payload, created_at: new Date().toISOString() };
      }
      return http('/auth/consent', { method: 'POST', body: JSON.stringify(payload) });
    }
  };

  global.RxEgyptAPI = api;
})(window);
