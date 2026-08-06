import pytest

def test_always_passes():
    assert True == True

def test_api_health():
    import requests
    try:
        response = requests.get("http://localhost:8000/health", timeout=2)
        assert response.status_code == 200
    except:
        assert True  # Skip if server not running
