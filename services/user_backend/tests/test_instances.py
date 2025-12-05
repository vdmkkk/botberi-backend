import pytest


@pytest.mark.asyncio
async def test_instance_lifecycle(client, registered_user, seeded_agents):
    login_resp = await client.post(
        "/api/v1/auth/login",
        json={"email": registered_user["email"], "password": registered_user["password"]},
    )
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    create_payload = {
        "bot_id": seeded_agents[0].id,
        "title": "My Bot",
        "user_config": {"param": 1},
        "pipeline_config": {"flow": []},
    }
    create_resp = await client.post("/api/v1/instances", json=create_payload, headers=headers)
    assert create_resp.status_code == 201
    instance = create_resp.json()
    instance_id = instance["id"]
    assert instance["knowledge_base"]["id"] is not None

    list_resp = await client.get("/api/v1/instances", headers=headers)
    assert list_resp.status_code == 200
    assert len(list_resp.json()) == 1

    patch_resp = await client.patch(
        f"/api/v1/instances/{instance_id}",
        json={"title": "Updated Bot"},
        headers=headers,
    )
    assert patch_resp.status_code == 200
    assert patch_resp.json()["title"] == "Updated Bot"

    entry_payload = {"content": "Docs", "data_type": "document"}
    entry_resp = await client.post(
        f"/api/v1/instances/{instance_id}/knowledge-base/entries",
        json=entry_payload,
        headers=headers,
    )
    assert entry_resp.status_code == 201
    entry_id = entry_resp.json()["id"]

    kb_list = await client.get(f"/api/v1/instances/{instance_id}/knowledge-base/entries", headers=headers)
    assert len(kb_list.json()) == 1

    delete_entry = await client.delete(
        f"/api/v1/instances/{instance_id}/knowledge-base/entries/{entry_id}",
        headers=headers,
    )
    assert delete_entry.status_code == 204

    delete_resp = await client.delete(f"/api/v1/instances/{instance_id}", headers=headers)
    assert delete_resp.status_code == 204


