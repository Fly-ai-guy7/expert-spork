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
Items at or below reorder level. → `InventoryOut[]`

### `GET /inventory/{drug_id}`
→ `InventoryOut` | `404`

### `PUT /inventory/{drug_id}`  *(pharmacist/admin)*
```json
{ "quantity": 40, "reorder_level": 10 }
```
→ `200` `InventoryOut`

---

## Orders — `/orders`

### `POST /orders`  *(auth)*
Create an order.
```json
{ "items": [ { "drug_id": 3, "quantity": 1 } ] }
```
**Rx gating:** if any item has `rx: true`, the order status is
`pending_rx_verification` and cannot advance to payment until verified.
Otherwise status is `pending_payment`.
→ `201` `OrderOut`

### `GET /orders/{order_id}`  *(auth — owner or staff)*
→ `OrderOut` | `404`

### `GET /orders/{order_id}/rx-whatsapp`  *(auth)*
Returns a `wa.me` link for the patient to confirm an Rx order with the pharmacy.
→ `{ "whatsapp_url": "https://wa.me/..." }`

### `POST /orders/{order_id}/verify-rx`  *(pharmacist/admin)*
Pharmacist verifies the prescription; order → `pending_payment`.
→ `200` `OrderOut`

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
