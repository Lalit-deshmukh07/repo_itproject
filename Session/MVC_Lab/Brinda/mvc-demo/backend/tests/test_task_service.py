import pytest
 
from app.models import User

from app.services.task_services import (

    TaskService, TaskNotFoundError, UserNotFoundError

)

from tests.fakes import FakeTaskRepository, FakeUserRepository
 
def make_service():

    """Build a TaskService with fresh fakes and two known users."""

    alice = User(id=1, name="Alice")

    bob = User(id=2, name="Bob")

    tasks = FakeTaskRepository()

    users = FakeUserRepository([alice, bob])

    return TaskService(tasks, users), alice, bob
 
def test_list_tasks_returns_only_current_users_tasks(): 
    service, alice, bob = make_service()

    service.create_task("Alice's task", alice)

    service.create_task("Bob's task", bob)

    service.create_task("Alice's second task", alice)

    service.create_task("Bob's second task", bob)

    service.create_task("Bob's third task", bob)
 
    tasks = service.list_tasks(alice)

    assert len(tasks) == 2

    assert all(task.owner_id == alice.id for task in tasks)
 
# def test_create_task_strips_whitespace_around_title():

#     """create_task('read_docs', alice) stores title 'read docs.'"""

#     # Hint: after calling create_task, inspect tasks.all_for_user(alice.id)

#     service, alice, bob = make_service()

#     service.create_task("read docs", alice.id)

#     tasks = service.get_user_task(alice.id)

#     assert len(tasks) == 1

#     assert tasks[0].title == "read docs"
 
# def test_get_task_raises_when_id_does_not_exist():

#     """service.get_task(999, alice) raises TaskNotFoundError"""

#     service, alice, bob = make_service()

#     with pytest.raises(TaskNotFoundError):

#         service.get_task(999)
 
# def test_get_task_raises_when_current_user_is_not_owner():

#     """

#     Bob creates a task. Alice calls get_task(bob_task.id, alice).

#     Expected: NotAuthorizedError (NOT TaskNotFoundError - the task exists, but Alice is not allowed to see it)

#     """

#     service, alice, bob = make_service()

#     task = service.create_task("Bob's task", bob.id)

#     with pytest.raises(TaskNotFoundError):

#         service.get_another_user_and_task(task.id, alice)
 
# def test_delete_task_raises_when_current_user_is_not_owner():

#     """

#     Bob creates a task. Alice tries to delete it. Expected: NotAuthorizedError, 

#     and the task is STILL PRESENT in the repository afterwards.

#     """

#     #Hint: verify tsks.find(bob_task.id) is not None after the assertion.

#     service, alice, bob = make_service()

#     task = service.create_task("Bob's task", bob.id)

#     with pytest.raises(TaskNotFoundError):

#         service.delete_others_task(task.id, alice)

#     assert service.get_task(task.id) is not None
 
# def test_delete_own_task_removes_it_from_repository():

#     """Alice creates a task, then deletes it. Afterwards, tasks.find(task.id) is None."""

#     service, alice, bob = make_service()

#     task = service.create_task("Alice's task", alice.id)

#     service.delete_others_task(task.id, alice)

#     with pytest.raises(TaskNotFoundError):

#         service.get_task(task.id)
 