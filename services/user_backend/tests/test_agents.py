import pytest


@pytest.mark.asyncio
async def test_list_agents(client, seeded_agents):
    response = await client.get("/api/v1/agents")
    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 2
    assert payload[0]["title"] == seeded_agents[0].title


@pytest.mark.asyncio
async def test_get_agent(client, seeded_agents):
    agent_id = seeded_agents[0].id
    response = await client.get(f"/api/v1/agents/{agent_id}")
    assert response.status_code == 200
    assert response.json()["activation_code"] == seeded_agents[0].activation_code

    missing = await client.get("/api/v1/agents/999")
    assert missing.status_code == 404


