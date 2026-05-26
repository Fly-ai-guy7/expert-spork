from enum import Enum


class Lang(str, Enum):
    AR = "ar"
    EN = "en"


def pick(content_ar: str | None, content_en: str | None, lang: Lang) -> str:
    if lang == Lang.AR:
        return content_ar or content_en or ""
    return content_en or content_ar or ""
