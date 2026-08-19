"""Sync + dedupe tests (Phases 3, 4, 5)."""


def _survey(
    aadhaar="123456789012",
    damage_date="2026-08-15",
    village="Village A",
    mobile="9876543210",
):
    return {
        "user": {
            "full_name": "Shubh",
            "father_name": "Sample Father",
            "mobile_number": mobile,
            "aadhaar_number": aadhaar,
        },
        "village": village,
        "district": "Barpeta",
        "post_office": "PO",
        "police_station": "PS",
        "pin_code": "781001",
        "disaster_type": "Flood",
        "damage_date": damage_date,
        "damage_area": "House",
        "casualties": [
            {
                "person_name": "Shubh",
                "age": 20,
                "gender": "Male",
                "status": "Alive",
                "current_location": "Village A",
            }
        ],
        "relief_camp": {
            "staying_in_camp": True,
            "camp_name": "ABC Camp",
            "camp_location": "XYZ",
            "camp_address": None,
            "nearest_landmark": "School",
        },
        "images": [{"image_url": "img_001.jpg"}],
    }


def test_upload_accepted(client):
    resp = client.post("/api/v1/sync/upload", json={"surveys": [_survey()]})
    assert resp.status_code == 200
    body = resp.json()
    assert body["accepted"] == 1
    assert body["duplicates"] == 0
    assert body["rejected"] == 0
    assert body["rejectedDetails"][0]["outcome"] == "accepted"


def test_upload_duplicate(client):
    dup = _survey(aadhaar="444444444444", mobile="9444444444")  # same aadhaar + same date
    payload = {"surveys": [dup, dup]}
    resp = client.post("/api/v1/sync/upload", json=payload)
    assert resp.status_code == 200
    body = resp.json()
    assert body["accepted"] == 1
    assert body["duplicates"] == 1
    assert body["rejectedDetails"][1]["outcome"] == "duplicate"


def test_upload_invalid_mobile_is_rejected(client):
    bad = _survey()
    bad["user"]["mobile_number"] = "123"  # not 10 digits
    resp = client.post("/api/v1/sync/upload", json={"surveys": [bad]})
    assert resp.status_code == 422  # pydantic validation


def test_upload_invalid_status_is_rejected(client):
    bad = _survey()
    bad["casualties"][0]["status"] = "Zombie"  # not in {Alive,Missing,Not Alive}
    resp = client.post("/api/v1/sync/upload", json={"surveys": [bad]})
    assert resp.status_code == 422


def test_download_full_and_delta(client):
    client.post(
        "/api/v1/sync/upload",
        json={
            "surveys": [
                _survey(
                    aadhaar="111111111111",
                    damage_date="2026-08-10",
                    village="Village B",
                    mobile="9111111111",
                )
            ]
        },
    )
    # full pull (no cursor)
    r1 = client.get("/api/v1/sync/download")
    assert r1.status_code == 200
    b1 = r1.json()
    assert b1["nextCursor"] is not None
    assert len(b1["surveys"]) >= 1
    # Aadhaar is masked in the download payload
    assert "XXXX-XXXX-" in b1["surveys"][0]["user"]["aadhaar_masked"]

    # delta pull: nothing newer than the cursor
    r2 = client.get("/api/v1/sync/download", params={"since": b1["nextCursor"]})
    assert r2.status_code == 200
    assert r2.json()["surveys"] == []


def test_download_invalid_cursor(client):
    r = client.get("/api/v1/sync/download", params={"since": "not-a-date"})
    assert r.status_code == 400
