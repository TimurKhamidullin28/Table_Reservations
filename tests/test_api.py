async def test_status_200(async_client):
    response = await async_client.get("tables")

    assert response.status_code == 200
    assert len(response.json()) == 2


async def test_create_table(async_client):
    data = {"name": "Table 3", "seats": 2, "location": "Зал посередине"}
    response = await async_client.post("/tables", json=data)

    assert response.status_code == 200
    assert response.json()["name"] == "Table 3"


async def test_delete_table(async_client):
    response_delete = await async_client.delete("/tables/1")
    response = await async_client.get("/tables")

    assert response_delete.status_code == 200
    assert len(response.json()) == 1


async def test_delete_wrong_table(async_client):
    response_delete = await async_client.delete("/tweets/5")

    assert response_delete.status_code == 404


async def test_reservations(async_client):
    data = {
        "customer_name": "John",
        "table_id": 1,
        "reservation_time": "2025-04-13 18:00",
        "duration_minutes": 60,
    }

    wrong_data = {
        "customer_name": "Sam",
        "table_id": 1,
        "reservation_time": "2025-04-13 18:30",
        "duration_minutes": 45,
    }

    response = await async_client.post("/reservations", json=data)
    response_get = await async_client.get("/reservations")
    response_wrong = await async_client.post("/reservations", json=wrong_data)

    assert response.status_code == 200
    assert response.json()["customer_name"] == "John"

    assert response_get.status_code == 200
    assert len(response_get.json()) == 1

    assert response_wrong.status_code == 400
    assert "Table is already reserved for this period time" in response_wrong.text
