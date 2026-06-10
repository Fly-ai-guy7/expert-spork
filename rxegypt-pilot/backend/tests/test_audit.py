"""Audit trail of sensitive actions (admin-readable)."""


def _auth(token):
    return {"Authorization": f"Bearer {token}"}


def test_audit_requires_admin(client, patient_token, pharmacist_token):
    assert client.get("/api/v1/audit").status_code == 401
    assert client.get("/api/v1/audit", headers=_auth(patient_token)).status_code == 403
    # pharmacist is not admin
    assert client.get("/api/v1/audit", headers=_auth(pharmacist_token)).status_code == 403


def test_rx_verify_is_audited(client, patient_token, pharmacist_token, admin_token):
    order = client.post("/api/v1/orders", json={"items": [{"drug_id": 2, "quantity": 1}]},
                        headers=_auth(patient_token)).json()
    client.post(f"/api/v1/orders/{order['id']}/verify-rx", headers=_auth(pharmacist_token))

    entries = client.get("/api/v1/audit", params={"action": "rx_verified"},
                         headers=_auth(admin_token)).json()
    assert any(e["target"] == f"order:{order['id']}" and e["actor_email"] == "ph@x.com"
               for e in entries)


def test_inventory_change_is_audited(client, pharmacist_token, admin_token):
    client.put("/api/v1/inventory/1", json={"quantity": 7}, headers=_auth(pharmacist_token))
    entries = client.get("/api/v1/audit", params={"action": "inventory_set"},
                         headers=_auth(admin_token)).json()
    assert any(e["target"] == "drug:1" and "qty=7" in e["detail"] for e in entries)


def test_consent_and_withdrawal_are_audited(client, patient_token, admin_token):
    # patient_token already granted consent in the fixture
    client.post("/api/v1/auth/consent/withdraw", headers=_auth(patient_token))
    actions = {e["action"] for e in client.get("/api/v1/audit", headers=_auth(admin_token)).json()}
    assert "consent_granted" in actions
    assert "consent_withdrawn" in actions


def test_audit_newest_first(client, pharmacist_token, admin_token):
    client.put("/api/v1/inventory/1", json={"quantity": 1}, headers=_auth(pharmacist_token))
    client.put("/api/v1/inventory/2", json={"quantity": 2}, headers=_auth(pharmacist_token))
    entries = client.get("/api/v1/audit", headers=_auth(admin_token)).json()
    assert len(entries) >= 2
    # newest first
    assert entries[0]["id"] > entries[1]["id"]


def test_admin_metrics_requires_admin(client, patient_token):
    assert client.get("/api/v1/admin/metrics").status_code == 401
    assert client.get("/api/v1/admin/metrics", headers=_auth(patient_token)).status_code == 403


def test_admin_metrics_counts_orders(client, patient_token, admin_token):
    client.post("/api/v1/orders", json={"items": [{"drug_id": 1, "quantity": 1}]},
                headers=_auth(patient_token))  # OTC -> pending_payment
    client.post("/api/v1/orders", json={"items": [{"drug_id": 2, "quantity": 1}]},
                headers=_auth(patient_token))  # Rx -> pending_rx_verification
    m = client.get("/api/v1/admin/metrics", headers=_auth(admin_token)).json()
    assert m["total_orders"] == 2
    assert m["orders_by_status"]["pending_payment"] == 1
    assert m["orders_by_status"]["pending_rx_verification"] == 1
    assert m["active_patients"] >= 1
