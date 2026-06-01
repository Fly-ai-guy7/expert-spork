"""Server-side legal guards on order creation (PDPL consent + controlled drugs)."""
from models import Drug, Inventory


def _auth(token):
    return {"Authorization": f"Bearer {token}"}


def _login_without_consent(client):
    client.post("/api/v1/auth/register",
                json={"email": "noconsent@x.com", "password": "password1"})
    return client.post("/api/v1/auth/login",
                       data={"username": "noconsent@x.com", "password": "password1"}).json()["access_token"]


def test_order_requires_server_side_consent(client):
    token = _login_without_consent(client)  # never granted consent
    r = client.post("/api/v1/orders", json={"items": [{"drug_id": 1, "quantity": 1}]},
                    headers=_auth(token))
    assert r.status_code == 403
    assert "consent" in r.json()["detail"].lower()


def test_order_allowed_after_consent(client):
    token = _login_without_consent(client)
    client.post("/api/v1/auth/consent", json={"granted": True}, headers=_auth(token))
    r = client.post("/api/v1/orders", json={"items": [{"drug_id": 1, "quantity": 1}]},
                    headers=_auth(token))
    assert r.status_code == 201


def test_withdrawn_consent_blocks_new_orders(client, patient_token):
    # patient_token starts consented; withdrawing must block subsequent orders
    client.post("/api/v1/auth/consent/withdraw", headers=_auth(patient_token))
    r = client.post("/api/v1/orders", json={"items": [{"drug_id": 1, "quantity": 1}]},
                    headers=_auth(patient_token))
    assert r.status_code == 403


def test_controlled_substance_not_orderable(client, session, patient_token):
    ctrl = Drug(name_en="Tramadol", name_ar="ترامادول", generic="Tramadol HCl",
                price_egp=35.0, rx=True, controlled=True)
    session.add(ctrl)
    session.flush()
    session.add(Inventory(drug_id=ctrl.id, quantity=10))
    session.commit()

    r = client.post("/api/v1/orders", json={"items": [{"drug_id": ctrl.id, "quantity": 1}]},
                    headers=_auth(patient_token))
    assert r.status_code == 400
    assert "controlled" in r.json()["detail"].lower()


def test_controlled_blocks_even_in_mixed_cart(client, session, patient_token):
    ctrl = Drug(name_en="Codeine", name_ar="كودايين", generic="Codeine",
                price_egp=20.0, rx=True, controlled=True)
    session.add(ctrl)
    session.flush()
    session.commit()
    r = client.post("/api/v1/orders",
                    json={"items": [{"drug_id": 1, "quantity": 1}, {"drug_id": ctrl.id, "quantity": 1}]},
                    headers=_auth(patient_token))
    assert r.status_code == 400
