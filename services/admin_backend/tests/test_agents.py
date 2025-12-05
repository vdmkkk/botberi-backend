import pytest


@pytest.mark.asyncio
async def test_agent_crud_flow(client):
    create_payload = {
        "title": "My Agent",
        "content": {"description": "demo"},
        "activation_code": "ACT123",
        "rate": 5,
    }
    create_resp = await client.post("/api/v1/agents", json=create_payload)
    assert create_resp.status_code == 201
    agent = create_resp.json()
    agent_id = agent["id"]
    assert agent["title"] == create_payload["title"]

    list_resp = await client.get("/api/v1/agents")
    assert list_resp.status_code == 200
    assert len(list_resp.json()) == 1

    detail_resp = await client.get(f"/api/v1/agents/{agent_id}")
    assert detail_resp.status_code == 200
    assert detail_resp.json()["activation_code"] == "ACT123"

    update_resp = await client.patch(
        f"/api/v1/agents/{agent_id}",
        json={"title": "Updated", "rate": 9},
    )
    assert update_resp.status_code == 200
    assert update_resp.json()["title"] == "Updated"
    assert update_resp.json()["rate"] == 9

    delete_resp = await client.delete(f"/api/v1/agents/{agent_id}")
    assert delete_resp.status_code == 204

    missing_resp = await client.get(f"/api/v1/agents/{agent_id}")
    assert missing_resp.status_code == 404


