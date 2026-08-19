"""Auth + export gating tests (Phases 6, 7)."""
import io
import csv


def test_login_wrong_key(client):
    r = client.post("/api/v1/auth/login", json={"api_key": "wrong"})
    assert r.status_code == 401


def test_login_ok_returns_token(client):
    r = client.post("/api/v1/auth/login", json={"api_key": "test-dev-key"})
    assert r.status_code == 200
    body = r.json()
    assert body["token"]
    assert body["role"] == "admin"


def test_export_requires_dev(client):
    r = client.get("/api/v1/export/verified")
    assert r.status_code == 403


def test_export_with_dev_key(client):
    # seed a synced survey first
    client.post(
        "/api/v1/sync/upload",
        json={
            "surveys": [
                {
                    "user": {
                        "full_name": "Export Test",
                        "father_name": "Father",
                        "mobile_number": "9123456789",
                        "aadhaar_number": "222222222222",
                    },
                    "village": "V",
                    "district": "D",
                    "post_office": "PO",
                    "police_station": "PS",
                    "pin_code": "781001",
                    "disaster_type": "Flood",
                    "damage_date": "2026-08-12",
                    "damage_area": "House",
                    "casualties": [
                        {
                            "person_name": "Person One",
                            "age": 30,
                            "gender": "Female",
                            "status": "Missing",
                            "current_location": "Elsewhere",
                        }
                    ],
                }
            ]
        },
    )
    r = client.get("/api/v1/export/verified", headers={"X-Dev-Key": "test-dev-key"})
    assert r.status_code == 200
    assert r.headers["content-disposition"].startswith("attachment")
    text = r.text
    reader = csv.reader(io.StringIO(text))
    rows = list(reader)
    # header + at least one data row
    assert len(rows) >= 2
    assert "aadhaar_masked" in rows[0] or "XXXX-XXXX-" in text
    # raw Aadhaar must never appear in export
    assert "222222222222" not in text
