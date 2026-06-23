"""Template render smoke tests.

These run via Jinja's render_html — they don't import weasyprint, so they're
safe in the lightweight test environment. The point is to catch broken
template syntax / missing variable handling before it surfaces as a 500 in
the PDF endpoints.
"""
from app.services.pdf_service import render_html


def _full_ruling_payload() -> dict:
    return {
        "case": {
            "title_en": "Alpha v Beta",
            "title_ar": "ألفا ضد بيتا",
            "summary_en": "Trademark dispute.",
            "summary_ar": "نزاع علامة.",
            "language_primary": "en",
            "area_of_law": "IP",
            "parties": [
                {"role": "PLAINTIFF", "name_en": "Alpha", "name_ar": "ألفا"},
                {"role": "DEFENDANT", "name_en": "Beta", "name_ar": "بيتا"},
            ],
        },
        "prosecution_arguments": [],
        "defense_arguments": [],
        "trainee_arguments": [],
        "ruling": {
            "plaintiff_success_prob": 62.0,
            "text_en": "Plaintiff prevails on the merits.",
            "text_ar": "الحكم للمدعي.",
            "critical_evidence_gaps": ["proof of bad faith"],
            "precedent_refs": ["Cassation 1234/2019"],
            "override_applied": True,
            "council_size": 3,
            "council_vote": {"for_plaintiff": 2, "for_defendant": 1},
            "dissent_en": "[deepseek] dissent reasoning",
            "dissent_ar": "حيثيات المخالف",
            "council_verdicts": [
                {"member_llm": "claude-opus", "verdict": "FOR_PLAINTIFF",
                 "plaintiff_success_prob": 70, "override_flagged": True,
                 "reasoning_en": "a", "reasoning_ar": "أ"},
                {"member_llm": "deepseek", "verdict": "FOR_DEFENDANT",
                 "plaintiff_success_prob": 30, "override_flagged": False,
                 "reasoning_en": "c", "reasoning_ar": "ج"},
            ],
        },
        "outcome": {
            "projected_prob": 62.0, "risk_score": 76.0,
            "pretrial_resolution_en": "Settlement recommended",
            "pretrial_resolution_ar": "يُنصح بالتسوية",
        },
    }


def _full_coaching_payload() -> dict:
    return {
        "grade": "B",
        "total_score": 72.0,
        "per_round": [{
            "round_no": 1, "factual": 80, "provable": 70, "unbiased": 75,
            "legal_law_based": 65, "overall": 72,
            "rationale_en": "Solid grounding.",
            "rationale_ar": "أساس جيد.",
        }],
        "missed_citations": ["82/2002:113"],
        "evidence_gaps_to_address": ["proof of bad faith"],
        "weak_patterns": ["weak citations"],
        "counsel_calls_count": 2,
        "council_alignment": "LOST",
        "council_for_trainee": 1,
        "council_against_trainee": 2,
        "council_supporters": ["claude-opus"],
        "council_dissenters": ["deepseek", "claude-sonnet"],
        "counsel_log": [{
            "created_at": "2026-06-22T10:00:00Z",
            "trainee_role": "DEFENSE",
            "draft_en": "Prior use since 2019.",
            "draft_ar": "استخدام سابق منذ 2019.",
            "citations": ["82/2002:115"],
            "advice": {
                "strategy_en": "Lead with prior use.",
                "strategy_ar": "ابدأ بالاستخدام السابق.",
                "suggested_citations": ["82/2002:115"],
                "missing_arguments": ["limitation period"],
                "strengths": [],
                "risks": [],
            },
        }],
    }


def test_ruling_en_template_renders_council_panel():
    html = render_html("report.en.html.j2", _full_ruling_payload())
    assert "Judicial council" in html
    assert "Council Verdicts" in html
    assert "claude-opus" in html and "deepseek" in html
    assert "Dissent" in html


def test_ruling_ar_template_renders_council_panel():
    html = render_html("report.ar.html.j2", _full_ruling_payload())
    assert "الهيئة القضائية" in html
    assert "أحكام أعضاء الهيئة" in html
    assert "claude-opus" in html
    assert "الرأي المخالف" in html


def test_ruling_templates_handle_missing_ruling():
    payload = _full_ruling_payload()
    payload["ruling"] = None
    for tmpl in ("report.en.html.j2", "report.ar.html.j2"):
        html = render_html(tmpl, payload)
        assert "No ruling produced" in html or "لم يصدر حكم" in html


def test_coaching_en_template_renders_alignment_and_log():
    html = render_html("coaching.en.html.j2", _full_coaching_payload())
    assert "Judicial Council Alignment" in html
    assert "AGAINST" in html  # LOST → AGAINST
    assert "claude-opus" in html
    assert "Advisory Counsel calls: 2" in html
    assert "Retrospective" in html
    assert "Lead with prior use" in html


def test_coaching_ar_template_renders_alignment_and_log():
    html = render_html("coaching.ar.html.j2", _full_coaching_payload())
    assert "موقف الهيئة القضائية" in html
    assert "ضد" in html
    assert "claude-opus" in html
    assert "سجل استشارات" in html
    assert "الاستخدام السابق" in html


def test_coaching_templates_handle_empty_session():
    empty = {
        "grade": None,
        "total_score": 0,
        "per_round": [],
        "missed_citations": [],
        "evidence_gaps_to_address": [],
        "weak_patterns": [],
        "counsel_calls_count": None,
    }
    for tmpl in ("coaching.en.html.j2", "coaching.ar.html.j2"):
        render_html(tmpl, empty)  # must not raise
