"""Pharmacist Rx-verification queue — closes the Rx-gating loop."""


def _auth(token):
    return {"Authorization": f"Bearer {token}"}


def _place_rx_order(client, patient_token):
    return client.post("/api/v1/orders",
                       json={"items": [{"drug_id": 2, "quantity": 1}]},
                       headers=_auth(patient_token)).json()


def test_queue_requires_pharmacist(client, patient_token):
    assert client.get("/api/v1/orders/pending-rx").status_code == 401
    assert client.get("/api/v1/orders/pending-rx",
                      headers=_auth(patient_token)).status_code == 403


def test_queue_lists_pending_rx_with_detail(client, patient_token, pharmacist_token):
    order = _place_rx_order(client, patient_token)
    queue = client.get("/api/v1/orders/pending-rx", headers=_auth(pharmacist_token)).json()
    ids = [o["id"] for o in queue]
    assert order["id"] in ids
    entry = next(o for o in queue if o["id"] == order["id"])
    assert entry["patient_email"] == "pat@x.com"
    assert entry["items"][0]["name_en"] == "Augmentin"  # enriched with drug name
    assert entry["items"][0]["rx"] is True


def test_verify_removes_order_from_queue(client, patient_token, pharmacist_token):
    order = _place_rx_order(client, patient_token)
    client.post(f"/api/v1/orders/{order['id']}/verify-rx", headers=_auth(pharmacist_token))
    queue = client.get("/api/v1/orders/pending-rx", headers=_auth(pharmacist_token)).json()
    assert order["id"] not in [o["id"] for o in queue]


def test_reject_cancels_and_removes_from_queue(client, patient_token, pharmacist_token):
    order = _place_rx_order(client, patient_token)
    r = client.post(f"/api/v1/orders/{order['id']}/reject-rx", headers=_auth(pharmacist_token))
    assert r.json()["status"] == "cancelled"
    assert r.json()["rx_verified_by"] == "ph@x.com"
    queue = client.get("/api/v1/orders/pending-rx", headers=_auth(pharmacist_token)).json()
    assert order["id"] not in [o["id"] for o in queue]


def test_patient_cannot_reject(client, patient_token):
    order = _place_rx_order(client, patient_token)
    assert client.post(f"/api/v1/orders/{order['id']}/reject-rx",
                       headers=_auth(patient_token)).status_code == 403


def test_reject_only_from_pending_state(client, patient_token, pharmacist_token):
    order = _place_rx_order(client, patient_token)
    client.post(f"/api/v1/orders/{order['id']}/verify-rx", headers=_auth(pharmacist_token))
    # already verified -> no longer rejectable
    r = client.post(f"/api/v1/orders/{order['id']}/reject-rx", headers=_auth(pharmacist_token))
    assert r.status_code == 400
