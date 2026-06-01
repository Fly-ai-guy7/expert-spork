// Headless unit tests for rxegypt-api.js DEMO-mode logic.
// Loads the browser IIFE in a vm sandbox with stubbed window/localStorage
// (no RXEGYPT_API_URL -> demo mode, so no network is touched).
//
//   node test/api.test.js
const assert = require('node:assert');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

function loadApi() {
  const code = fs.readFileSync(path.join(__dirname, '..', 'rxegypt-api.js'), 'utf8');
  const store = {};
  const localStorage = {
    getItem: (k) => (k in store ? store[k] : null),
    setItem: (k, v) => { store[k] = String(v); },
    removeItem: (k) => { delete store[k]; },
  };
  const window = { localStorage };
  const ctx = vm.createContext({ window, localStorage, console });
  vm.runInContext(code, ctx);
  return window.RxEgyptAPI;
}

async function main() {
  const api = loadApi();

  assert.strictEqual(api.mode, 'demo', 'should be in demo mode');

  // search
  const aug = await api.searchDrugs('augmentin');
  assert.ok(aug.length >= 1 && /Augmentin/.test(aug[0].name_en), 'finds Augmentin');
  assert.strictEqual(aug[0].rx, true, 'Augmentin is Rx');
  const otcOnly = await api.searchDrugs('', { rx: false });
  assert.ok(otcOnly.every((d) => d.rx === false), 'rx:false filter returns only OTC');

  // barcode
  const byCode = await api.lookupBarcode('6223000111052');
  assert.strictEqual(byCode.name_en, 'Augmentin 1g', 'barcode lookup');
  await assert.rejects(() => api.lookupBarcode('0000000000000'), /No drug found/, 'unknown barcode throws');

  // Rx gating in createOrder
  const rxOrder = await api.createOrder([{ drug_id: 3, quantity: 1 }]); // Augmentin
  assert.strictEqual(rxOrder.requires_rx_verification, true, 'Rx order gated');
  assert.strictEqual(rxOrder.status, 'pending_rx_verification');

  const otcOrder = await api.createOrder([{ drug_id: 1, quantity: 2 }]); // Panadol 28*2
  assert.strictEqual(otcOrder.status, 'pending_payment', 'OTC order pending payment');
  assert.strictEqual(otcOrder.total_egp, 56, 'OTC total computed');

  // payment lifecycle (demo) operates on the last order
  const intent = await api.payOrder(otcOrder.id);
  assert.strictEqual(intent.mock, true, 'demo pay is mock');
  const paid = await api.mockConfirmPayment(otcOrder.id, true);
  assert.strictEqual(paid.status, 'paid', 'mock confirm marks paid');
  const paidQueue = await api.paidOrders();
  assert.ok(paidQueue.some((o) => o.id === otcOrder.id), 'paid order shows in fulfillment queue');

  // auth helpers
  assert.strictEqual(api.isAuthenticated(), true, 'demo is always authenticated');
  await api.login('x@y.com', 'whatever');
  api.logout();

  console.log('rxegypt-api demo tests: all assertions passed ✓');
}

main().catch((e) => { console.error('FAILED:', e.message); process.exit(1); });
