import pytest


@pytest.mark.asyncio
async def test_health_endpoint(client) -> None:
    response = await client.get("/api/v1/health")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"


