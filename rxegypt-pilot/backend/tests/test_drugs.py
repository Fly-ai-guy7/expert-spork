def test_health(client):
    assert client.get("/health").json()["status"] == "ok"


def test_search_by_name(client):
    drugs = client.get("/api/v1/drugs", params={"q": "panadol"}).json()
    assert len(drugs) == 1
    assert drugs[0]["name_en"] == "Panadol"


def test_filter_rx_only(client):
    rx = client.get("/api/v1/drugs", params={"rx": "true"}).json()
    assert [d["name_en"] for d in rx] == ["Augmentin"]


def test_barcode_lookup(client):
    d = client.get("/api/v1/drugs/barcode/6223000000027").json()
    assert d["name_en"] == "Augmentin" and d["rx"] is True


def test_barcode_not_found(client):
    assert client.get("/api/v1/drugs/barcode/0000000000000").status_code == 404
