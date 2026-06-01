from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from app.disclaimer import DISCLAIMER_AR, DISCLAIMER_EN
from app.i18n import Lang

TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "reports" / "templates"
STYLES = Path(__file__).resolve().parent.parent / "reports" / "styles.css"

PARTY_ROLE_LABELS_EN = {
    "PLAINTIFF": "Plaintiff",
    "DEFENDANT": "Defendant",
    "THIRD_PARTY": "Third Party",
}
PARTY_ROLE_LABELS_AR = {
    "PLAINTIFF": "المدعي",
    "DEFENDANT": "المدعى عليه",
    "THIRD_PARTY": "طرف ثالث",
}

_env = Environment(
    loader=FileSystemLoader(str(TEMPLATES_DIR)),
    autoescape=select_autoescape(["html", "j2"]),
)


def render_html(template_name: str, context: dict) -> str:
    template = _env.get_template(template_name)
    context = {
        **context,
        "disclaimer_en": DISCLAIMER_EN,
        "disclaimer_ar": DISCLAIMER_AR,
        "party_role_labels_en": PARTY_ROLE_LABELS_EN,
        "party_role_labels_ar": PARTY_ROLE_LABELS_AR,
    }
    return template.render(**context)


def html_to_pdf_bytes(html: str) -> bytes:
    # Imported lazily so tests that don't render PDFs don't pay for it
    from weasyprint import CSS, HTML

    css = CSS(filename=str(STYLES)) if STYLES.exists() else None
    return HTML(string=html, base_url=str(TEMPLATES_DIR)).write_pdf(stylesheets=[css] if css else None)


def render_report_pdf(report_payload: dict, lang: Lang) -> bytes:
    template = f"report.{lang.value}.html.j2"
    html = render_html(template, report_payload)
    return html_to_pdf_bytes(html)


def render_coaching_pdf(coaching_payload: dict, lang: Lang) -> bytes:
    template = f"coaching.{lang.value}.html.j2"
    html = render_html(template, coaching_payload)
    return html_to_pdf_bytes(html)
