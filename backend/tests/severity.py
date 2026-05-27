"""Severity-graduated scenario builders + edge-case fixtures.

Difficulty grid (1, 3, 5) is generated from the base SCENARIOS in scenarios.py:
- Level 1 — all facts undisputed, no missing evidence (clean case)
- Level 3 — one disputed key fact (the base fixtures already encode this)
- Level 5 — multi-issue: original facts + additional disputed facts + missing evidence

Edge cases are 5 named fixtures targeting specific stress points: missing evidence,
counterclaim, single disputed fact, multi-defendant, limitation-period borderline.
"""
from __future__ import annotations

import copy

from tests.scenarios import SCENARIOS


def _at_level(scenario_key: str, difficulty: int) -> dict:
    """Return a deep-copied fixture tweaked to the requested difficulty."""
    base = copy.deepcopy(SCENARIOS[scenario_key])
    if difficulty == 1:
        for f in base["facts"]:
            f["disputed"] = False
        for e in base["evidence"]:
            e["missing"] = False
    elif difficulty == 3:
        # Base fixtures already have a disputed fact — no change
        pass
    elif difficulty == 5:
        # Add additional disputed facts + mark some evidence missing
        base["facts"].extend([
            {
                "text_en": "Additional procedural complication: defendant raises forum-selection clause defense.",
                "text_ar": "تعقيد إجرائي إضافي: يحتج المدعى عليه بشرط اختصاص المحكمة.",
                "disputed": True,
                "order_index": len(base["facts"]),
            },
            {
                "text_en": "Damages quantification is contested; defendant disputes plaintiff's accounting.",
                "text_ar": "تحديد قيمة التعويض محل خلاف؛ يطعن المدعى عليه في حساب المدعي.",
                "disputed": True,
                "order_index": len(base["facts"]) + 1,
            },
        ])
        base["evidence"].append({
            "kind": "WITNESS",
            "title_en": "Independent expert valuation (NOT yet obtained)",
            "title_ar": "تقييم خبير مستقل (لم يتم الحصول عليه بعد)",
            "missing": True,
        })
        base["difficulty"] = 5
    base.setdefault("difficulty", difficulty)
    base["difficulty"] = difficulty
    return base


def difficulty_grid() -> dict[tuple[str, int], dict]:
    """7 areas × 3 difficulties = 21 fixtures."""
    return {
        (key, level): _at_level(key, level)
        for key in SCENARIOS
        for level in (1, 3, 5)
    }


EDGE_CASES = {
    "missing_evidence_dominant": {
        "title_en": "Sara Adel v. AlphaBank — fraudulent transfers (evidence largely missing)",
        "title_ar": "سارة عادل ضد ألفا بنك — تحويلات احتيالية (الأدلة مفقودة في معظمها)",
        "language_primary": "en",
        "area_of_law": "PRIVACY",
        "parties": [
            {"role": "PLAINTIFF", "kind": "NATURAL", "name_en": "Sara Adel", "name_ar": "سارة عادل"},
            {"role": "DEFENDANT", "kind": "LEGAL", "name_en": "AlphaBank Egypt", "name_ar": "ألفا بنك مصر"},
        ],
        "facts": [
            {"text_en": "Plaintiff reports unauthorized transfers of 500,000 EGP from her account.", "text_ar": "تفيد المدعية بتحويلات غير مصرح بها بمبلغ 500000 جنيه.", "disputed": False, "order_index": 0},
            {"text_en": "Bank claims the transfers were authorized via OTP.", "text_ar": "يدّعي البنك أن التحويلات تمت بترخيص OTP.", "disputed": True, "order_index": 1},
        ],
        "evidence": [
            {"kind": "DOCUMENT", "title_en": "Account statement", "title_ar": "كشف حساب", "missing": False},
            {"kind": "DOCUMENT", "title_en": "OTP / SMS audit trail", "title_ar": "سجل OTP والرسائل", "missing": True},
            {"kind": "DOCUMENT", "title_en": "Branch CCTV footage of disputed period", "title_ar": "تسجيلات كاميرات الفرع للفترة محل النزاع", "missing": True},
            {"kind": "WITNESS", "title_en": "Bank's IT-security officer testimony", "title_ar": "شهادة مسؤول أمن المعلومات بالبنك", "missing": True},
        ],
    },
    "counterclaim_driven": {
        "title_en": "MediaHouse v. FreelanceCo — counterclaim of nonpayment",
        "title_ar": "ميديا هاوس ضد فري لانس كو — دعوى مقابلة لعدم الدفع",
        "language_primary": "en",
        "area_of_law": "COMMERCIAL",
        "parties": [
            {"role": "PLAINTIFF", "kind": "LEGAL", "name_en": "MediaHouse LLC", "name_ar": "ميديا هاوس ش.م.م."},
            {"role": "DEFENDANT", "kind": "LEGAL", "name_en": "FreelanceCo", "name_ar": "فري لانس كو"},
        ],
        "facts": [
            {"text_en": "Plaintiff sues for breach of services contract.", "text_ar": "ترفع المدعية دعوى إخلال بعقد خدمات.", "disputed": False, "order_index": 0},
            {"text_en": "Defendant counterclaims plaintiff withheld 80,000 EGP in agreed payments.", "text_ar": "يدّعي المدعى عليه مقابلاً أن المدعية حجبت 80000 جنيه من المدفوعات المتفق عليها.", "disputed": True, "order_index": 1},
            {"text_en": "Both parties signed three written amendments.", "text_ar": "وقّع الطرفان ثلاثة تعديلات مكتوبة.", "disputed": False, "order_index": 2},
        ],
        "evidence": [
            {"kind": "DOCUMENT", "title_en": "Original contract + amendments", "title_ar": "العقد الأصلي والتعديلات", "missing": False},
            {"kind": "DOCUMENT", "title_en": "Invoices and remittance records", "title_ar": "الفواتير وسجلات التحويل", "missing": False},
        ],
    },
    "single_disputed_fact": {
        "title_en": "Mahmoud Fawzy v. NeighborCo — sole dispute over delivery date",
        "title_ar": "محمود فوزي ضد جوار كو — نزاع وحيد على تاريخ التسليم",
        "language_primary": "en",
        "area_of_law": "CIVIL",
        "parties": [
            {"role": "PLAINTIFF", "kind": "NATURAL", "name_en": "Mahmoud Fawzy", "name_ar": "محمود فوزي"},
            {"role": "DEFENDANT", "kind": "LEGAL", "name_en": "NeighborCo", "name_ar": "جوار كو"},
        ],
        "facts": [
            {"text_en": "Plaintiff ordered custom furniture; price 60,000 EGP paid in full.", "text_ar": "طلب المدعي أثاثاً مخصصاً؛ وسدد ثمنه كاملاً 60000 جنيه.", "disputed": False, "order_index": 0},
            {"text_en": "Defendant delivered the furniture; the date of delivery is contested.", "text_ar": "سلّم المدعى عليه الأثاث؛ تاريخ التسليم محل خلاف.", "disputed": True, "order_index": 1},
        ],
        "evidence": [
            {"kind": "DOCUMENT", "title_en": "Sales receipt", "title_ar": "إيصال البيع", "missing": False},
            {"kind": "DOCUMENT", "title_en": "Delivery note (date redacted)", "title_ar": "إذن التسليم (التاريخ مطموس)", "missing": False},
        ],
    },
    "multi_defendant": {
        "title_en": "OrangeCorp v. (Distributor + Manufacturer) — joint liability",
        "title_ar": "أورانج كورب ضد (الموزع + الشركة المصنعة) — مسؤولية تضامنية",
        "language_primary": "en",
        "area_of_law": "CONSUMER",
        "parties": [
            {"role": "PLAINTIFF", "kind": "LEGAL", "name_en": "OrangeCorp", "name_ar": "أورانج كورب"},
            {"role": "DEFENDANT", "kind": "LEGAL", "name_en": "DeltaDistribution", "name_ar": "دلتا للتوزيع"},
            {"role": "DEFENDANT", "kind": "LEGAL", "name_en": "PhoenixManufacturing", "name_ar": "فينيكس للتصنيع"},
        ],
        "facts": [
            {"text_en": "Plaintiff received defective batch causing 3M EGP in losses.", "text_ar": "تسلّمت المدعية دفعة معيبة تسببت في خسائر 3 مليون جنيه.", "disputed": False, "order_index": 0},
            {"text_en": "Distributor blames manufacturer; manufacturer blames distributor's storage conditions.", "text_ar": "الموزع يلوم المصنّعَ، والمصنّع يلوم ظروف تخزين الموزع.", "disputed": True, "order_index": 1},
        ],
        "evidence": [
            {"kind": "DOCUMENT", "title_en": "Purchase orders", "title_ar": "أوامر الشراء", "missing": False},
            {"kind": "PHYSICAL", "title_en": "Defective product samples", "title_ar": "عينات المنتج المعيب", "missing": False},
            {"kind": "WITNESS", "title_en": "Storage facility manager testimony", "title_ar": "شهادة مدير منشأة التخزين", "missing": True},
        ],
    },
    "limitation_borderline": {
        "title_en": "Yousef Khalil v. former employer — wage claim, limitation borderline",
        "title_ar": "يوسف خليل ضد صاحب العمل السابق — مطالبة بأجر، عند حافة التقادم",
        "language_primary": "en",
        "area_of_law": "LABOUR",
        "parties": [
            {"role": "PLAINTIFF", "kind": "NATURAL", "name_en": "Yousef Khalil", "name_ar": "يوسف خليل"},
            {"role": "DEFENDANT", "kind": "LEGAL", "name_en": "Construction Co.", "name_ar": "شركة المقاولات"},
        ],
        "facts": [
            {"text_en": "Plaintiff alleges unpaid overtime totalling 120,000 EGP across 2020-2021.", "text_ar": "يدّعي المدعي عدم سداد أجر إضافي يبلغ 120000 جنيه عن 2020-2021.", "disputed": False, "order_index": 0},
            {"text_en": "Plaintiff filed claim in late 2024, near the limitation boundary.", "text_ar": "رفع المدعي الدعوى أواخر 2024، قرب حافة التقادم.", "disputed": False, "order_index": 1},
            {"text_en": "Defendant raises limitation defense and disputes overtime hours.", "text_ar": "يدفع المدعى عليه بالتقادم ويطعن في ساعات العمل الإضافي.", "disputed": True, "order_index": 2},
        ],
        "evidence": [
            {"kind": "DOCUMENT", "title_en": "Time-keeping records 2020-2021", "title_ar": "سجلات الحضور 2020-2021", "missing": False},
            {"kind": "DOCUMENT", "title_en": "Plaintiff's filing receipt with date stamp", "title_ar": "إيصال الإيداع بختم التاريخ", "missing": False},
        ],
    },
}
