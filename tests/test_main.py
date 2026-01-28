def test_openapi_available(client):
    res = client.get("/openapi.json")
    assert res.status_code == 200
    assert res.json()["info"]["title"] == "smart-irrigation-api"

