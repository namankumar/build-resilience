import sys, pathlib
sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_check():
    """Verify ``app.main.health_check`` returns the expected response."""
    response = client.get('/health')
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_full_flow():
    """End-to-end test of reflection and win functions in ``app.main``."""
    # create reflection via ``create_reflection`` endpoint
    resp = client.post('/reflections', json={"text": "I overate", "mood": "sad"})
    assert resp.status_code == 200
    reflection = resp.json()
    assert reflection["id"] == 1

    # get reframe via ``get_reframe`` endpoint
    resp = client.get(f'/reframe/{reflection["id"]}')
    assert resp.status_code == 200
    reframe = resp.json()
    assert reframe["reflection_id"] == reflection["id"]

    # record win via ``record_win`` endpoint
    resp = client.post('/wins', json={"reflection_id": reflection["id"], "win": "walk"})
    assert resp.status_code == 200

    # check streak via ``get_streak``
    resp = client.get('/streak')
    assert resp.status_code == 200
    assert resp.json()["count"] == 1

    # check winrack via ``get_winrack``
    resp = client.get('/winrack')
    assert resp.status_code == 200
    assert "walk" in resp.json()["wins"]
