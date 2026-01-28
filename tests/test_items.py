def test_list_items_returns_mockdata(client):
    res = client.get("/items/")
    assert res.status_code == 200
    assert res.json() == [
        {"id": 1, "name": "mock-item-1"},
        {"id": 2, "name": "mock-item-2"},
    ]


def test_create_item_does_not_use_real_db_and_updates_repo(client):
    res = client.post("/items/", json={"name": "new-item"})
    assert res.status_code == 201
    assert res.json() == {"id": 3, "name": "new-item"}

    res2 = client.get("/items/")
    assert res2.status_code == 200
    assert res2.json() == [
        {"id": 1, "name": "mock-item-1"},
        {"id": 2, "name": "mock-item-2"},
        {"id": 3, "name": "new-item"},
    ]

