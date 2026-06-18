import { useEffect, useState } from 'react';
import { fetchTasks, createTask, deleteTask, updateTask } from './services/api';

export default function App() {
    const [tasks, setTasks] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [input, setInput] = useState('');
    const [editingId, setEditingId] = useState(null);
    const [editingTitle, setEditingTitle] = useState('');

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
        loadTasks();
    }, []);

    const handleAddTask = async (e) => {
        e.preventDefault();
        if (!input.trim()) return;
        try {
            await createTask(input);
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

    return (
        <div style={{ padding: '24px', fontFamily: 'Arial, sans-serif', maxWidth: '600px' }}>
            <h1>Tasks</h1>
            
            <form onSubmit={handleAddTask} style={{ marginBottom: '24px', display: 'flex', gap: '8px' }}>
                <input
                    type="text"
                    placeholder="New task"
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    style={{
                        padding: '8px 12px',
                        borderRadius: '4px',
                        border: '1px solid #ccc',
                        flex: 1,
                    }}
                />
                <button
                    type="submit"
                    style={{
                        padding: '8px 16px',
                        background: '#007bff',
                        color: 'white',
                        border: 'none',
                        borderRadius: '4px',
                        cursor: 'pointer',
                    }}
                >
                    Add
                </button>
            </form>

            {error && <p style={{ color: '#666', marginBottom: '16px' }}>No task added yet</p>}
            {loading && <p>Loading tasks...</p>}
            
            {!loading && !error && (
                <div style={{ display: 'grid', gap: '12px' }}>
                    {tasks.length === 0 ? (
                        <p style={{ color: '#666' }}>No task added yet</p>
                    ) : (
                        tasks.map((task) => (
                            <div
                                key={task.id}
                                style={{
                                    padding: '16px',
                                    background: '#f7f7f7',
                                    borderRadius: '8px',
                                    boxShadow: '0 1px 4px rgba(0,0,0,0.08)',
                                    display: 'flex',
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
                                                padding: '4px 8px',
                                                borderRadius: '4px',
                                                border: '1px solid #999',
                                                flex: 1,
                                            }}
                                        />
                                        <button
                                            onClick={() => handleUpdateTask(task.id)}
                                            style={{
                                                padding: '4px 8px',
                                                background: '#28a745',
                                                color: 'white',
                                                border: 'none',
                                                borderRadius: '4px',
                                                cursor: 'pointer',
                                            }}
                                        >
                                            Save
                                        </button>
                                        <button
                                            onClick={() => setEditingId(null)}
                                            style={{
                                                padding: '4px 8px',
                                                background: '#6c757d',
                                                color: 'white',
                                                border: 'none',
                                                borderRadius: '4px',
                                                cursor: 'pointer',
                                            }}
                                        >
                                            Cancel
                                        </button>
                                    </>
                                ) : (
                                    <>
                                        <strong style={{ flex: 1 }}>{task.title}</strong>
                                        <button
                                            onClick={() => {
                                                setEditingId(task.id);
                                                setEditingTitle(task.title);
                                            }}
                                            style={{
                                                padding: '4px 8px',
                                                background: '#ffc107',
                                                color: '#333',
                                                border: 'none',
                                                borderRadius: '4px',
                                                cursor: 'pointer',
                                            }}
                                        >
                                            Edit
                                        </button>
                                        <button
                                            onClick={() => handleDeleteTask(task.id)}
                                            style={{
                                                padding: '4px 8px',
                                                background: '#dc3545',
                                                color: 'white',
                                                border: 'none',
                                                borderRadius: '4px',
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
    );
}
