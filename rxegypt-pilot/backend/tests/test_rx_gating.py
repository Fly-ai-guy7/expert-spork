"""Rx drug gating — the core legal control. These tests must not regress."""


def _auth(token):
    return {"Authorization": f"Bearer {token}"}


def test_otc_order_goes_straight_to_payment(client, patient_token):
    r = client.post("/api/v1/orders",
                    json={"items": [{"drug_id": 1, "quantity": 2}]},
                    headers=_auth(patient_token))
    body = r.json()
    assert body["status"] == "pending_payment"
    assert body["requires_rx_verification"] is False
    assert body["total_egp"] == 40.0


def test_rx_order_is_gated(client, patient_token):
    r = client.post("/api/v1/orders",
                    json={"items": [{"drug_id": 2, "quantity": 1}]},
                    headers=_auth(patient_token))
    body = r.json()
    assert body["status"] == "pending_rx_verification"
    assert body["requires_rx_verification"] is True


def test_mixed_cart_is_gated(client, patient_token):
    r = client.post("/api/v1/orders",
                    json={"items": [{"drug_id": 1, "quantity": 1},
                                    {"drug_id": 2, "quantity": 1}]},
                    headers=_auth(patient_token))
    assert r.json()["status"] == "pending_rx_verification"


def test_patient_cannot_self_verify_rx(client, patient_token):
    order = client.post("/api/v1/orders",
                        json={"items": [{"drug_id": 2, "quantity": 1}]},
                        headers=_auth(patient_token)).json()
    r = client.post(f"/api/v1/orders/{order['id']}/verify-rx",
                    headers=_auth(patient_token))
    assert r.status_code == 403


def test_pharmacist_verifies_rx_order(client, patient_token, pharmacist_token):
    order = client.post("/api/v1/orders",
                        json={"items": [{"drug_id": 2, "quantity": 1}]},
                        headers=_auth(patient_token)).json()
    r = client.post(f"/api/v1/orders/{order['id']}/verify-rx",
                    headers=_auth(pharmacist_token))
    body = r.json()
    assert body["status"] == "pending_payment"
    assert body["rx_verified_by"] == "ph@x.com"


def test_whatsapp_link_only_for_rx_orders(client, patient_token):
    otc = client.post("/api/v1/orders",
                      json={"items": [{"drug_id": 1, "quantity": 1}]},
                      headers=_auth(patient_token)).json()
    r = client.get(f"/api/v1/orders/{otc['id']}/rx-whatsapp",
                   headers=_auth(patient_token))
    assert r.status_code == 400  # no Rx items

    rx = client.post("/api/v1/orders",
                     json={"items": [{"drug_id": 2, "quantity": 1}]},
                     headers=_auth(patient_token)).json()
    r2 = client.get(f"/api/v1/orders/{rx['id']}/rx-whatsapp",
                    headers=_auth(patient_token))
    assert r2.json()["whatsapp_url"].startswith("https://wa.me/")


def test_empty_order_rejected(client, patient_token):
    r = client.post("/api/v1/orders", json={"items": []},
                    headers=_auth(patient_token))
    assert r.status_code == 400


def test_my_orders_lists_only_own_orders(client, patient_token):
    client.post("/api/v1/orders", json={"items": [{"drug_id": 1, "quantity": 1}]},
                headers=_auth(patient_token))
    client.post("/api/v1/orders", json={"items": [{"drug_id": 2, "quantity": 1}]},
                headers=_auth(patient_token))
    mine = client.get("/api/v1/orders", headers=_auth(patient_token)).json()
    assert len(mine) == 2

    # a second patient sees none of the first's orders
    client.post("/api/v1/auth/register", json={"email": "other@x.com", "password": "password1"})
    other = client.post("/api/v1/auth/login",
                        data={"username": "other@x.com", "password": "password1"}).json()["access_token"]
    assert client.get("/api/v1/orders", headers=_auth(other)).json() == []


def test_my_orders_requires_auth(client):
    assert client.get("/api/v1/orders").status_code == 401
