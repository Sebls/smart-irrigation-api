def test_openapi_available(client):
    res = client.get("/openapi.json")
    assert res.status_code == 200
    assert res.json()["info"]["title"] == "smart-irrigation-api"


def test_docs_available(client):
    res = client.get("/docs")
    assert res.status_code == 200


