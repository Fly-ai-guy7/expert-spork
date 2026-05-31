def test_register_and_login(client):
    r = client.post("/api/v1/auth/register",
                    json={"email": "new@x.com", "password": "password1"})
    assert r.status_code == 201
    tok = client.post("/api/v1/auth/login",
                      data={"username": "new@x.com", "password": "password1"})
    assert tok.status_code == 200 and tok.json()["access_token"]


def test_duplicate_email_rejected(client):
    client.post("/api/v1/auth/register",
                json={"email": "dup@x.com", "password": "password1"})
    r = client.post("/api/v1/auth/register",
                    json={"email": "dup@x.com", "password": "password1"})
    assert r.status_code == 400


def test_wrong_password_rejected(client):
    client.post("/api/v1/auth/register",
                json={"email": "a@x.com", "password": "password1"})
    r = client.post("/api/v1/auth/login",
                    data={"username": "a@x.com", "password": "wrongpass"})
    assert r.status_code == 401


def test_me_requires_auth(client):
    assert client.get("/api/v1/auth/me").status_code == 401


def test_consent_is_logged_with_timestamp(client, patient_token):
    h = {"Authorization": f"Bearer {patient_token}"}
    r = client.post("/api/v1/auth/consent", json={"granted": True}, headers=h)
    assert r.status_code == 201
    body = r.json()
    assert body["granted"] is True
    assert body["created_at"]  # server-side timestamp present
