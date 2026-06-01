# RXEG-LEGAL-001 — Egyptian Regulatory Compliance Framework

**Project:** RxEgypt Pilot — Experts Pharmacy Hurghada
**Owner:** Michael Gamal (Legal), AISE
**Status:** Living document — review before go-live

---

## 1. Scope

This framework governs the legal and regulatory obligations for operating
RxEgypt as a B2B pharmacy-management and patient-facing platform in the Arab
Republic of Egypt, piloted at Experts Pharmacy, Al Ahyaa, Red Sea Governorate.

## 2. Governing Authorities & Instruments

| Area | Authority / Instrument |
|---|---|
| Drug regulation | Egyptian Drug Authority (EDA) |
| Pharmacy practice | Law 127/1955 (Pharmacy Practice) and amendments |
| Prescription-only dispensing | EDA scheduling; controlled substances under Law 182/1960 |
| Data protection | Personal Data Protection Law (PDPL) — Law 151/2020 |
| Consumer protection | Law 181/2018 |
| Track & Trace | EDA serialization / GS1 requirements (Phase 2) |
| Health insurance | Universal Health Insurance (UHI) — Law 2/2018 (Phase 3) |

## 3. Mandatory Controls Before Go-Live

### 3.1 Prescription (Rx) Drug Gating — **BLOCKING**
- Every drug record carries an `rx` boolean. Drugs with `rx: true` are
  prescription-only and **must not** be fulfilled without pharmacist verification.
- Implementation: an order containing any Rx item is placed in
  `pending_rx_verification` and cannot advance to payment until a pharmacist
  calls the verification endpoint (`POST /orders/{id}/verify-rx`).
- Patient is routed to a WhatsApp confirmation flow with the pharmacy.
- Controlled substances (e.g. Tramadol) require additional EDA-compliant
  handling and must never be orderable online in the pilot.

### 3.2 PDPL Consent — **BLOCKING**
- Explicit, informed, freely-given consent must be collected **before** any
  health or personal data is processed (Art. 2, Law 151/2020).
- Consent is logged server-side with a timestamp and policy version
  (`POST /auth/consent`, `consents` table).
- Patients must be able to withdraw consent; withdrawal handling is a
  documented Phase-1.5 task.

### 3.3 Health Information Guide Disclaimers — **BLOCKING**
- The former "symptom checker" is renamed **Health Information Guide**.
- Bilingual (EN + AR) disclaimer displayed on every screen of the feature.
- No diagnosis, no severity ratings, no Rx-drug suggestions.
- Directs users to a qualified healthcare professional and emergency line (123).

### 3.4 AISE Liability Shield — **BLOCKING**
- A signed Platform Service Agreement between AISE and Experts Pharmacy must be
  in place before go-live (Michael Gamal action). The agreement allocates
  pharmacy-practice liability to the licensed pharmacy, not AISE.

## 4. Data Handling Principles (PDPL)

- **Lawful basis:** explicit consent for health data (special category).
- **Minimization:** collect only what an order requires.
- **Retention:** define and document a retention schedule before go-live.
- **Security:** encryption in transit (TLS) and at rest; access controls by role.
- **Localization:** prefer in-country / compliant hosting for personal data.

## 5. Open Legal Items (tracked)

- [ ] Confirm EDA position on online OTC sale + delivery for the pilot.
- [ ] Controlled-substance exclusion list finalized with pharmacist.
- [x] Consent-withdrawal + data-deletion workflow (PDPL data-subject rights).
      Built: `GET/POST /auth/consent`, `/auth/consent/withdraw`, `/auth/export`,
      `DELETE /auth/account` (erasure = anonymize PII + block login; de-identified
      order records retained). **Retention schedule still to be signed off.**
- [ ] Retention schedule signed off by Legal (drives order/consent retention).
- [ ] Platform Service Agreement executed.

---
🌿 ✦ ASTRA INTELLIGENCE SERVICES ✦ 🌿 | ⚜ MISR ⚜
RxEgypt Pilot · RXEG-LEGAL-001 · Generated 2026-05-31
