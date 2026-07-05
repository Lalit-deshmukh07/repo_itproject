const BASE = "http://localhost:8000";
 
 
function authHeaders() {
  const token = localStorage.getItem("token");
  return token ? { Authorization: `Bearer ${token}` } : {};
}
 
 
export function isLoggedIn() {
  return !!localStorage.getItem("token");
}
 
export function logout() {
  localStorage.removeItem("token");
}
 
 
export async function login(name, password) {
  const body = new URLSearchParams({ username: name, password });
  const res = await fetch(`${BASE}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body,
  });
  if (!res.ok) throw new Error("Login failed");
  const { access_token } = await res.json();
  localStorage.setItem("token", access_token);
}
 
 
async function authedFetch(url, options = {}) {
  const res = await fetch(url, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...authHeaders(),
      ...options.headers,
    },
  });
  if (res.status === 401) {
    logout();
    window.location.reload();
    throw new Error("Session expired");
  }
  return res;
}
 
 
export async function fetchMe() {
  const res = await authedFetch(`${BASE}/auth/me`);
  if (!res.ok) throw new Error("Failed to load user");
  return res.json();
}
 
export async function fetchTasks() {
  const res = await authedFetch(`${BASE}/tasks/`);
  if (!res.ok) throw new Error("Failed to load tasks");
  return res.json();
}
 
export async function createTask(title ) {
  const res = await authedFetch(`${BASE}/tasks/`, {
    method: "POST",
    body: JSON.stringify({ title}),
  });
  if (!res.ok) throw new Error(`Create failed: ${res.status}`);
  return res.json();
}
 
export async function deleteTask(id) {
  const res = await authedFetch(`${BASE}/tasks/${id}`, { method: "DELETE" });
  if (!res.ok) throw new Error("Delete failed");
}
