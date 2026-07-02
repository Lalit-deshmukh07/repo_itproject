import { useEffect, useState } from "react";
import {
  isLoggedIn,
  login,
  logout,
  fetchMe,
  fetchTasks,
  createTask,
  deleteTask,
} from "./services/api";

function LoginScreen({ onLogin }) {
  const [name, setName] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState(null);

  async function handleSubmit(e) {
    e.preventDefault();
    try {
      await login(name, password);
      onLogin();
    } catch (e) {
      setError(e.message);
    }
  }

  return (
    <div style={{ maxWidth: 360, margin: "5rem auto", fontFamily: "system-ui" }}>
      <h1>Log in</h1>
      <form
        onSubmit={handleSubmit}
        style={{ display: "flex", flexDirection: "column", gap: 8 }}
      >
        <input
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="username"
          autoFocus
        />
        <input
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          type="password"
          placeholder="password"
        />
        <button type="submit">Log in</button>
      </form>
      {error && <div style={{ color: "crimson", marginTop: 8 }}>{error}</div>}
    </div>
  );
}

function App() {
  const [loggedIn, setLoggedIn] = useState(isLoggedIn());
  const [user, setUser] = useState(null);
  const [tasks, setTasks] = useState([]);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!loggedIn) {
      return;
    }

    async function loadData() {
      try {
        const [me, taskList] = await Promise.all([fetchMe(), fetchTasks()]);
        setUser(me);
        setTasks(taskList);
      } catch (e) {
        setError(e.message);
      }
    }

    loadData();
  }, [loggedIn]);

  async function handleCreateTask(e) {
    e.preventDefault();
    const title = e.target.title.value.trim();
    if (!title) return;

    try {
      const created = await createTask(title, user?.id);
      setTasks((current) => [created, ...current]);
      e.target.reset();
    } catch (e) {
      setError(e.message);
    }
  }

  async function handleDeleteTask(id) {
    try {
      await deleteTask(id);
      setTasks((current) => current.filter((task) => task.id !== id));
    } catch (e) {
      setError(e.message);
    }
  }

  if (!loggedIn) {
    return <LoginScreen onLogin={() => setLoggedIn(true)} />;
  }

  return (
    <div style={{ maxWidth: 720, margin: "2rem auto", fontFamily: "system-ui" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <h1>Tasks</h1>
        <button
          onClick={() => {
            logout();
            setLoggedIn(false);
            setUser(null);
            setTasks([]);
          }}
        >
          Log out
        </button>
      </div>

      {user && <p>Welcome, {user.username}</p>}
      {error && <div style={{ color: "crimson", marginBottom: 12 }}>{error}</div>}

      <form onSubmit={handleCreateTask} style={{ display: "flex", gap: 8, marginBottom: 16 }}>
        <input name="title" placeholder="New task" style={{ flex: 1 }} />
        <button type="submit">Add</button>
      </form>

      <ul style={{ paddingLeft: 20 }}>
        {tasks.map((task) => (
          <li key={task.id} style={{ marginBottom: 8 }}>
            <span>{task.title}</span>
            <button style={{ marginLeft: 8 }} onClick={() => handleDeleteTask(task.id)}>
              Delete
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}

export default App;
 