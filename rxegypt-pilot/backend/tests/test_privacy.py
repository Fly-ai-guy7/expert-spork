"""PDPL data-subject rights: consent status/withdrawal, export, erasure."""


def _auth(token):
    return {"Authorization": f"Bearer {token}"}


def test_consent_status_defaults_to_not_granted(client, patient_token):
    r = client.get("/api/v1/auth/consent", headers=_auth(patient_token))
    assert r.status_code == 200 and r.json()["granted"] is False


def test_consent_grant_then_status_reflects_it(client, patient_token):
    client.post("/api/v1/auth/consent", json={"granted": True}, headers=_auth(patient_token))
    assert client.get("/api/v1/auth/consent", headers=_auth(patient_token)).json()["granted"] is True


def test_withdraw_consent_updates_status(client, patient_token):
    client.post("/api/v1/auth/consent", json={"granted": True}, headers=_auth(patient_token))
    r = client.post("/api/v1/auth/consent/withdraw", headers=_auth(patient_token))
    assert r.status_code == 201 and r.json()["granted"] is False
    assert client.get("/api/v1/auth/consent", headers=_auth(patient_token)).json()["granted"] is False


def test_export_returns_user_consents_and_orders(client, patient_token):
    client.post("/api/v1/auth/consent", json={"granted": True}, headers=_auth(patient_token))
    client.post("/api/v1/orders", json={"items": [{"drug_id": 1, "quantity": 1}]}, headers=_auth(patient_token))
    data = client.get("/api/v1/auth/export", headers=_auth(patient_token)).json()
    assert data["user"]["email"] == "pat@x.com"
    assert len(data["consents"]) >= 1
    assert len(data["orders"]) == 1


def test_export_requires_auth(client):
    assert client.get("/api/v1/auth/export").status_code == 401


def test_delete_account_blocks_login_and_token(client, session, patient_token):
    # token works before deletion
    assert client.get("/api/v1/auth/me", headers=_auth(patient_token)).status_code == 200
    r = client.delete("/api/v1/auth/account", headers=_auth(patient_token))
    assert r.status_code == 200 and "anonymized" in r.json()["detail"].lower()

    # existing token is now rejected
    assert client.get("/api/v1/auth/me", headers=_auth(patient_token)).status_code == 401
    # original credentials no longer work
    assert client.post("/api/v1/auth/login",
                       data={"username": "pat@x.com", "password": "password1"}).status_code == 401


def test_deleted_account_retains_anonymized_order(client, session, patient_token):
    from models import Order, User
    client.post("/api/v1/orders", json={"items": [{"drug_id": 1, "quantity": 1}]}, headers=_auth(patient_token))
    client.delete("/api/v1/auth/account", headers=_auth(patient_token))
    # order is retained but the user PII is scrubbed
    user = session.query(User).filter(User.email.like("deleted+%@rxegypt.invalid")).one()
    assert user.full_name == "" and user.phone == "" and user.deleted_at is not None
    assert session.query(Order).filter(Order.user_id == user.id).count() == 1
