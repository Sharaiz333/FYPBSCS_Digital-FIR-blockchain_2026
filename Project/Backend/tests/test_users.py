"""
Run from backend/ with:  pytest -v
Uses a throwaway SQLite file so no PostgreSQL is needed for tests.
The env vars MUST be set before the app is imported.
"""
import os

os.environ["DATABASE_URL"] = "sqlite:///./test_users.db"
os.environ["JWT_SECRET_KEY"] = "test-secret"

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session

from app.core.database import engine
from app.core.security import hash_password
from app.main import app
from app.models.enums import RoleName
from app.models.user import User


@pytest.fixture(scope="module")
def client():
    if os.path.exists("./test_users.db"):
        os.remove("./test_users.db")
    with TestClient(app) as c:
        yield c
    if os.path.exists("./test_users.db"):
        os.remove("./test_users.db")


def _make_user(username: str, role: RoleName, password: str = "Pass12345") -> str:
    with Session(engine) as s:
        user = User(full_name=username.title(), username=username,
                    password_hash=hash_password(password), role=role)
        s.add(user)
        s.commit()
        s.refresh(user)
        return user.user_id


def _login(client, username: str, password: str = "Pass12345") -> dict:
    r = client.post("/auth/login", json={"username": username, "password": password})
    assert r.status_code == 200, r.text
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


@pytest.fixture(scope="module")
def admin(client):
    admin_id = _make_user("admin", RoleName.ADMIN)
    return {"id": admin_id, "headers": _login(client, "admin")}


NEW_USER = {"full_name": "Officer One", "username": "officer1", "password": "Pass12345", "role": "police_officer"}


def test_admin_can_create_user_and_hash_is_not_returned(client, admin):
    r = client.post("/users", json=NEW_USER, headers=admin["headers"])
    assert r.status_code == 201
    body = r.json()
    assert body["role"] == "police_officer"
    assert "password" not in body and "password_hash" not in body


def test_new_user_can_log_in(client, admin):
    assert _login(client, "officer1")


def test_duplicate_username_rejected(client, admin):
    r = client.post("/users", json=NEW_USER, headers=admin["headers"])
    assert r.status_code == 409


def test_weak_password_and_bad_username_rejected(client, admin):
    r = client.post("/users", json={**NEW_USER, "username": "x1", "password": "short"}, headers=admin["headers"])
    assert r.status_code == 422
    r = client.post("/users", json={**NEW_USER, "username": "bad name!"}, headers=admin["headers"])
    assert r.status_code == 422


def test_no_token_gets_401(client):
    assert client.get("/users").status_code == 401
    assert client.post("/users", json=NEW_USER).status_code == 401


def test_non_admin_gets_403(client, admin):
    officer = _login(client, "officer1")
    assert client.get("/users", headers=officer).status_code == 403
    assert client.post("/users", json={**NEW_USER, "username": "another"}, headers=officer).status_code == 403


def test_admin_can_list_and_filter(client, admin):
    r = client.get("/users", headers=admin["headers"])
    assert r.status_code == 200 and len(r.json()) >= 2
    r = client.get("/users", params={"role": "police_officer"}, headers=admin["headers"])
    assert [u["username"] for u in r.json()] == ["officer1"]


def test_me_returns_own_profile(client, admin):
    r = client.get("/users/me", headers=_login(client, "officer1"))
    assert r.status_code == 200 and r.json()["username"] == "officer1"


def test_deactivated_user_cannot_log_in(client, admin):
    officer_id = client.get("/users", params={"role": "police_officer"}, headers=admin["headers"]).json()[0]["user_id"]
    r = client.patch(f"/users/{officer_id}", json={"is_active": False}, headers=admin["headers"])
    assert r.status_code == 200 and r.json()["is_active"] is False
    r = client.post("/auth/login", json={"username": "officer1", "password": "Pass12345"})
    assert r.status_code == 401
    client.patch(f"/users/{officer_id}", json={"is_active": True}, headers=admin["headers"])


def test_admin_cannot_lock_themselves_out(client, admin):
    r = client.patch(f"/users/{admin['id']}", json={"is_active": False}, headers=admin["headers"])
    assert r.status_code == 400
    r = client.patch(f"/users/{admin['id']}", json={"role": "citizen"}, headers=admin["headers"])
    assert r.status_code == 400


def test_update_unknown_user_404(client, admin):
    assert client.patch("/users/does-not-exist", json={"is_active": False}, headers=admin["headers"]).status_code == 404