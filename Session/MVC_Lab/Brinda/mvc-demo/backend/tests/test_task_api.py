def test_get_tasks_empty_returns_200_and_empty_list(client):
    """GET /tasks/ with no tasks yet returns 200 and []."""
    response = client.get("/tasks/")
    assert response.status_code == 200
    assert response.json() == []
 
def test_post_task_returns_201_with_created_task(client, alice):
    """POST /tasks/ with {"title": "read docs"} returns 201.
    Body has an id, title == "read docs".
    Hint: r = client.post("/tasks/", json={"title": "read docs"})
    """
    response = client.post("/tasks/", json={"title": "read docs", "owner_id": alice.id})
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["title"] == "read docs"
def test_post_task_with_emoty_title_returns_422(client):
    """
    pydantic min_length=1 rejects an empty title before the service is called.
    Status: 422.
    """
    response = client.post("/tasks/", json={"title": "", "owner_id": 1})
    assert response.status_code == 422
 
def test_get_task_by_id_returns_the_task(client):
    """POST creates a task, then GET /tasks.{id} returns the same task with 200.
    Hint: pull id out of the POST response body.
    """
    post_response = client.post("/tasks/", json={"title": "read docs", "owner_id": 1})
    task_id = post_response.json()["id"]
    get_response = client.get(f"/tasks/{task_id}")
    assert get_response.status_code == 200
    data = get_response.json()
    assert data["id"] == task_id
    assert data["title"] == "read docs"
 
def test_delete_own_task_returns_204_then_get_returns_404(client):
    """
    Create a task, DELETE it ( expect 204), then GET the same id (expect 404).
    """
    post_response = client.post("/tasks/", json={"title": "read docs", "owner_id": 1})
    task_id = post_response.json()["id"]
    delete_response = client.delete(f"/tasks/{task_id}")
    assert delete_response.status_code == 204
    get_response = client.get(f"/tasks/{task_id}")
    assert get_response.status_code == 404
 