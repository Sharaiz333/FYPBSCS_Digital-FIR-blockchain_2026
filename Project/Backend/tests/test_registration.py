"""Citizen self-registration and officer verification."""
import pytest
from sqlmodel import Session

from app.core.database import engine
from app.core.security import hash_password
from app.models.enums import RoleName
from app.models.user import User

CITIZEN = {
    "full_name": "Ali Khan",
    "username": "ali.khan",
    "password": "Pass12345",
    "cnic": "12345-1234567-1",
    "phone": "0300-1234567",
    "address": "House 1, Street 2, Rawalpindi",
}


def _make_staff(username: str, role: RoleName) -> None:
    with Session(engine) as s:
        s.add(User(full_name=username.title(), username=username,
                   password_hash=hash_password("Pass12345"), role=role))
        s.commit()


def _login(client, username: str, password: str = "Pass12345"):
    return client.post("/auth/login", json={"username": username, "password": password})


def _headers(client, username: str) -> dict:
    r = _login(client, username)
    assert r.status_code == 200, r.text
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


@pytest.fixture(scope="module")
def staff(client):
    _make_staff("front_desk", RoleName.POLICE_OFFICER)
    _make_staff("supervisor", RoleName.SUPERVISORY_OFFICER)
    _make_staff("investigator", RoleName.INVESTIGATING_OFFICER)
    return {
        "officer": _headers(client, "front_desk"),
        "supervisor": _headers(client, "supervisor"),
        "investigator": _headers(client, "investigator"),
    }


def _pending_id(client, headers, username: str) -> str:
    rows = client.get("/verification/citizens", headers=headers).json()
    return next(r["user_id"] for r in rows if r["username"] == username)


def test_register_creates_pending_citizen(client):
    r = client.post("/auth/register", json=CITIZEN)
    assert r.status_code == 201
    assert r.json()["verification_status"] == "pending"
    assert "password" not in r.text


def test_pending_citizen_cannot_log_in(client):
    r = _login(client, "ali.khan")
    assert r.status_code == 403
    assert "awaiting verification" in r.json()["detail"]


def test_wrong_password_still_gets_generic_401(client):
    # Status messages must not be reachable without the correct password.
    assert _login(client, "ali.khan", "WrongPass999").status_code == 401


def test_registration_validation(client):
    bad = {**CITIZEN, "username": "someone"}
    assert client.post("/auth/register", json={**bad, "cnic": "1234512345671"}).status_code == 422
    assert client.post("/auth/register", json={**bad, "phone": "12345"}).status_code == 422
    assert client.post("/auth/register", json={**bad, "password": "short"}).status_code == 422
    assert client.post("/auth/register", json={**bad, "username": "bad name!"}).status_code == 422


def test_duplicate_cnic_and_username_rejected(client):
    r = client.post("/auth/register", json={**CITIZEN, "username": "other.name"})
    assert r.status_code == 409  # same CNIC
    r = client.post("/auth/register", json={**CITIZEN, "cnic": "99999-9999999-9"})
    assert r.status_code == 409  # same username


def test_client_cannot_choose_a_role(client, staff):
    # A client sending role=admin must be ignored: the account is a plain citizen.
    r = client.post("/auth/register", json={
        **CITIZEN, "username": "sneaky", "cnic": "11111-1111111-1", "role": "admin",
    })
    assert r.status_code == 201
    sid = _pending_id(client, staff["officer"], "sneaky")
    client.post(f"/verification/citizens/{sid}", json={"approve": True}, headers=staff["officer"])
    me = client.get("/users/me", headers=_headers(client, "sneaky")).json()
    assert me["role"] == "citizen"


def test_verification_queue_access_control(client, staff):
    assert client.get("/verification/citizens").status_code == 401
    assert client.get("/verification/citizens", headers=staff["investigator"]).status_code == 403
    citizen_headers = _headers(client, "sneaky")  # verified citizen from the previous test
    assert client.get("/verification/citizens", headers=citizen_headers).status_code == 403


def test_officer_sees_full_details_in_queue(client, staff):
    rows = client.get("/verification/citizens", headers=staff["officer"]).json()
    ali = next(r for r in rows if r["username"] == "ali.khan")
    assert ali["cnic"] == "12345-1234567-1"
    assert "password_hash" not in ali and "password" not in ali


def test_officer_approves_and_citizen_can_log_in(client, staff):
    uid = _pending_id(client, staff["officer"], "ali.khan")
    r = client.post(f"/verification/citizens/{uid}", json={"approve": True}, headers=staff["officer"])
    assert r.status_code == 200
    body = r.json()
    assert body["verification_status"] == "verified" and body["verified_at"] is not None

    login = _login(client, "ali.khan")
    assert login.status_code == 200 and login.json()["role"] == "citizen"


def test_decision_cannot_be_repeated(client, staff):
    rows = client.get("/verification/citizens", params={"status_filter": "verified"}, headers=staff["officer"]).json()
    uid = next(r["user_id"] for r in rows if r["username"] == "ali.khan")
    r = client.post(f"/verification/citizens/{uid}", json={"approve": False, "reason": "changed my mind"},
                    headers=staff["officer"])
    assert r.status_code == 409


def test_rejection_needs_reason_then_blocks_login(client, staff):
    client.post("/auth/register", json={**CITIZEN, "username": "fake.person", "cnic": "22222-2222222-2"})
    uid = _pending_id(client, staff["officer"], "fake.person")

    r = client.post(f"/verification/citizens/{uid}", json={"approve": False}, headers=staff["officer"])
    assert r.status_code == 422
    r = client.post(f"/verification/citizens/{uid}", json={"approve": False, "reason": "   "}, headers=staff["officer"])
    assert r.status_code == 422

    r = client.post(f"/verification/citizens/{uid}",
                    json={"approve": False, "reason": "CNIC does not match the card shown"},
                    headers=staff["supervisor"])  # supervisory officers may verify too
    assert r.status_code == 200 and r.json()["verification_status"] == "rejected"

    login = _login(client, "fake.person")
    assert login.status_code == 403 and "not approved" in login.json()["detail"]


def test_rejected_citizen_can_reapply_and_be_approved(client, staff):
    again = {**CITIZEN, "username": "fake.person", "cnic": "22222-2222222-2", "full_name": "Corrected Name"}
    assert client.post("/auth/register", json=again).status_code == 201
    assert _login(client, "fake.person").status_code == 403  # pending again

    uid = _pending_id(client, staff["officer"], "fake.person")
    assert client.post(f"/verification/citizens/{uid}", json={"approve": True}, headers=staff["officer"]).status_code == 200
    ok = _login(client, "fake.person")
    assert ok.status_code == 200 and ok.json()["full_name"] == "Corrected Name"


def test_unknown_or_staff_id_returns_404(client, staff):
    assert client.post("/verification/citizens/nope", json={"approve": True}, headers=staff["officer"]).status_code == 404
    me = client.get("/users/me", headers=staff["officer"]).json()
    assert client.post(f"/verification/citizens/{me['user_id']}", json={"approve": True},
                       headers=staff["officer"]).status_code == 404