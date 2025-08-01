import pytest
from fastapi.testclient import TestClient
from src.api.main import app
from src.core.database import create_tables, drop_tables

client = TestClient(app)

@pytest.fixture(autouse=True, scope="module")
def setup_and_teardown():
    # Drop and re-create all tables for a clean test DB
    drop_tables()
    create_tables()
    yield
    drop_tables()

def test_openapi_endpoints_visible():
    # Check the endpoints are listed in the OpenAPI schema
    resp = client.get("/openapi.json")
    assert resp.status_code == 200
    data = resp.json()
    # The endpoints might have prefix in OpenAPI
    auth_paths = [p for p in data["paths"].keys() if "register" in p or "login" in p]
    assert any("register" in p for p in auth_paths)
    assert any("login" in p for p in auth_paths)

def test_register_and_login_flow():
    # Registration: success
    new_user = {
        "type": "user",
        "username": "testuser",
        "email": "testuser@example.com",
        "full_name": "Test User",
        "password": "Validpass1"
    }
    resp = client.post("/api/v1/auth/register", json=new_user)
    assert resp.status_code == 201
    res = resp.json()
    assert res["success"] is True
    assert "registered successfully" in res["message"]

    # Registration: duplicate username/email rejected
    resp2 = client.post("/api/v1/auth/register", json=new_user)
    assert resp2.status_code == 400
    assert "already exists" in resp2.json()["detail"]

    # Registration: missing fields
    resp3 = client.post("/api/v1/auth/register", json={"username": "partial"})
    assert resp3.status_code == 422

    # Registration: password too short (should fail pydantic validation)
    short_pw = dict(new_user)
    short_pw["username"] = "testuser2"
    short_pw["email"] = "testuser2@example.com"
    short_pw["password"] = "short"
    resp4 = client.post("/api/v1/auth/register", json=short_pw)
    assert resp4.status_code == 422

    # Registration: extra/invalid field (should fail with 422)
    with_extra = dict(new_user)
    with_extra["unexpected_field"] = "boom"
    resp5 = client.post("/api/v1/auth/register", json=with_extra)
    assert resp5.status_code == 422
    err = resp5.json()
    assert "extra fields not permitted" in str(err["detail"])

    # Login: success (with email)
    resp6 = client.post("/api/v1/auth/login", data={
        "username": new_user["email"],
        "password": new_user["password"]
    })
    assert resp6.status_code == 200
    login_data = resp6.json()
    assert "access_token" in login_data
    assert login_data["token_type"] == "bearer"

    # Login: wrong password (should fail)
    resp7 = client.post("/api/v1/auth/login", data={
        "username": new_user["email"],
        "password": "wrongpassword"
    })
    assert resp7.status_code == 401

    # Login: unknown user
    resp8 = client.post("/api/v1/auth/login", data={
        "username": "notfound@example.com",
        "password": "nopass123"
    })
    assert resp8.status_code == 401

def test_admin_registration_and_login():
    admin_payload = {
        "type": "admin",
        "username": "operator",
        "email": "operator@example.com",
        "full_name": "Main Operator",
        "is_superuser": True,
        "is_admin": True,
        "permissions": {"config": True},
        "notes": "Test admin",
        "password": "SuperPass1"
    }
    resp = client.post("/api/v1/auth/register", json=admin_payload)
    assert resp.status_code == 201
    assert resp.json()["success"]

    # Login as admin
    resp2 = client.post("/api/v1/auth/login", data={
        "username": admin_payload["email"],
        "password": admin_payload["password"]
    })
    assert resp2.status_code == 200
    assert "access_token" in resp2.json()
    assert resp2.json()["token_type"] == "bearer"
