// RxEgypt shared API client — demo mode + live backend switching.
// Astra Intelligence Services (Misr) — AISE
//
// Configuration lives in config.js (loaded BEFORE this file):
//   window.RXEGYPT_API_URL   = 'http://localhost:8000/api/v1';  // enables LIVE mode
//   window.RXEGYPT_TOKEN_KEY = 'rxegypt_token_pharmacist';      // optional, per-role
// If RXEGYPT_API_URL is unset, the client runs in DEMO mode against the bundled
// sample drug data — no backend required.

(function (global) {
  const API_URL = global.RXEGYPT_API_URL || null;
  const DEMO = !API_URL;
  // Namespace the token per page so a patient and a pharmacist on the same
  // origin don't clobber each other's session.
  const TOKEN_KEY = global.RXEGYPT_TOKEN_KEY || 'rxegypt_token';
  const DEMO_WHATSAPP = '20100000000'; // demo-only placeholder pharmacy number

  let _cachedUser = null;     // memoized GET /auth/me result (live)
  let _lastDemoOrder = null;  // demo orders have random ids and no store

  // --- Demo dataset (subset of backend/seed/drugs_egypt.json) ---
  const DEMO_DRUGS = [
    { id: 1, name_en: 'Panadol Extra', name_ar: 'بنادول إكسترا', generic: 'Paracetamol + Caffeine', form: 'tablet', strength: '500mg/65mg', category: 'Analgesic', manufacturer: 'GSK', barcode: '6223000111014', price_egp: 28.0, rx: false, rx_source: 'demo' },
    { id: 2, name_en: 'Brufen', name_ar: 'بروفين', generic: 'Ibuprofen', form: 'tablet', strength: '400mg', category: 'NSAID', manufacturer: 'Abbott', barcode: '6223000111038', price_egp: 22.5, rx: false, rx_source: 'demo' },
    { id: 3, name_en: 'Augmentin 1g', name_ar: 'أوجمنتين', generic: 'Amoxicillin + Clavulanic Acid', form: 'tablet', strength: '875mg/125mg', category: 'Antibiotic', manufacturer: 'GSK', barcode: '6223000111052', price_egp: 96.0, rx: true, rx_source: 'demo' },
    { id: 4, name_en: 'Zithromax', name_ar: 'زيثروماكس', generic: 'Azithromycin', form: 'tablet', strength: '500mg', category: 'Antibiotic', manufacturer: 'Pfizer', barcode: '6223000111076', price_egp: 78.0, rx: true, rx_source: 'demo' },
    { id: 5, name_en: 'Concor', name_ar: 'كونكور', generic: 'Bisoprolol', form: 'tablet', strength: '5mg', category: 'Cardiovascular', manufacturer: 'Merck', barcode: '6223000111106', price_egp: 60.0, rx: true, rx_source: 'demo' },
    { id: 6, name_en: 'Glucophage', name_ar: 'جلوكوفاج', generic: 'Metformin', form: 'tablet', strength: '850mg', category: 'Antidiabetic', manufacturer: 'Merck', barcode: '6223000111144', price_egp: 32.0, rx: true, rx_source: 'demo' },
    { id: 7, name_en: 'Claritine', name_ar: 'كلاريتين', generic: 'Loratadine', form: 'tablet', strength: '10mg', category: 'Antihistamine', manufacturer: 'Bayer', barcode: '6223000111182', price_egp: 36.0, rx: false, rx_source: 'demo' },
    { id: 8, name_en: 'Nexium', name_ar: 'نيكسيم', generic: 'Esomeprazole', form: 'capsule', strength: '40mg', category: 'Gastrointestinal', manufacturer: 'AstraZeneca', barcode: '6223000111205', price_egp: 110.0, rx: false, rx_source: 'demo' },
    { id: 9, name_en: 'Vitamin C 1000', name_ar: 'فيتامين سي', generic: 'Ascorbic Acid', form: 'effervescent', strength: '1000mg', category: 'Supplement', manufacturer: 'Pharco', barcode: '6223000111250', price_egp: 40.0, rx: false, rx_source: 'demo' },
    { id: 10, name_en: 'ORS Sachet', name_ar: 'محلول معالجة الجفاف', generic: 'Oral Rehydration Salts', form: 'sachet', strength: '—', category: 'Electrolyte', manufacturer: 'CID', barcode: '6223000111304', price_egp: 5.0, rx: false, rx_source: 'demo' }
  ];

  // --- token storage ---
  function getToken() {
    return global.localStorage ? localStorage.getItem(TOKEN_KEY) : null;
  }
  function setToken(t) {
    if (global.localStorage) localStorage.setItem(TOKEN_KEY, t);
  }
  function clearToken() {
    if (global.localStorage) localStorage.removeItem(TOKEN_KEY);
    _cachedUser = null;
  }
  function authHeader() {
    const t = getToken();
    return t ? { Authorization: `Bearer ${t}` } : {};
  }

  async function http(path, options = {}) {
    const res = await fetch(API_URL + path, {
      headers: { 'Content-Type': 'application/json', ...authHeader(), ...(options.headers || {}) },
      ...options
    });
    if (!res.ok) {
      const detail = await res.json().catch(() => ({}));
      const err = new Error(detail.detail || `HTTP ${res.status}`);
      err.status = res.status;            // let UI branch on 401 / 403
      if (res.status === 401) clearToken(); // stale token — drop it
      throw err;
    }
    return res.status === 204 ? null : res.json();
  }

  const DEMO_USER = { id: 0, email: 'demo@local', full_name: 'Demo User', phone: '', role: 'patient' };

  const api = {
    mode: DEMO ? 'demo' : 'live',

    // --- auth helpers ---
    isAuthenticated() {
      return DEMO ? true : !!getToken();
    },

    logout() {
      clearToken();
    },

    async currentUser() {
      if (DEMO) return { ...DEMO_USER };
      if (_cachedUser) return _cachedUser;
      _cachedUser = await http('/auth/me');
      return _cachedUser;
    },

    async login(email, password) {
      if (DEMO) {
        setToken('demo-token');
        return { access_token: 'demo-token', token_type: 'bearer' };
      }
      const body = new URLSearchParams({ username: email, password });
      const res = await fetch(API_URL + '/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body
      });
      if (!res.ok) {
        const detail = await res.json().catch(() => ({}));
        const err = new Error(detail.detail || 'Incorrect email or password');
        err.status = res.status;
        throw err;
      }
      const data = await res.json();
      setToken(data.access_token);
      _cachedUser = null;
      return data;
    },

    // Register returns a UserOut (NOT a token). Callers must login() afterwards.
    async register(payload) {
      if (DEMO) return { id: 1, role: 'patient', ...payload };
      return http('/auth/register', { method: 'POST', body: JSON.stringify(payload) });
    },

    async me() {
      return this.currentUser();
    },

    // --- drugs ---
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
        if (!d) { const e = new Error('No drug found for barcode'); e.status = 404; throw e; }
        return d;
      }
      return http(`/drugs/barcode/${encodeURIComponent(barcode)}`);
    },

    // --- orders ---
    async createOrder(items) {
      if (DEMO) {
        const lines = items.map((i) => {
          const d = DEMO_DRUGS.find((x) => x.id === i.drug_id) || {};
          return { drug_id: i.drug_id, quantity: i.quantity, unit_price_egp: d.price_egp || 0, rx: !!d.rx };
        });
        const requires_rx = lines.some((l) => l.rx);
        const total = lines.reduce((s, l) => s + l.unit_price_egp * l.quantity, 0);
        _lastDemoOrder = {
          id: Math.floor(Math.random() * 100000),
          status: requires_rx ? 'pending_rx_verification' : 'pending_payment',
          requires_rx_verification: requires_rx,
          rx_verified_by: '',
          total_egp: Math.round(total * 100) / 100,
          items: lines,
          created_at: new Date().toISOString()
        };
        return _lastDemoOrder;
      }
      return http('/orders', { method: 'POST', body: JSON.stringify({ items }) });
    },

    async getOrder(orderId) {
      if (DEMO) return _lastDemoOrder || { id: orderId, status: 'pending_payment', items: [], total_egp: 0 };
      return http(`/orders/${orderId}`);
    },

    async rxWhatsApp(orderId) {
      if (DEMO) {
        const o = _lastDemoOrder || { id: orderId, total_egp: 0 };
        const msg = `Experts Pharmacy — Rx confirmation\nOrder #${o.id}\nTotal: EGP ${(o.total_egp || 0).toFixed(2)}\nPlease confirm my prescription.`;
        return { whatsapp_url: `https://wa.me/${DEMO_WHATSAPP}?text=${encodeURIComponent(msg)}` };
      }
      return http(`/orders/${orderId}/rx-whatsapp`);
    },

    async pendingRxOrders() {
      if (DEMO) {
        return _lastDemoOrder && _lastDemoOrder.requires_rx_verification
          ? [{
              id: _lastDemoOrder.id, patient_email: 'demo@local', patient_name: 'Demo User',
              patient_phone: '', total_egp: _lastDemoOrder.total_egp,
              created_at: _lastDemoOrder.created_at,
              items: (_lastDemoOrder.items || []).map((l) => {
                const d = DEMO_DRUGS.find((x) => x.id === l.drug_id) || {};
                return { drug_id: l.drug_id, name_en: d.name_en || '', name_ar: d.name_ar || '', rx: !!d.rx, quantity: l.quantity, unit_price_egp: l.unit_price_egp };
              })
            }]
          : [];
      }
      return http('/orders/pending-rx');
    },

    async verifyRx(orderId) {
      if (DEMO) { if (_lastDemoOrder && _lastDemoOrder.id === orderId) _lastDemoOrder.status = 'pending_payment'; return { id: orderId, status: 'pending_payment', requires_rx_verification: true, rx_verified_by: 'demo-pharmacist', items: [], total_egp: 0 }; }
      return http(`/orders/${orderId}/verify-rx`, { method: 'POST' });
    },

    async rejectRx(orderId) {
      if (DEMO) { if (_lastDemoOrder && _lastDemoOrder.id === orderId) _lastDemoOrder.status = 'cancelled'; return { id: orderId, status: 'cancelled', requires_rx_verification: true, rx_verified_by: 'demo-pharmacist', items: [], total_egp: 0 }; }
      return http(`/orders/${orderId}/reject-rx`, { method: 'POST' });
    },

    // --- consent + PDPL data-subject rights ---
    async recordConsent(payload) {
      if (DEMO) return { id: 1, ...payload, created_at: new Date().toISOString() };
      return http('/auth/consent', { method: 'POST', body: JSON.stringify(payload) });
    },

    async consentStatus() {
      if (DEMO) return { granted: true, policy_version: '1.0', updated_at: new Date().toISOString() };
      return http('/auth/consent');
    },

    async withdrawConsent() {
      if (DEMO) return { id: 1, purpose: 'health_data_processing', granted: false, policy_version: '1.0', created_at: new Date().toISOString() };
      return http('/auth/consent/withdraw', { method: 'POST' });
    },

    async exportMyData() {
      if (DEMO) return { user: DEMO_USER, consents: [], orders: _lastDemoOrder ? [_lastDemoOrder] : [] };
      return http('/auth/export');
    },

    async deleteMyAccount() {
      if (DEMO) { clearToken(); return { detail: 'Account deleted (demo).', user_id: 0 }; }
      const r = await http('/auth/account', { method: 'DELETE' });
      clearToken(); // session is now invalid
      return r;
    },

    // --- inventory ---
    async getInventory(drugId) {
      if (DEMO) return { drug_id: drugId, quantity: 0, reorder_level: 5, updated_at: new Date().toISOString() };
      return http(`/inventory/${drugId}`);
    },

    async lowStock() {
      if (DEMO) return [];
      return http('/inventory/low-stock');
    },

    async updateInventory(drugId, payload) {
      if (DEMO) {
        return { drug_id: drugId, quantity: payload.quantity, reorder_level: payload.reorder_level ?? 5, updated_at: new Date().toISOString() };
      }
      return http(`/inventory/${drugId}`, { method: 'PUT', body: JSON.stringify(payload) });
    }
  };

  global.RxEgyptAPI = api;
})(window);
