from app.i18n import Lang
from app.services.pdf_service import render_html


def test_render_html_english_includes_disclaimer():
    html = render_html(
        "report.en.html.j2",
        {
            "case": {"id": "abc", "title_en": "Test", "title_ar": None, "summary_en": "summary", "summary_ar": None, "parties": [], "area_of_law": "IP"},
            "prosecution_arguments": [],
            "defense_arguments": [],
            "trainee_arguments": [],
            "ruling": None,
            "outcome": None,
        },
    )
    assert "AI Simulation Only" in html
    assert "EQUALISE" in html


def test_render_html_arabic_uses_rtl():
    html = render_html(
        "report.ar.html.j2",
        {
            "case": {"id": "abc", "title_en": None, "title_ar": "اختبار", "summary_en": None, "summary_ar": "ملخص", "parties": [], "area_of_law": "IP"},
            "prosecution_arguments": [],
            "defense_arguments": [],
            "trainee_arguments": [],
            "ruling": None,
            "outcome": None,
        },
    )
    assert 'dir="rtl"' in html
    assert "محاكاة بالذكاء" in html


def test_pdf_generation_smoke():
    """Render a tiny PDF to ensure WeasyPrint is wired up."""
    from app.services.pdf_service import render_report_pdf

    pdf = render_report_pdf(
        {
            "case": {"id": "abc", "title_en": "Smoke", "title_ar": None, "summary_en": "x", "summary_ar": None, "parties": [], "area_of_law": "IP"},
            "prosecution_arguments": [],
            "defense_arguments": [],
            "trainee_arguments": [],
            "ruling": None,
            "outcome": None,
        },
        Lang.EN,
    )
    assert pdf.startswith(b"%PDF")


def test_coaching_pdf_smoke():
    """Render a coaching PDF with realistic per-round + missed-citations data."""
    from app.services.pdf_service import render_coaching_pdf

    pdf = render_coaching_pdf(
        {
            "grade": "B",
            "total_score": 72.0,
            "per_round": [
                {"round_no": 1, "factual": 80, "provable": 70, "unbiased": 75, "legal_law_based": 65, "overall": 72,
                 "rationale_en": "Solid factual base; thin on statute coverage."},
            ],
            "missed_citations": ["82/2002:115"],
            "evidence_gaps_to_address": ["proof of bad-faith adoption"],
            "weak_patterns": ["Insufficient statute citations — ground in Egyptian code"],
            "session": {"id": "s1", "trainee_role": "DEFENSE", "difficulty": 2, "user_id": "alice"},
            "case": {"id": "c1", "title_en": "Smoke", "title_ar": None, "area_of_law": "IP"},
        },
        Lang.EN,
    )
    assert pdf.startswith(b"%PDF")
