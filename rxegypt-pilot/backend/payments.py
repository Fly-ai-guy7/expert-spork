"""Paymob (Egypt) payment integration.

If ``PAYMOB_API_KEY`` is unset the module runs in **MOCK mode**: it returns a
synthetic payment reference and no external calls are made, so the full
``pending_payment → paid`` lifecycle is testable without credentials. When the
key is present, the standard Paymob 3-step flow is used (auth → register order →
payment key) and the processed callback is HMAC-verified.

LIVE specifics (field names, HMAC field order) follow Paymob's documented
"Accept" API and MUST be re-validated against current Paymob docs before
go-live; only the MOCK path is exercised by the test suite.
"""
import hashlib
import hmac

import httpx

from config import get_settings

settings = get_settings()
PAYMOB_BASE = "https://accept.paymob.com/api"

# Ordered fields Paymob concatenates to compute the callback HMAC-SHA512.
_HMAC_FIELDS = [
    "amount_cents", "created_at", "currency", "error_occured",
    "has_parent_transaction", "id", "integration_id", "is_3d_secure",
    "is_auth", "is_capture", "is_refunded", "is_standalone_payment",
    "is_voided", "order.id", "owner", "pending", "source_data.pan",
    "source_data.sub_type", "source_data.type", "success",
]


def is_live() -> bool:
    return bool(settings.paymob_api_key)


def create_payment(order, user) -> dict:
    """Create a payment intent for an order. Returns a dict with a checkout_url,
    an opaque reference (stored on the order), and a ``mock`` flag.
    """
    if not is_live():
        return {
            "reference": f"mock-{order.id}",
            "checkout_url": "",   # frontend uses the mock-confirm flow instead
            "mock": True,
        }

    amount_cents = int(round(order.total_egp * 100))
    with httpx.Client(timeout=30) as client:
        token = client.post(
            f"{PAYMOB_BASE}/auth/tokens",
            json={"api_key": settings.paymob_api_key},
        ).json()["token"]

        pm_order = client.post(
            f"{PAYMOB_BASE}/ecommerce/orders",
            json={
                "auth_token": token,
                "delivery_needed": False,
                "amount_cents": amount_cents,
                "currency": "EGP",
                "merchant_order_id": str(order.id),
                "items": [],
            },
        ).json()

        name = (user.full_name or "NA").split(" ")
        billing = {
            "first_name": name[0] or "NA",
            "last_name": name[-1] if len(name) > 1 else "NA",
            "email": user.email,
            "phone_number": user.phone or "NA",
            "apartment": "NA", "floor": "NA", "street": "NA", "building": "NA",
            "shipping_method": "NA", "postal_code": "NA", "city": "NA",
            "country": "EG", "state": "NA",
        }
        payment_key = client.post(
            f"{PAYMOB_BASE}/acceptance/payment_keys",
            json={
                "auth_token": token,
                "amount_cents": amount_cents,
                "expiration": 3600,
                "order_id": pm_order["id"],
                "billing_data": billing,
                "currency": "EGP",
                "integration_id": int(settings.paymob_integration_id),
            },
        ).json()["token"]

    checkout_url = (
        f"{PAYMOB_BASE}/acceptance/iframes/{settings.paymob_iframe_id}"
        f"?payment_token={payment_key}"
    )
    return {"reference": str(pm_order["id"]), "checkout_url": checkout_url, "mock": False}


def verify_callback_hmac(obj: dict, received_hmac: str) -> bool:
    """Verify the HMAC-SHA512 Paymob sends with a processed-transaction callback."""
    if not settings.paymob_hmac_secret:
        return False

    def _get(path: str):
        cur = obj
        for part in path.split("."):
            cur = (cur or {}).get(part) if isinstance(cur, dict) else None
        return cur

    def _norm(v) -> str:
        if isinstance(v, bool):
            return "true" if v else "false"
        return "" if v is None else str(v)

    concatenated = "".join(_norm(_get(f)) for f in _HMAC_FIELDS)
    digest = hmac.new(
        settings.paymob_hmac_secret.encode(),
        concatenated.encode(),
        hashlib.sha512,
    ).hexdigest()
    return hmac.compare_digest(digest, received_hmac or "")
