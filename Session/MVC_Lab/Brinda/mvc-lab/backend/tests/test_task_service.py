from app.services.task_service import TaskService

def test_create_task():
    service = TaskService()
    result = service.create_task("buy milk")
    
    assert result["title"] == "buy milk"
    assert "id" in result
    assert len(service.list_tasks()) == 1

def test_delete_task():
    service = TaskService()
    task = service.create_task("temp task")
    deleted = service.delete_task(task["id"])
    
    assert deleted is True
    assert len(service.list_tasks()) == 0