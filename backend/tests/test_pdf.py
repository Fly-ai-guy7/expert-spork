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
