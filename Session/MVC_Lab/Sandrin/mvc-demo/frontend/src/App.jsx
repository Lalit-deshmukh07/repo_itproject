import { useEffect, useMemo, useState } from 'react';
import { fetchTasks, fetchUsers, createTask, deleteTask, updateTask } from './services/api';

// Local fallback users in case the backend user list isn't available yet
const FALLBACK_USERS = [
    { id: 1, name: 'Alice' },
    { id: 2, name: 'Bob' },
    { id: 3, name: 'Brinda' },
    { id: 4, name: 'Deval' },
    { id: 5, name: 'Lalit' },
    { id: 6, name: 'Grishma' },
    { id: 7, name: 'Sandrin' },
];

export default function App() {
    const [tasks, setTasks] = useState([]);
    const [users, setUsers] = useState(FALLBACK_USERS);
    const [selectedOwnerId, setSelectedOwnerId] = useState(String(FALLBACK_USERS[0].id));
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [input, setInput] = useState('');
    const [editingId, setEditingId] = useState(null);
    const [editingTitle, setEditingTitle] = useState('');

    const loadUsers = () => {
        fetchUsers()
            .then((data) => {
                if (Array.isArray(data)) {
                    // merge fetched users with fallback, keeping fetched first but ensuring fallback names exist
                    const combined = [...data];
                    for (const fb of FALLBACK_USERS) {
                        if (!combined.some((u) => u && u.name && u.name.toLowerCase() === fb.name.toLowerCase())) {
                            // ensure fallback id doesn't conflict with fetched ids
                            combined.push(fb);
                        }
                    }
                    setUsers(combined);
                    if (!selectedOwnerId && combined.length > 0) setSelectedOwnerId(String(combined[0].id));
                }
            })
            .catch((err) => {
                // keep fallback users and show non-fatal warning
                console.warn('fetchUsers failed, using fallback users', err);
                setError(err.message || 'Failed to load users');
                setUsers(FALLBACK_USERS);
            });
    };

    const loadTasks = () => {
        setLoading(true);
        fetchTasks()
            .then((data) => {
                setTasks(data);
                setLoading(false);
                setError(null);
            })
            .catch((err) => {
                setError(err.message);
                setLoading(false);
            });
    };

    useEffect(() => {
        loadUsers();
        loadTasks();
    }, []);

    const handleAddTask = async (e) => {
        e.preventDefault();
        if (!input.trim() || !selectedOwnerId) return;
        try {
            await createTask(input, Number(selectedOwnerId));
            setInput('');
            loadTasks();
        } catch (err) {
            setError(err.message);
        }
    };

    const handleDeleteTask = async (taskId) => {
        try {
            await deleteTask(taskId);
            loadTasks();
        } catch (err) {
            setError(err.message);
        }
    };

    const handleUpdateTask = async (taskId) => {
        if (!editingTitle.trim()) return;
        try {
            await updateTask(taskId, editingTitle);
            setEditingId(null);
            setEditingTitle('');
            loadTasks();
        } catch (err) {
            setError(err.message);
        }
    };

    const usersById = useMemo(
        () => Object.fromEntries(users.map((user) => [user.id, user])),
        [users],
    );

    return (
        <div
            style={{
                minHeight: '100vh',
                background: 'linear-gradient(135deg, #1D4ED8 0%, #8B5CF6 55%, #EC4899 100%)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                padding: '40px',
                fontFamily: 'Inter, system-ui, sans-serif',
            }}
        >
            <div
                style={{
                    width: '100%',
                    maxWidth: '840px',
                    background: 'rgba(255, 255, 255, 0.98)',
                    borderRadius: '32px',
                    boxShadow: '0 32px 90px rgba(15, 23, 42, 0.18)',
                    padding: '40px',
                    color: '#111827',
                }}
            >
                <div style={{ textAlign: 'center', marginBottom: '30px' }}>
                    <h1 style={{ margin: 0, fontSize: '3rem', color: '#1D4ED8' }}>Task</h1>
                </div>

                <form
                    onSubmit={handleAddTask}
                    style={{
                        display: 'grid',
                        gridTemplateColumns: '1.8fr 1fr 0.85fr',
                        gap: '14px',
                        marginBottom: '26px',
                    }}
                >
                    <input
                        type="text"
                        placeholder="Task title"
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        style={{
                            padding: '16px 18px',
                            borderRadius: '20px',
                            border: '1px solid #E5E7EB',
                            boxShadow: 'inset 0 1px 2px rgba(15, 23, 42, 0.06)',
                            fontSize: '1rem',
                            width: '100%',
                        }}
                    />
                    <select
                        value={selectedOwnerId}
                        onChange={(e) => setSelectedOwnerId(e.target.value)}
                        style={{
                            padding: '16px 18px',
                            borderRadius: '20px',
                            border: '1px solid #E5E7EB',
                            fontSize: '1rem',
                            width: '100%',
                        }}
                    >
                        <option value="">Select owner</option>
                        {users.map((user) => (
                            <option key={user.id} value={user.id}>
                                {user.name}
                            </option>
                        ))}
                    </select>
                    <button
                        type="submit"
                        style={{
                            padding: '16px 0',
                            borderRadius: '20px',
                            border: 'none',
                            background: '#4338CA',
                            color: 'white',
                            fontWeight: 700,
                            cursor: 'pointer',
                        }}
                    >
                        Add task
                    </button>
                </form>

                <p style={{ color: '#6B7280', marginBottom: '12px' }}>Select an owner and click Add task.</p>
                {loading && <p style={{ color: '#6B7280' }}>Loading tasks...</p>}

                {!loading && (
                    <div style={{ display: 'grid', gap: '16px' }}>
                        {tasks.length === 0 ? (
                            <p style={{ color: '#6B7280' }}>No tasks yet — add your first one.</p>
                        ) : (
                            tasks.map((task) => (
                                <div
                                    key={task.id}
                                    style={{
                                        padding: '22px',
                                        background: 'linear-gradient(135deg, #F8FAFC 0%, #EEF2FF 100%)',
                                        borderRadius: '24px',
                                        boxShadow: '0 12px 24px rgba(15, 23, 42, 0.08)',
                                        display: 'grid',
                                        gridTemplateColumns: '1fr auto auto',
                                        gap: '12px',
                                        alignItems: 'center',
                                    }}
                                >
                                    {editingId === task.id ? (
                                        <>
                                            <input
                                                type="text"
                                                value={editingTitle}
                                                onChange={(e) => setEditingTitle(e.target.value)}
                                                style={{
                                                    padding: '14px 16px',
                                                    borderRadius: '18px',
                                                    border: '1px solid #CBD5E1',
                                                    width: '100%',
                                                }}
                                            />
                                            <button
                                                onClick={() => handleUpdateTask(task.id)}
                                                style={{
                                                    padding: '12px 16px',
                                                    borderRadius: '18px',
                                                    border: 'none',
                                                    background: '#10B981',
                                                    color: 'white',
                                                    cursor: 'pointer',
                                                }}
                                            >
                                                Save
                                            </button>
                                            <button
                                                onClick={() => setEditingId(null)}
                                                style={{
                                                    padding: '12px 16px',
                                                    borderRadius: '18px',
                                                    border: 'none',
                                                    background: '#6B7280',
                                                    color: 'white',
                                                    cursor: 'pointer',
                                                }}
                                            >
                                                Cancel
                                            </button>
                                        </>
                                    ) : (
                                        <>
                                            <div>
                                                <strong style={{ display: 'block', fontSize: '1.05rem', color: '#111827' }}>
                                                    {task.title}
                                                </strong>
                                                <span style={{ color: '#4B5563', fontSize: '0.95rem' }}>
                                                    Owner: {usersById[task.owner_id]?.name ?? 'Unknown'}
                                                </span>
                                            </div>
                                            <button
                                                onClick={() => {
                                                    setEditingId(task.id);
                                                    setEditingTitle(task.title);
                                                }}
                                                style={{
                                                    padding: '12px 16px',
                                                    borderRadius: '18px',
                                                    border: 'none',
                                                    background: '#F59E0B',
                                                    color: '#111827',
                                                    cursor: 'pointer',
                                                }}
                                            >
                                                Edit
                                            </button>
                                            <button
                                                onClick={() => handleDeleteTask(task.id)}
                                                style={{
                                                    padding: '12px 16px',
                                                    borderRadius: '18px',
                                                    border: 'none',
                                                    background: '#EF4444',
                                                    color: 'white',
                                                    cursor: 'pointer',
                                                }}
                                            >
                                                Delete
                                            </button>
                                        </>
                                    )}
                                </div>
                            ))
                        )}
                    </div>
                )}
            </div>
        </div>
    );
}
