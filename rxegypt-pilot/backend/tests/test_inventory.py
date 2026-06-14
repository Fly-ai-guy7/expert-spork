def _auth(token):
    return {"Authorization": f"Bearer {token}"}


def test_get_inventory(client):
    inv = client.get("/api/v1/inventory/1").json()
    assert inv["drug_id"] == 1 and inv["quantity"] == 50


def test_patient_cannot_update_inventory(client, patient_token):
    r = client.put("/api/v1/inventory/1", json={"quantity": 5},
                   headers=_auth(patient_token))
    assert r.status_code == 403


def test_pharmacist_updates_inventory_and_low_stock(client, pharmacist_token):
    r = client.put("/api/v1/inventory/1", json={"quantity": 3, "reorder_level": 10},
                   headers=_auth(pharmacist_token))
    assert r.status_code == 200 and r.json()["quantity"] == 3

    low = client.get("/api/v1/inventory/low-stock").json()
    item = next(i for i in low if i["drug_id"] == 1)
    # enriched with the drug name for reordering
    assert item["name_en"] == "Panadol"
    assert item["quantity"] == 3 and item["reorder_level"] == 10
