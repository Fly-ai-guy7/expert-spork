# Disclaimer Policy

EQUALISE is an AI simulation tool for legal training. It is **not legal advice**. Every artifact
the system produces must carry the disclaimer:

> **English**: AI Simulation Only — Not Legal Advice — All outputs require review by a qualified Egyptian lawyer.
>
> **Arabic**: محاكاة بالذكاء الاصطناعي فقط — ليست استشارة قانونية — جميع النتائج تتطلب مراجعة من محامٍ مصري مؤهل.

## Where it appears

| Layer | Mechanism | File |
|---|---|---|
| LLM system prompts | Prefix on every agent's system message | `backend/app/disclaimer.py:SYSTEM_DISCLAIMER_PREFIX`, used in `agents/base.py:_system` |
| API responses | `disclaimer` field on key payloads | `backend/app/disclaimer.py:disclaimer_block`, used in `routers/cases.py:_report_payload` |
| PDF reports | Header banner on cover, `@page @bottom-center` on every page footer | `backend/app/reports/styles.css`, `backend/app/reports/templates/report.{ar,en}.html.j2` |
| Frontend | `DisclaimerBanner` sticky at top of every page | `frontend/src/components/DisclaimerBanner.tsx`, mounted in `frontend/src/App.tsx` |
| README | Top of file | `README.md` |
| LICENSE | Inline statement | `LICENSE` |

## Implementation rule

**The disclaimer must be non-removable.** If you find yourself writing code that lets a user
hide or disable it (a "dismiss" button, a CSS toggle, a config flag), stop and reconsider. The
banner is part of the product contract, not a UI preference.
