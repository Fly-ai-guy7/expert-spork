"""Canonical case fixtures, one per area of law, used by the scenario tests.

Each fixture is a fully-formed `CaseIn`-compatible dict that the orchestrator
can run end-to-end against the MockLLMClient.
"""

SCENARIOS = {
    "ip": {
        "title_en": "Alpha Tech v. Beta Corp — trademark infringement",
        "title_ar": "ألفا تك ضد بيتا كورب — انتهاك علامة تجارية",
        "language_primary": "en",
        "area_of_law": "IP",
        "parties": [
            {"role": "PLAINTIFF", "kind": "LEGAL", "name_en": "Alpha Tech LLC", "name_ar": "ألفا تك ش.م.م."},
            {"role": "DEFENDANT", "kind": "LEGAL", "name_en": "Beta Corp", "name_ar": "بيتا كورب"},
        ],
        "facts": [
            {"text_en": "Plaintiff registered the mark ALPHA-T in Egypt on 2021-03-15.", "text_ar": "سجّل المدعي علامة ألفا-ت في 15/03/2021.", "disputed": False, "order_index": 0},
            {"text_en": "Defendant began selling ALPHATEK-branded routers in Cairo in 2024.", "text_ar": "بدأ المدعى عليه بيع موجهات بعلامة ألفاتك في 2024.", "disputed": False, "order_index": 1},
            {"text_en": "Defendant claims independent prior use since 2019.", "text_ar": "يدّعي المدعى عليه استخداماً مستقلاً سابقاً منذ 2019.", "disputed": True, "order_index": 2},
        ],
        "evidence": [
            {"kind": "DOCUMENT", "title_en": "Trademark registration certificate 2021", "title_ar": "شهادة تسجيل العلامة 2021", "missing": False},
            {"kind": "DOCUMENT", "title_en": "Defendant sales invoices 2024", "title_ar": "فواتير مبيعات المدعى عليه 2024", "missing": False},
        ],
    },
    "labour": {
        "title_en": "Mohamed Ali v. Nile Logistics — arbitrary dismissal",
        "title_ar": "محمد علي ضد لوجستيات النيل — فصل تعسفي",
        "language_primary": "en",
        "area_of_law": "LABOUR",
        "parties": [
            {"role": "PLAINTIFF", "kind": "NATURAL", "name_en": "Mohamed Ali", "name_ar": "محمد علي"},
            {"role": "DEFENDANT", "kind": "LEGAL", "name_en": "Nile Logistics SAE", "name_ar": "لوجستيات النيل ش.م.م."},
        ],
        "facts": [
            {"text_en": "Plaintiff worked for defendant for 7 years as logistics manager.", "text_ar": "عمل المدعي لدى المدعى عليه سبع سنوات كمدير لوجستيات.", "disputed": False, "order_index": 0},
            {"text_en": "On 2024-09-12 plaintiff was dismissed via WhatsApp, no written notice.", "text_ar": "في 12/09/2024 فُصل المدعي عبر واتساب، دون إنذار كتابي.", "disputed": False, "order_index": 1},
            {"text_en": "Defendant alleges serious fault — repeated unauthorized absences.", "text_ar": "يدّعي المدعى عليه خطأ جسيماً — غياب متكرر غير مبرر.", "disputed": True, "order_index": 2},
        ],
        "evidence": [
            {"kind": "DOCUMENT", "title_en": "Employment contract 2017", "title_ar": "عقد العمل 2017", "missing": False},
            {"kind": "DOCUMENT", "title_en": "WhatsApp dismissal message screenshot", "title_ar": "لقطة شاشة رسالة الفصل عبر واتساب", "missing": False},
            {"kind": "WITNESS", "title_en": "HR director testimony on attendance records", "title_ar": "شهادة مدير الموارد البشرية بشأن سجل الحضور", "missing": True},
        ],
    },
    "commercial": {
        "title_en": "Cairo Foods v. SwiftPay — breach of supply contract",
        "title_ar": "القاهرة للأغذية ضد سويفت باي — إخلال بعقد توريد",
        "language_primary": "en",
        "area_of_law": "COMMERCIAL",
        "parties": [
            {"role": "PLAINTIFF", "kind": "LEGAL", "name_en": "Cairo Foods LLC", "name_ar": "القاهرة للأغذية ش.م.م."},
            {"role": "DEFENDANT", "kind": "LEGAL", "name_en": "SwiftPay Egypt", "name_ar": "سويفت باي مصر"},
        ],
        "facts": [
            {"text_en": "Parties signed a 12-month supply contract on 2023-01-10.", "text_ar": "وقّع الطرفان عقد توريد لمدة 12 شهراً في 10/01/2023.", "disputed": False, "order_index": 0},
            {"text_en": "Defendant failed to deliver three consecutive monthly shipments.", "text_ar": "أخفق المدعى عليه في تسليم ثلاث شحنات شهرية متتالية.", "disputed": False, "order_index": 1},
            {"text_en": "Defendant invokes force majeure due to Red Sea shipping disruptions.", "text_ar": "يحتج المدعى عليه بالقوة القاهرة بسبب اضطرابات الشحن في البحر الأحمر.", "disputed": True, "order_index": 2},
        ],
        "evidence": [
            {"kind": "DOCUMENT", "title_en": "Supply contract", "title_ar": "عقد التوريد", "missing": False},
            {"kind": "DOCUMENT", "title_en": "Shipping records 2024", "title_ar": "سجلات الشحن 2024", "missing": False},
        ],
    },
    "consumer": {
        "title_en": "Heba Khaled v. ZenMobile — defective device",
        "title_ar": "هبة خالد ضد زن موبايل — منتج معيب",
        "language_primary": "en",
        "area_of_law": "CONSUMER",
        "parties": [
            {"role": "PLAINTIFF", "kind": "NATURAL", "name_en": "Heba Khaled", "name_ar": "هبة خالد"},
            {"role": "DEFENDANT", "kind": "LEGAL", "name_en": "ZenMobile Retail", "name_ar": "زن موبايل للتجزئة"},
        ],
        "facts": [
            {"text_en": "Plaintiff purchased a smartphone on 2025-01-15 for 25,000 EGP.", "text_ar": "اشترت المدعية هاتفاً في 15/01/2025 بمبلغ 25000 جنيه.", "disputed": False, "order_index": 0},
            {"text_en": "Device became unusable after 10 days; plaintiff sought refund within 14-day window.", "text_ar": "أصبح الجهاز غير قابل للاستخدام بعد 10 أيام؛ طلبت المدعية الاسترداد ضمن نافذة 14 يوماً.", "disputed": False, "order_index": 1},
            {"text_en": "Defendant refused, citing 'user damage'.", "text_ar": "رفض المدعى عليه مدّعياً 'إساءة استخدام'.", "disputed": True, "order_index": 2},
        ],
        "evidence": [
            {"kind": "DOCUMENT", "title_en": "Purchase receipt", "title_ar": "إيصال الشراء", "missing": False},
            {"kind": "PHYSICAL", "title_en": "Defective device", "title_ar": "الجهاز المعيب", "missing": False},
        ],
    },
    "privacy": {
        "title_en": "Ahmed Said v. DataLeak Co — personal data breach",
        "title_ar": "أحمد سعيد ضد داتا ليك — اختراق بيانات شخصية",
        "language_primary": "en",
        "area_of_law": "PRIVACY",
        "parties": [
            {"role": "PLAINTIFF", "kind": "NATURAL", "name_en": "Ahmed Said", "name_ar": "أحمد سعيد"},
            {"role": "DEFENDANT", "kind": "LEGAL", "name_en": "DataLeak Co", "name_ar": "شركة داتا ليك"},
        ],
        "facts": [
            {"text_en": "Defendant suffered a data breach on 2024-11-03 exposing plaintiff's national ID and financial data.", "text_ar": "تعرض المدعى عليه لاختراق بيانات في 03/11/2024 كشف بطاقة المدعي وبياناته المالية.", "disputed": False, "order_index": 0},
            {"text_en": "Defendant notified the Center on 2024-11-09, six days after discovery.", "text_ar": "أخطر المدعى عليه المركز في 09/11/2024، بعد ستة أيام من الاكتشاف.", "disputed": False, "order_index": 1},
            {"text_en": "Plaintiff alleges identity fraud loss of 80,000 EGP.", "text_ar": "يدّعي المدعي خسارة من احتيال هوية بمبلغ 80000 جنيه.", "disputed": True, "order_index": 2},
        ],
        "evidence": [
            {"kind": "DOCUMENT", "title_en": "Breach notification letter", "title_ar": "خطاب الإخطار بالاختراق", "missing": False},
        ],
    },
    "corporate": {
        "title_en": "Minority shareholders v. NorthBay Holdings — board misconduct",
        "title_ar": "مساهمو الأقلية ضد قابضة نورث باي — سوء إدارة مجلس",
        "language_primary": "en",
        "area_of_law": "CORPORATE",
        "parties": [
            {"role": "PLAINTIFF", "kind": "NATURAL", "name_en": "Group of minority shareholders (7%)", "name_ar": "مجموعة مساهمي الأقلية (7%)"},
            {"role": "DEFENDANT", "kind": "LEGAL", "name_en": "NorthBay Holdings JSC", "name_ar": "قابضة نورث باي ش.م.م."},
        ],
        "facts": [
            {"text_en": "Board approved a related-party transaction transferring 12M EGP to a director's affiliate without shareholder vote.", "text_ar": "وافق مجلس الإدارة على معاملة ذات صلة بتحويل 12 مليون جنيه لشركة تابعة لأحد الأعضاء دون تصويت المساهمين.", "disputed": False, "order_index": 0},
            {"text_en": "Plaintiffs request judicial investigation under Companies Law.", "text_ar": "يطلب المدعون التحقيق القضائي بموجب قانون الشركات.", "disputed": False, "order_index": 1},
            {"text_en": "Defendants claim the transaction was at fair market value.", "text_ar": "يدّعي المدعى عليهم أن المعاملة جرت بقيمة سوقية عادلة.", "disputed": True, "order_index": 2},
        ],
        "evidence": [
            {"kind": "DOCUMENT", "title_en": "Board meeting minutes", "title_ar": "محضر اجتماع المجلس", "missing": False},
            {"kind": "DOCUMENT", "title_en": "Independent valuation report", "title_ar": "تقرير تقييم مستقل", "missing": True},
        ],
    },
    "civil": {
        "title_en": "Tarek Hassan v. Karim Fouad — breach of contract & damages",
        "title_ar": "طارق حسن ضد كريم فؤاد — إخلال بعقد وتعويض",
        "language_primary": "en",
        "area_of_law": "CIVIL",
        "parties": [
            {"role": "PLAINTIFF", "kind": "NATURAL", "name_en": "Tarek Hassan", "name_ar": "طارق حسن"},
            {"role": "DEFENDANT", "kind": "NATURAL", "name_en": "Karim Fouad", "name_ar": "كريم فؤاد"},
        ],
        "facts": [
            {"text_en": "Parties signed a private services agreement on 2022-06-01.", "text_ar": "وقّع الطرفان عقد خدمات خاص في 01/06/2022.", "disputed": False, "order_index": 0},
            {"text_en": "Defendant failed to perform after receiving advance payment of 150,000 EGP.", "text_ar": "أخفق المدعى عليه في الأداء بعد تلقي دفعة مقدمة بمبلغ 150000 جنيه.", "disputed": False, "order_index": 1},
        ],
        "evidence": [
            {"kind": "DOCUMENT", "title_en": "Services agreement", "title_ar": "عقد الخدمات", "missing": False},
            {"kind": "DOCUMENT", "title_en": "Bank transfer receipt", "title_ar": "إيصال التحويل المصرفي", "missing": False},
        ],
    },
}
