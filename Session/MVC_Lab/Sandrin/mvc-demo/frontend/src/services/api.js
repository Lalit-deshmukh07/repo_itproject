const BASE = 'http://localhost:8000';

function getToken() {
    return localStorage.getItem('token');
}

function authHeaders() {
    const token = getToken();
    return token ? { Authorization: `Bearer ${token}` } : {};
}

export async function fetchTasks() {
    const res = await fetch(`${BASE}/tasks/tasks`, {
        headers: {
            ...authHeaders(),
        },
    });
    if (!res.ok) throw new Error('Failed to fetch tasks');
    return res.json();
}

export async function fetchUsers() {
    const res = await fetch(`${BASE}/users/`, {
        headers: {
            ...authHeaders(),
        },
    });
    if (!res.ok) throw new Error('Failed to fetch users');
    return res.json();
}

export async function fetchCurrentUser() {
    const res = await fetch(`${BASE}/auth/me`, {
        headers: {
            ...authHeaders(),
        },
    });
    if (!res.ok) throw new Error('Failed to fetch current user');
    return res.json();
}

export async function createTask(title) {
    const res = await fetch(`${BASE}/tasks/tasks`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            ...authHeaders(),
        },
        body: JSON.stringify({ title }),
    });
    if (!res.ok) throw new Error('Failed to create task');
    return res.json();
}

export async function updateTask(taskId, title) {
    const res = await fetch(`${BASE}/tasks/tasks/${taskId}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
            ...authHeaders(),
        },
        body: JSON.stringify({ title }),
    });
    if (!res.ok) throw new Error('Failed to update task');
    return res.json();
}

export async function deleteTask(taskId) {
    const res = await fetch(`${BASE}/tasks/tasks/${taskId}`, {
        method: 'DELETE',
        headers: {
            ...authHeaders(),
        },
    });
    if (!res.ok) throw new Error('Failed to delete task');
}

export async function login(username, password) {
    const body = new URLSearchParams();
    body.append('username', username);
    body.append('password', password);

    const res = await fetch(`${BASE}/auth/login`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body,
    });

    if (!res.ok) {
        const error = await res.json().catch(() => null);
        throw new Error(error?.detail || 'Login failed');
    }

    const data = await res.json();
    localStorage.setItem('token', data.access_token);
    return data;
}

export async function register(name, password) {
    const res = await fetch(`${BASE}/auth/register`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ name, password }),
    });

    if (!res.ok) {
        const error = await res.json().catch(() => null);
        throw new Error(error?.detail || 'Registration failed');
    }

    return res.json();
}

export function logout() {
    localStorage.removeItem('token');
}

export function isLoggedIn() {
    return Boolean(getToken());
}
