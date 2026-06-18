const BASE = 'http://localhost:8000';

export async function fetchTasks() {
    const res = await fetch(`${BASE}/tasks`);
    if (!res.ok) throw new Error('Failed to fetch tasks');
    return res.json();
}

export async function fetchUsers() {
    const res = await fetch(`${BASE}/users`);
    if (!res.ok) throw new Error('Failed to fetch users');
    return res.json();
}

export async function createTask(title, owner_id) {
    const res = await fetch(`${BASE}/tasks`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title, owner_id }),
    });
    if (!res.ok) throw new Error('Failed to create task');
    return res.json();
}

export async function updateTask(taskId, title) {
    const res = await fetch(`${BASE}/tasks/${taskId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title }),
    });
    if (!res.ok) throw new Error('Failed to update task');
    return res.json();
}

export async function deleteTask(taskId) {
    const res = await fetch(`${BASE}/tasks/${taskId}`, {
        method: 'DELETE',
    });
    if (!res.ok) throw new Error('Failed to delete task');
}
