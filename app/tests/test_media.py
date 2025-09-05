import pytest_asyncio
import pytest
from httpx import AsyncClient
from app.main import app


# Must match event_loop scope (function)
@pytest_asyncio.fixture(scope="function")
async def async_client():
    async with AsyncClient(app=app, base_url="http://testserver") as client:
        yield client


@pytest.mark.asyncio
async def test_signup_login_and_presign(async_client):
    # signup
    resp = await async_client.post("/auth/signup", json={"email": "test@example.com", "password": "pass123"})
    assert resp.status_code in [200, 400]  # allow 400 if already signed up

    # login
    resp = await async_client.post("/auth/login", data={"username": "test@example.com", "password": "pass123"})
    assert resp.status_code == 200
    login_token = resp.json()["access_token"]

    headers = {"Authorization": f"Bearer {login_token}"}

    # create media
    files = {"file": ("small.txt", b"hello world")}
    data = {"title": "t", "type": "audio"}
    resp = await async_client.post("/media/", headers=headers, files=files, data=data)
    assert resp.status_code == 200
    media_id = resp.json()["id"]

    # generate stream URL
    resp = await async_client.get(f"/media/{media_id}/stream-url", headers=headers)
    assert resp.status_code == 200
    assert "token=" in resp.json()["stream_url"]

    # analytics
    resp = await async_client.get(f"/media/{media_id}/analytics", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["total_views"] == 0


@pytest.mark.asyncio
async def test_rate_limit_on_view(async_client):
    # login
    resp = await async_client.post("/auth/login", data={"username": "test@example.com", "password": "pass123"})
    assert resp.status_code == 200
    token = resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # create media
    files = {"file": ("small2.txt", b"hi")}
    data = {"title": "t2", "type": "audio"}
    resp = await async_client.post("/media/", headers=headers, files=files, data=data)
    assert resp.status_code == 200
    media_id = resp.json()["id"]

    # hit view endpoint more than limit (limit = 20), call 22 times
    for i in range(22):
        r = await async_client.post(f"/media/{media_id}/view", headers=headers)
        if i < 20:
            assert r.status_code == 200
        else:
            assert r.status_code == 429
            break
