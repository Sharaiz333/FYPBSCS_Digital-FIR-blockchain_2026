"""Complaint -> review -> FIR -> assignment -> investigation -> closure."""
import re
from datetime import datetime, timedelta, timezone

import pytest
from sqlmodel import Session

from app.core.database import engine
from app.core.security import hash_password
from app.models.enums import RoleName
from app.models.user import User

YEAR = datetime.now(timezone.utc).year


def _make_user(username: str, role: RoleName, **extra) -> str:
    with Session(engine) as s:
        user = User(full_name=username.replace("_", " ").title(), username=username,
                    password_hash=hash_password("Pass12345"), role=role, **extra)
        s.add(user)
        s.commit()
        s.refresh(user)
        return user.user_id


def _auth(client, username: str) -> dict:
    r = client.post("/auth/login", json={"username": username, "password": "Pass12345"})
    assert r.status_code == 200, r.text
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


def _complaint_body(station_id: str, **overrides) -> dict:
    body = {
        "station_id": station_id,
        "crime_category": "Theft",
        "incident_date": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat(),
        "incident_location": "Main Market, Saddar",
        "description": "My bicycle was stolen from outside the shop while I was inside.",
        "complainant_name": "Ali Khan",
        "complainant_cnic": "12345-1234567-1",
        "complainant_phone": "0300-1234567",
    }
    body.update(overrides)
    return body


@pytest.fixture(scope="module")
def world(client):
    ids = {
        "admin": _make_user("admin", RoleName.ADMIN),
        "citizen": _make_user("citizen_a", RoleName.CITIZEN),
        "citizen2": _make_user("citizen_b", RoleName.CITIZEN),
        "officer": _make_user("officer", RoleName.POLICE_OFFICER),
        "supervisor": _make_user("supervisor", RoleName.SUPERVISORY_OFFICER),
        "io": _make_user("io_one", RoleName.INVESTIGATING_OFFICER),
        "io2": _make_user("io_two", RoleName.INVESTIGATING_OFFICER),
        "auditor": _make_user("auditor", RoleName.AUDIT_REVIEW_OFFICER),
    }
    headers = {k: _auth(client, u) for k, u in {
        "admin": "admin", "citizen": "citizen_a", "citizen2": "citizen_b", "officer": "officer",
        "supervisor": "supervisor", "io": "io_one", "io2": "io_two", "auditor": "auditor"}.items()}
    r = client.post("/stations", json={"name": "Saddar Police Station", "location": "Rawalpindi"},
                    headers=headers["admin"])
    assert r.status_code == 201
    return {"ids": ids, "h": headers, "station": r.json()["station_id"]}


# ----------------------------------------------------------------- stations

def test_only_admin_creates_stations_but_all_can_list(client, world):
    h = world["h"]
    assert client.post("/stations", json={"name": "Another PS"}, headers=h["officer"]).status_code == 403
    assert client.post("/stations", json={"name": "Saddar Police Station"}, headers=h["admin"]).status_code == 409
    assert client.get("/stations").status_code == 401
    rows = client.get("/stations", headers=h["citizen"]).json()
    assert [s["name"] for s in rows] == ["Saddar Police Station"]


# ---------------------------------------------------------------- complaints

def test_citizen_files_complaint(client, world):
    r = client.post("/complaints", json=_complaint_body(world["station"]), headers=world["h"]["citizen"])
    assert r.status_code == 201, r.text
    c = r.json()
    assert re.fullmatch(rf"CMP-{YEAR}-000001", c["reference_number"])
    assert c["status"] == "submitted"
    assert c["complainant_user_id"] == world["ids"]["citizen"]
    assert c["filed_on_behalf"] is False
    assert c["fir_number"] is None
    world["complaint_1"] = c["complaint_id"]


def test_officer_files_for_walk_in_complainant(client, world):
    r = client.post("/complaints", headers=world["h"]["officer"],
                    json=_complaint_body(world["station"], complainant_name="Walk In Person",
                                         complainant_cnic="54321-7654321-2"))
    assert r.status_code == 201
    c = r.json()
    assert c["filed_on_behalf"] is True
    assert c["complainant_user_id"] is None            # walk-in has no account
    assert c["filed_by_user_id"] == world["ids"]["officer"]
    assert c["complainant_name"] == "Walk In Person"   # officer typed the complainant's own details
    assert c["reference_number"].endswith("000002")
    world["complaint_walkin"] = c["complaint_id"]


@pytest.mark.parametrize("override,label", [
    ({"complainant_cnic": "1234512345671"}, "bad cnic"),
    ({"complainant_phone": "12345"}, "bad phone"),
    ({"description": "too short"}, "short description"),
    ({"incident_date": (datetime.now(timezone.utc) + timedelta(days=3)).isoformat()}, "future date"),
    ({"incident_location": "x"}, "short location"),
])
def test_complaint_validation(client, world, override, label):
    r = client.post("/complaints", json=_complaint_body(world["station"], **override), headers=world["h"]["citizen"])
    assert r.status_code == 422, label


def test_complaint_with_unknown_station_rejected(client, world):
    r = client.post("/complaints", json=_complaint_body("no-such-station"), headers=world["h"]["citizen"])
    assert r.status_code == 422


def test_who_may_file_and_who_may_list_complaints(client, world):
    h = world["h"]
    body = _complaint_body(world["station"])
    assert client.post("/complaints", json=body).status_code == 401
    for role in ("io", "supervisor", "auditor", "admin"):
        assert client.post("/complaints", json=body, headers=h[role]).status_code == 403, role
    for role in ("io", "auditor", "admin"):
        assert client.get("/complaints", headers=h[role]).status_code == 403, role


def test_citizen_sees_only_own_complaints(client, world):
    h = world["h"]
    mine = client.get("/complaints", headers=h["citizen"]).json()
    assert [c["complaint_id"] for c in mine] == [world["complaint_1"]]
    assert client.get("/complaints", headers=h["citizen2"]).json() == []
    # someone else's complaint looks like it does not exist
    assert client.get(f"/complaints/{world['complaint_1']}", headers=h["citizen2"]).status_code == 404
    assert client.get(f"/complaints/{world['complaint_1']}", headers=h["citizen"]).status_code == 200


def test_police_see_all_complaints_and_can_filter(client, world):
    h = world["h"]
    assert len(client.get("/complaints", headers=h["officer"]).json()) == 2
    assert len(client.get("/complaints", params={"search": "000002"}, headers=h["supervisor"]).json()) == 1
    assert len(client.get("/complaints", params={"status_filter": "rejected"}, headers=h["officer"]).json()) == 0
    assert client.get("/complaints", params={"limit": 1}, headers=h["officer"]).json().__len__() == 1


def test_citizen_cannot_review_their_own_complaint(client, world):
    cid = world["complaint_1"]
    for action in ("start-review", "register"):
        assert client.post(f"/complaints/{cid}/{action}", headers=world["h"]["citizen"]).status_code == 403
    assert client.post(f"/complaints/{cid}/reject", json={"reason": "no"}, headers=world["h"]["citizen"]).status_code == 403


def test_cannot_register_before_review(client, world):
    r = client.post(f"/complaints/{world['complaint_1']}/register", headers=world["h"]["officer"])
    assert r.status_code == 409


def test_review_then_register_creates_fir(client, world):
    h, cid = world["h"], world["complaint_1"]
    r = client.post(f"/complaints/{cid}/start-review", headers=h["officer"])
    assert r.status_code == 200 and r.json()["status"] == "under_review"
    assert client.post(f"/complaints/{cid}/start-review", headers=h["officer"]).status_code == 409  # not twice

    r = client.post(f"/complaints/{cid}/register", headers=h["supervisor"])
    assert r.status_code == 201, r.text
    fir = r.json()
    assert re.fullmatch(rf"FIR-{YEAR}-000001", fir["fir_number"])
    assert fir["status"] == "registered" and fir["complaint_reference"].startswith("CMP-")
    assert fir["complainant"] is None                       # list-style payload carries no personal data
    world["fir_id"] = fir["fir_id"]

    c = client.get(f"/complaints/{cid}", headers=h["officer"]).json()
    assert c["status"] == "registered" and c["fir_number"] == fir["fir_number"]
    assert client.post(f"/complaints/{cid}/register", headers=h["officer"]).status_code == 409  # only one FIR


def test_reject_needs_reason_and_is_final(client, world):
    h, cid = world["h"], world["complaint_walkin"]
    assert client.post(f"/complaints/{cid}/reject", json={}, headers=h["officer"]).status_code == 422
    assert client.post(f"/complaints/{cid}/reject", json={"reason": "  "}, headers=h["officer"]).status_code == 422
    r = client.post(f"/complaints/{cid}/reject", json={"reason": "Not a police matter"}, headers=h["officer"])
    assert r.status_code == 200
    assert r.json()["status"] == "rejected" and r.json()["rejection_reason"] == "Not a police matter"
    assert client.post(f"/complaints/{cid}/start-review", headers=h["officer"]).status_code == 409
    assert client.post(f"/complaints/{cid}/register", headers=h["officer"]).status_code == 409


# --------------------------------------------------------------------- FIRs

def test_assignment_rules(client, world):
    h, ids, fid = world["h"], world["ids"], world["fir_id"]
    body = {"io_user_id": ids["io"]}
    assert client.post(f"/firs/{fid}/assign", json=body, headers=h["officer"]).status_code == 403   # only supervisory
    assert client.post(f"/firs/{fid}/assign", json=body, headers=h["io"]).status_code == 403
    # target must be an active Investigating Officer
    assert client.post(f"/firs/{fid}/assign", json={"io_user_id": ids["officer"]}, headers=h["supervisor"]).status_code == 422
    assert client.post(f"/firs/{fid}/assign", json={"io_user_id": "nobody"}, headers=h["supervisor"]).status_code == 422

    r = client.post(f"/firs/{fid}/assign", json=body, headers=h["supervisor"])
    assert r.status_code == 200
    assert r.json()["status"] == "assigned" and r.json()["assigned_io"] == ids["io"]
    assert r.json()["assigned_io_name"] == "Io One"


def test_reassignment_changes_who_can_see_the_fir(client, world):
    h, ids, fid = world["h"], world["ids"], world["fir_id"]
    assert len(client.get("/firs", headers=h["io"]).json()) == 1
    assert client.get("/firs", headers=h["io2"]).json() == []
    assert client.get(f"/firs/{fid}", headers=h["io2"]).status_code == 404

    r = client.post(f"/firs/{fid}/assign", json={"io_user_id": ids["io2"]}, headers=h["supervisor"])
    assert r.status_code == 200 and r.json()["assigned_io"] == ids["io2"]
    assert client.get("/firs", headers=h["io"]).json() == []
    assert len(client.get("/firs", headers=h["io2"]).json()) == 1


def test_only_the_assigned_io_can_work_the_case(client, world):
    h, fid = world["h"], world["fir_id"]
    assert client.post(f"/firs/{fid}/start-investigation", headers=h["io"]).status_code == 403      # no longer assigned
    assert client.post(f"/firs/{fid}/start-investigation", headers=h["supervisor"]).status_code == 403  # wrong role
    assert client.post(f"/firs/{fid}/submit-for-review", headers=h["io2"]).status_code == 409        # must start first

    r = client.post(f"/firs/{fid}/start-investigation", headers=h["io2"])
    assert r.status_code == 200 and r.json()["status"] == "investigation_in_progress"
    # once investigation has begun the assignment is locked
    assert client.post(f"/firs/{fid}/assign", json={"io_user_id": world["ids"]["io"]},
                       headers=h["supervisor"]).status_code == 409


def test_review_cycle_and_closure(client, world):
    h, fid = world["h"], world["fir_id"]
    assert client.post(f"/firs/{fid}/close", headers=h["supervisor"]).status_code == 409   # can't skip review

    r = client.post(f"/firs/{fid}/submit-for-review", headers=h["io2"])
    assert r.status_code == 200 and r.json()["status"] == "pending_review"

    assert client.post(f"/firs/{fid}/close", headers=h["officer"]).status_code == 403      # only supervisory
    assert client.post(f"/firs/{fid}/return-to-investigation", json={}, headers=h["supervisor"]).status_code == 422
    r = client.post(f"/firs/{fid}/return-to-investigation",
                    json={"reason": "Witness statement missing"}, headers=h["supervisor"])
    assert r.status_code == 200 and r.json()["status"] == "investigation_in_progress"

    client.post(f"/firs/{fid}/submit-for-review", headers=h["io2"])
    r = client.post(f"/firs/{fid}/close", headers=h["supervisor"])
    assert r.status_code == 200 and r.json()["status"] == "closed" and r.json()["closed_at"] is not None
    assert client.post(f"/firs/{fid}/close", headers=h["supervisor"]).status_code == 409   # closed is final


def test_fir_visibility_and_personal_data_rules(client, world):
    h, fid = world["h"], world["fir_id"]
    # the complainant can track their own FIR, and see their own details
    mine = client.get("/firs", headers=h["citizen"]).json()
    assert [f["fir_id"] for f in mine] == [fid] and mine[0]["complainant"] is None
    detail = client.get(f"/firs/{fid}", headers=h["citizen"]).json()
    assert detail["complainant"]["cnic"] == "12345-1234567-1"
    # another citizen cannot see it
    assert client.get("/firs", headers=h["citizen2"]).json() == []
    assert client.get(f"/firs/{fid}", headers=h["citizen2"]).status_code == 404
    # police and the assigned IO see the complainant; the auditor does not (data minimisation)
    for role in ("officer", "supervisor", "io2"):
        assert client.get(f"/firs/{fid}", headers=h[role]).json()["complainant"]["name"] == "Ali Khan"
    assert client.get(f"/firs/{fid}", headers=h["auditor"]).json()["complainant"] is None
    # admin manages users, not cases
    assert client.get("/firs", headers=h["admin"]).status_code == 403
    assert client.get(f"/firs/{fid}", headers=h["admin"]).status_code == 403
    assert client.get("/firs").status_code == 401


def test_fir_search_and_filters(client, world):
    h = world["h"]
    assert len(client.get("/firs", params={"search": "000001"}, headers=h["officer"]).json()) == 1
    assert client.get("/firs", params={"search": "999999"}, headers=h["officer"]).json() == []
    assert len(client.get("/firs", params={"status_filter": "closed"}, headers=h["auditor"]).json()) == 1
    assert client.get("/firs", params={"status_filter": "registered"}, headers=h["auditor"]).json() == []
    today = datetime.now(timezone.utc).date().isoformat()
    assert len(client.get("/firs", params={"date_from": today, "date_to": today}, headers=h["officer"]).json()) == 1
    assert client.get("/firs", params={"date_to": "2000-01-01"}, headers=h["officer"]).json() == []
    assert len(client.get("/firs", params={"assigned_io": world["ids"]["io2"]}, headers=h["supervisor"]).json()) == 1
    assert client.get("/firs", params={"limit": 0}, headers=h["officer"]).status_code == 422


# ---------------------------------------------------------------- audit trail

def test_audit_trail_records_every_step_in_order(client, world):
    h, fid = world["h"], world["fir_id"]
    rows = client.get(f"/audit/fir/{fid}", headers=h["auditor"]).json()
    assert [r["action"] for r in rows] == [
        "fir_registered", "io_assigned", "io_reassigned", "investigation_started", "submitted_for_review",
        "returned_to_investigation", "submitted_for_review", "fir_closed",
    ]
    assert rows[-1]["from_status"] == "pending_review" and rows[-1]["to_status"] == "closed"
    assert rows[-1]["actor_role"] == "supervisory_officer" and rows[-1]["actor_id"] == world["ids"]["supervisor"]
    assert "12345-1234567-1" not in str(rows)                  # no personal data in the audit log

    crows = client.get(f"/audit/complaint/{world['complaint_1']}", headers=h["supervisor"]).json()
    assert [r["action"] for r in crows] == ["complaint_submitted", "review_started", "complaint_registered"]


def test_audit_trail_access_control(client, world):
    fid = world["fir_id"]
    for role in ("officer", "io2", "citizen"):
        assert client.get(f"/audit/fir/{fid}", headers=world["h"][role]).status_code == 403, role
    assert client.get(f"/audit/fir/{fid}", headers=world["h"]["admin"]).status_code == 200
    assert client.get(f"/audit/other/{fid}", headers=world["h"]["admin"]).status_code == 422
    assert client.get(f"/audit/fir/{fid}").status_code == 401


def test_failed_actions_leave_no_audit_entry(client, world):
    before = len(client.get(f"/audit/fir/{world['fir_id']}", headers=world["h"]["admin"]).json())
    client.post(f"/firs/{world['fir_id']}/close", headers=world["h"]["supervisor"])   # 409: already closed
    after = len(client.get(f"/audit/fir/{world['fir_id']}", headers=world["h"]["admin"]).json())
    assert before == after


def test_second_fir_gets_next_number(client, world):
    h = world["h"]
    cid = client.post("/complaints", json=_complaint_body(world["station"], crime_category="Fraud"),
                      headers=h["citizen2"]).json()["complaint_id"]
    client.post(f"/complaints/{cid}/start-review", headers=h["officer"])
    fir = client.post(f"/complaints/{cid}/register", headers=h["officer"]).json()
    assert fir["fir_number"] == f"FIR-{YEAR}-000002"