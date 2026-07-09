from fastapi.testclient import TestClient
from app.models import Task
from app.main import app
from app.database import get_db
 
def _seed_task(db, title: str, owner_id: int) -> Task:
    t = Task(title=title, owner_id=owner_id)
    db.add(t)
    db.commit()
    db.refresh(t)
    return t
 
 
def test_list_tasks_does_not_leak_other_users_tasks(client, db_session, alice, bob):
    _seed_task(db_session, "Alice's task", alice.id)
    _seed_task(db_session, "Bob's task", bob.id)
 
    response = client.get("/tasks")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["title"] == "Alice's task"
 
 
def test_alice_cannot_get_bob_task_by_id(client, db_session, bob):
    bob_task = _seed_task(db_session, "Bob's task", bob.id)
    response = client.get(f"/tasks/{bob_task.id}")
    assert response.status_code == 403
 
 
def test_alice_cannot_delete_bob_task(client, db_session, bob):
    bob_task = _seed_task(db_session, "Bob's task", bob.id)
    response = client.delete(f"/tasks/{bob_task.id}")
    assert response.status_code == 403
 
 
def test_unauthenticated_request_is_rejected(db_session):
    app.dependency_overrides[get_db] = lambda: db_session
    try:
        raw = TestClient(app)
        r = raw.get("/tasks")
        assert r.status_code == 401
    finally:
        app.dependency_overrides.clear()
 