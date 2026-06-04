const BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

export async function listTasks() {
  const res = await fetch(`${BASE}/tasks/`);
  if (!res.ok) throw new Error("Failed to fetch tasks");
  return res.json();
}

export async function createTask(title) {
  const res = await fetch(`${BASE}/tasks/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ title }),
  });
  if (!res.ok) throw new Error("Create failed");
  return res.json();
}

// ADD THIS ENTIRE FUNCTION
export async function completeTask(id) {
  const res = await fetch(`${BASE}/tasks/${id}/complete`, { 
    method: "PATCH" 
  });
  if (!res.ok) throw new Error("Complete failed");
  return res.json();
}
export async function updateTask(id, data) {
  const res = await fetch(`${BASE}/tasks/${id}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data)
  });
  if (!res.ok) throw new Error("Update failed");
  return res.json();
}

export async function deleteTask(id) {
  const res = await fetch(`${BASE}/tasks/${id}`, { method: "DELETE" });
  if (!res.ok) throw new Error("Delete failed");
}