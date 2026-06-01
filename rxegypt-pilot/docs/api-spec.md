# RxEgypt API Specification (v1)

Base URL: `/api/v1`
Auth: JWT Bearer (`Authorization: Bearer <token>`) where noted.

Interactive docs are available at `/docs` (Swagger) when the server is running.

---

## Meta

### `GET /health`
Liveness check. Returns `{ "status": "ok", ... }`. No auth.

---

## Auth & Consent — `/auth`

### `POST /auth/register`
Register a patient account.
```json
{ "email": "patient@example.com", "password": "min8chars", "full_name": "", "phone": "" }
```
→ `201` `UserOut`

### `POST /auth/login`
OAuth2 password form (`application/x-www-form-urlencoded`): `username`, `password`.
→ `200` `{ "access_token": "...", "token_type": "bearer" }`

### `GET /auth/me`  *(auth)*
Returns the current `UserOut`.

### `POST /auth/consent`  *(auth)*
Record explicit PDPL consent. Timestamped server-side.
```json
{ "purpose": "health_data_processing", "granted": true, "policy_version": "1.0" }
```
→ `201` `ConsentOut`

### PDPL data-subject rights *(all auth)*

| Method | Path | Purpose | Response |
|---|---|---|---|
| `GET` | `/auth/consent` | Current consent decision (latest) | `{ granted, policy_version, updated_at }` |
| `POST` | `/auth/consent/withdraw` | Withdraw consent (logs `granted=false`) | `201` `ConsentOut` |
| `GET` | `/auth/export` | Data portability — user + consents + orders | `DataExport` |
| `DELETE` | `/auth/account` | Erasure — anonymize PII, block login, retain de-identified orders | `200 { detail, user_id }` |

After `DELETE /auth/account` the user's existing token and original credentials
are rejected (`401`).

---

## Drugs — `/drugs`

### `GET /drugs?q=&category=&rx=&limit=`
Search by name (EN/AR) or generic. Optional `category`, `rx` (bool), `limit` (≤200).
→ `200` `DrugOut[]`

### `GET /drugs/barcode/{barcode}`
EAN-13 lookup. → `200` `DrugOut` | `404`

### `GET /drugs/{drug_id}`
→ `200` `DrugOut` | `404`

---

## Inventory — `/inventory`

### `GET /inventory/low-stock`
Items at or below reorder level, lowest first, enriched with drug names.
→ `LowStockItem[]` `{ drug_id, name_en, name_ar, quantity, reorder_level }`

### `GET /inventory/{drug_id}`
→ `InventoryOut` | `404`

### `PUT /inventory/{drug_id}`  *(pharmacist/admin)*
```json
{ "quantity": 40, "reorder_level": 10 }
```
→ `200` `InventoryOut`

---

## Orders — `/orders`

### `GET /orders`  *(auth)*
The current user's orders, newest first.
→ `200` `OrderOut[]`

### `POST /orders`  *(auth)*
Create an order.
```json
{ "items": [ { "drug_id": 3, "quantity": 1 } ] }
```
**Rx gating:** if any item has `rx: true`, the order status is
`pending_rx_verification` and cannot advance to payment until verified.
Otherwise status is `pending_payment`.
**Legal guards:** requires a granted PDPL `Consent` on record (else `403`);
rejects any `controlled: true` item (else `400` — in-pharmacy only).
→ `201` `OrderOut` · `403` no consent · `400` controlled item / empty

### `GET /orders/pending-rx`  *(pharmacist/admin)*
Verification queue: orders in `pending_rx_verification`, oldest first, enriched
with patient contact and drug names.
→ `200` `RxQueueOrder[]`
```json
[ { "id": 12, "patient_email": "...", "patient_name": "...", "patient_phone": "...",
    "total_egp": 96.0, "created_at": "...",
    "items": [ { "drug_id": 2, "name_en": "Augmentin", "name_ar": "...", "rx": true,
                 "quantity": 1, "unit_price_egp": 96.0 } ] } ]
```

### `GET /orders/paid`  *(pharmacist/admin)*
Fulfillment queue: `paid` orders awaiting hand-off, oldest first (same
`RxQueueOrder[]` shape as the Rx queue).
→ `200` `RxQueueOrder[]`

### `GET /orders/{order_id}`  *(auth — owner or staff)*
→ `OrderOut` | `404`

### `GET /orders/{order_id}/rx-whatsapp`  *(auth)*
Returns a `wa.me` link for the patient to confirm an Rx order with the pharmacy.
→ `{ "whatsapp_url": "https://wa.me/..." }`

### `POST /orders/{order_id}/verify-rx`  *(pharmacist/admin)*
Pharmacist verifies the prescription; order → `pending_payment`.
→ `200` `OrderOut` · `400` if not awaiting verification

### `POST /orders/{order_id}/reject-rx`  *(pharmacist/admin)*
Pharmacist declines the prescription; order → `cancelled`.
→ `200` `OrderOut` · `400` if not awaiting verification

### `POST /orders/{order_id}/pay`  *(auth — owner)*
Create a payment intent for a `pending_payment` order.
→ `200` `{ order_id, amount_egp, reference, checkout_url, mock }`
- **Live (Paymob configured):** `checkout_url` is the Paymob iframe URL; `mock=false`.
- **Mock (no `PAYMOB_API_KEY`):** `mock=true`; settle via `POST /payments/mock/confirm`.
- `400` if the order is not awaiting payment.

### `POST /orders/{order_id}/fulfill`  *(pharmacist/admin)*
Mark a `paid` order as `fulfilled` (handed to the patient). Decrements stock for
each item that has an inventory record (clamped at 0).
→ `200` `OrderOut` · `400` if not paid

---

## Payments — `/payments`

### `POST /payments/mock/confirm`  *(auth — owner; MOCK mode only)*
Simulates the gateway settling a payment (no Paymob credentials configured).
```json
{ "order_id": 12, "success": true }
```
→ `200` `OrderOut` (status `paid` on success) · `404` in live mode

### `POST /payments/paymob/callback`  *(no auth; LIVE mode only)*
Paymob processed-transaction server callback. HMAC-SHA512 verified via the
`hmac` query param; on success the referenced order → `paid`.
→ `200` `{ received, order_id, status }` · `400` invalid HMAC · `404` in mock mode

---

## Order status lifecycle

```
cart → pending_rx_verification → pending_payment → paid → fulfilled
                                       ↑ (OTC-only orders start here)
                                   cancelled (terminal)
```

---
🌿 ✦ ASTRA INTELLIGENCE SERVICES ✦ 🌿 | ⚜ MISR ⚜
RxEgypt Pilot · docs/api-spec.md · Generated 2026-05-31
