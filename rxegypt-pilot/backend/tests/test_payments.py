"""Payment lifecycle (MOCK mode): pending_payment → paid → fulfilled."""


def _auth(token):
    return {"Authorization": f"Bearer {token}"}


def _otc_order(client, patient_token):
    return client.post("/api/v1/orders", json={"items": [{"drug_id": 1, "quantity": 1}]},
                       headers=_auth(patient_token)).json()


def _rx_order(client, patient_token):
    return client.post("/api/v1/orders", json={"items": [{"drug_id": 2, "quantity": 1}]},
                       headers=_auth(patient_token)).json()


def test_pay_returns_mock_intent_and_sets_reference(client, patient_token):
    order = _otc_order(client, patient_token)
    r = client.post(f"/api/v1/orders/{order['id']}/pay", headers=_auth(patient_token))
    body = r.json()
    assert r.status_code == 200
    assert body["mock"] is True
    assert body["reference"] == f"mock-{order['id']}"


def test_cannot_pay_order_awaiting_rx(client, patient_token):
    order = _rx_order(client, patient_token)  # pending_rx_verification
    r = client.post(f"/api/v1/orders/{order['id']}/pay", headers=_auth(patient_token))
    assert r.status_code == 400


def test_cannot_pay_someone_elses_order(client, patient_token):
    order = _otc_order(client, patient_token)
    client.post("/api/v1/auth/register", json={"email": "other@x.com", "password": "password1"})
    other = client.post("/api/v1/auth/login",
                        data={"username": "other@x.com", "password": "password1"}).json()["access_token"]
    assert client.post(f"/api/v1/orders/{order['id']}/pay", headers=_auth(other)).status_code == 404


def test_mock_confirm_marks_paid(client, patient_token):
    order = _otc_order(client, patient_token)
    client.post(f"/api/v1/orders/{order['id']}/pay", headers=_auth(patient_token))
    r = client.post("/api/v1/payments/mock/confirm",
                    json={"order_id": order["id"], "success": True}, headers=_auth(patient_token))
    assert r.json()["status"] == "paid"


def test_mock_confirm_failure_stays_pending(client, patient_token):
    order = _otc_order(client, patient_token)
    r = client.post("/api/v1/payments/mock/confirm",
                    json={"order_id": order["id"], "success": False}, headers=_auth(patient_token))
    assert r.json()["status"] == "pending_payment"


def test_cannot_pay_twice(client, patient_token):
    order = _otc_order(client, patient_token)
    client.post("/api/v1/payments/mock/confirm",
                json={"order_id": order["id"], "success": True}, headers=_auth(patient_token))
    # already paid → no longer payable
    assert client.post(f"/api/v1/orders/{order['id']}/pay", headers=_auth(patient_token)).status_code == 400


def test_paid_queue_lists_paid_orders(client, patient_token, pharmacist_token):
    order = _otc_order(client, patient_token)
    # not paid yet → absent from the fulfillment queue
    assert order["id"] not in [
        o["id"] for o in client.get("/api/v1/orders/paid", headers=_auth(pharmacist_token)).json()
    ]
    client.post("/api/v1/payments/mock/confirm",
                json={"order_id": order["id"], "success": True}, headers=_auth(patient_token))
    queue = client.get("/api/v1/orders/paid", headers=_auth(pharmacist_token)).json()
    assert order["id"] in [o["id"] for o in queue]


def test_paid_queue_requires_pharmacist(client, patient_token):
    assert client.get("/api/v1/orders/paid").status_code == 401
    assert client.get("/api/v1/orders/paid", headers=_auth(patient_token)).status_code == 403


def test_pharmacist_fulfills_paid_order_removed_from_queue(client, patient_token, pharmacist_token):
    order = _otc_order(client, patient_token)
    client.post("/api/v1/payments/mock/confirm",
                json={"order_id": order["id"], "success": True}, headers=_auth(patient_token))
    r = client.post(f"/api/v1/orders/{order['id']}/fulfill", headers=_auth(pharmacist_token))
    assert r.json()["status"] == "fulfilled"
    # fulfilled → no longer in the paid queue
    assert order["id"] not in [
        o["id"] for o in client.get("/api/v1/orders/paid", headers=_auth(pharmacist_token)).json()
    ]


def test_patient_cannot_fulfill(client, patient_token):
    order = _otc_order(client, patient_token)
    client.post("/api/v1/payments/mock/confirm",
                json={"order_id": order["id"], "success": True}, headers=_auth(patient_token))
    assert client.post(f"/api/v1/orders/{order['id']}/fulfill", headers=_auth(patient_token)).status_code == 403


def test_cannot_fulfill_unpaid_order(client, patient_token, pharmacist_token):
    order = _otc_order(client, patient_token)  # pending_payment, not paid
    assert client.post(f"/api/v1/orders/{order['id']}/fulfill", headers=_auth(pharmacist_token)).status_code == 400


def test_callback_hmac_verification(monkeypatch):
    """Exercise the live HMAC verifier (otherwise only used in live mode)."""
    import hashlib
    import hmac as _hmac

    import payments

    monkeypatch.setattr(payments.settings, "paymob_hmac_secret", "test-secret")
    obj = {
        "amount_cents": 9600, "created_at": "2026-06-01T00:00:00", "currency": "EGP",
        "error_occured": False, "has_parent_transaction": False, "id": 123,
        "integration_id": 99, "is_3d_secure": False, "is_auth": False,
        "is_capture": False, "is_refunded": False, "is_standalone_payment": True,
        "is_voided": False, "order": {"id": 555}, "owner": 7, "pending": False,
        "source_data": {"pan": "2345", "sub_type": "MasterCard", "type": "card"},
        "success": True,
    }

    def _norm(v):
        return ("true" if v else "false") if isinstance(v, bool) else ("" if v is None else str(v))

    concat = "".join(_norm(payments_get(obj, f)) for f in payments._HMAC_FIELDS)
    good = _hmac.new(b"test-secret", concat.encode(), hashlib.sha512).hexdigest()

    assert payments.verify_callback_hmac(obj, good) is True
    assert payments.verify_callback_hmac(obj, "deadbeef") is False


def payments_get(obj, path):
    cur = obj
    for part in path.split("."):
        cur = (cur or {}).get(part) if isinstance(cur, dict) else None
    return cur
