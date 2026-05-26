DISCLAIMER_EN = (
    "AI Simulation Only — Not Legal Advice — All outputs require review by a "
    "qualified Egyptian lawyer."
)

DISCLAIMER_AR = (
    "محاكاة بالذكاء الاصطناعي فقط — ليست استشارة قانونية — "
    "جميع النتائج تتطلب مراجعة من محامٍ مصري مؤهل."
)


def disclaimer_block() -> dict[str, str]:
    return {"en": DISCLAIMER_EN, "ar": DISCLAIMER_AR}


SYSTEM_DISCLAIMER_PREFIX = (
    "IMPORTANT: This is an AI legal simulation for training purposes only. "
    "You are NOT providing legal advice. Always remind that outputs require "
    "review by a qualified Egyptian lawyer. Ground every legal claim in the "
    "Egyptian statute corpus provided.\n\n"
)
