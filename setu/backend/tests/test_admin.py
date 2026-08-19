"""Admin endpoint tests (Phase 8)."""


def test_admin_requires_dev(client):
    r = client.get("/api/v1/admin/surveys")
    assert r.status_code == 403


def test_admin_surveys_and_stats(client):
    headers = {"X-Dev-Key": "test-dev-key"}
    # seed
    client.post(
        "/api/v1/sync/upload",
        json={
            "surveys": [
                {
                    "user": {
                        "full_name": "Admin Test",
                        "father_name": "F",
                        "mobile_number": "9000000000",
                        "aadhaar_number": "333333333333",
                    },
                    "village": "V",
                    "district": "Kamrup",
                    "post_office": "PO",
                    "police_station": "PS",
                    "pin_code": "781001",
                    "disaster_type": "Flood",
                    "damage_date": "2026-08-13",
                    "damage_area": "House",
                    "casualties": [
                        {
                            "person_name": "C1",
                            "age": 10,
                            "gender": "Male",
                            "status": "Alive",
                            "current_location": "V",
                        }
                    ],
                }
            ]
        },
    )
    r = client.get("/api/v1/admin/surveys", headers=headers)
    assert r.status_code == 200
    assert r.json()["count"] >= 1

    stats = client.get("/api/v1/admin/stats", headers=headers)
    assert stats.status_code == 200
    assert stats.json()["surveys"] >= 1

    audit = client.get("/api/v1/admin/audit", headers=headers)
    assert audit.status_code == 200
    assert "exports" in audit.json()
