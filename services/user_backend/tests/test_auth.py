import json

import pytest

from app.core.config import get_settings


@pytest.mark.asyncio
async def test_registration_and_login_flow(client, fake_redis):
    payload = {
        "name": "Alice",
        "company": "Botberi",
        "email": "alice@example.com",
        "password": "secret123",
        "phone": "+1234567890",
        "telegram": "@alice",
    }
    resp = await client.post("/api/v1/auth/register/request", json=payload)
    assert resp.status_code == 202

    cached = await fake_redis.get("registration:pending:alice@example.com")
    code = json.loads(cached)["code"]

    resp = await client.post(
        "/api/v1/auth/register/confirm",
        json={"email": payload["email"], "code": code},
    )
    assert resp.status_code == 201

    login_resp = await client.post(
        "/api/v1/auth/login",
        json={"email": payload["email"], "password": payload["password"]},
    )
    assert login_resp.status_code == 200
    body = login_resp.json()
    assert "access_token" in body
    assert login_resp.headers["X-Auth-Token"] == body["access_token"]
    assert settings().auth_cookie_name in login_resp.headers.get("set-cookie", "")


@pytest.mark.asyncio
async def test_profile_update(client, fake_redis, registered_user):
    login_resp = await client.post(
        "/api/v1/auth/login",
        json={"email": registered_user["email"], "password": registered_user["password"]},
    )
    token = login_resp.json()["access_token"]

    updated = {
        "name": "Updated User",
        "company": "Updated Co",
        "phone": "+1888888888",
        "telegram": "@updated",
    }
    resp = await client.patch(
        "/api/v1/users/me",
        json=updated,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["name"] == updated["name"]
    assert body["company"] == updated["company"]
    assert body["phone"] == updated["phone"]
    assert body["telegram"] == updated["telegram"]


@pytest.mark.asyncio
async def test_password_reset_flow(client, fake_redis, registered_user):
    login_resp = await client.post(
        "/api/v1/auth/login",
        json={"email": registered_user["email"], "password": registered_user["password"]},
    )
    token = login_resp.json()["access_token"]

    resp = await client.post(
        "/api/v1/auth/password/reset/request",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 202

    keys = await fake_redis.keys("password-reset:*")
    assert keys, "expected password reset token"
    redis_key = keys[0]
    reset_token = redis_key.split("password-reset:", 1)[1]

    confirm_resp = await client.post(
        "/api/v1/auth/password/reset/confirm",
        json={"token": reset_token, "new_password": "newsecret123"},
    )
    assert confirm_resp.status_code == 200

    new_login = await client.post(
        "/api/v1/auth/login",
        json={"email": registered_user["email"], "password": "newsecret123"},
    )
    assert new_login.status_code == 200


def settings():
    return get_settings()


