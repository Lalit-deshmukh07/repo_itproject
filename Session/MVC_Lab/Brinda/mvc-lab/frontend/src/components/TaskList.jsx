import React, { useState, useEffect } from 'react';
import { listTasks, createTask, updateTask, deleteTask } from "../services/api";

function TaskList() {
  const [tasks, setTasks] = useState([]);
  const [newTaskTitle, setNewTaskTitle] = useState('');
  const [editingId, setEditingId] = useState(null);
  const [editText, setEditText] = useState('');

  useEffect(() => {
    loadTasks();
  }, []);

  const loadTasks = async () => {
    const data = await listTasks();
    setTasks(data);
  };

  const handleAddTask = async (e) => {
    e.preventDefault();
    if (!newTaskTitle.trim()) return;
    const newTask = await createTask(newTaskTitle);
    setTasks([...tasks, newTask]);
    setNewTaskTitle('');
  };

  const handleDelete = async (id) => {
    await deleteTask(id);
    setTasks(tasks.filter(task => task.id !== id));
  };

  const handleEditClick = (task) => {
    setEditingId(task.id);
    setEditText(task.title);
  };

  const handleSaveEdit = async (id) => {
    const task = tasks.find(t => t.id === id);
    const updated = await updateTask(id, { 
      title: editText, 
      completed: task.completed 
    });
    setTasks(tasks.map(t => t.id === id ? updated : t));
    setEditingId(null);
  };

  const handleComplete = async (id) => {
    const task = tasks.find(t => t.id === id);
    const updated = await updateTask(id, { 
      title: task.title, 
      completed: !task.completed 
    });
    setTasks(tasks.map(t => t.id === id ? updated : t));
  };

  return (
    <div style={{ padding: '20px', maxWidth: '600px' }}>
      <h1>MVC Lab - Tasks</h1>
      
      <form onSubmit={handleAddTask} style={{ marginBottom: '20px' }}>
        <input
          type="text"
          placeholder="New task"
          value={newTaskTitle}
          onChange={(e) => setNewTaskTitle(e.target.value)}
          style={{ padding: '8px', width: '300px', marginRight: '8px' }}
        />
        <button type="submit" style={{ 
          padding: '8px 16px', 
          background: '#007bff', 
          color: 'white', 
          border: 'none',
          borderRadius: '4px'
        }}>
          Add
        </button>
      </form>

      {tasks.map(task => (
        <div key={task.id} style={{ 
          display: 'flex', 
          alignItems: 'center', 
          marginBottom: '8px',
          padding: '8px',
          borderBottom: '1px solid #eee'
        }}>
          <input
            type="checkbox"
            checked={task.completed}
            onChange={() => handleComplete(task.id)}
          />
          
          {editingId === task.id ? (
            <input
              type="text"
              value={editText}
              onChange={(e) => setEditText(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSaveEdit(task.id)}
              style={{ marginLeft: '8px', flex: 1, padding: '4px' }}
              autoFocus
            />
          ) : (
            <span style={{
              textDecoration: task.completed ? 'line-through' : 'none',
              color: task.completed ? 'gray' : 'black',
              marginLeft: '8px',
              flex: 1
            }}>
              {task.title}
            </span>
          )}

          {editingId === task.id ? (
            <button 
              onClick={() => handleSaveEdit(task.id)}
              style={{ 
                marginLeft: '8px', 
                background: '#28a745', 
                color: 'white',
                border: 'none', 
                padding: '4px 8px',
                borderRadius: '4px'
              }}
            >
              Save
            </button>
          ) : (
            <button 
              onClick={() => handleEditClick(task)}
              style={{ 
                marginLeft: '8px', 
                background: '#ffc107', 
                border: 'none', 
                padding: '4px 8px',
                borderRadius: '4px'
              }}
            >
              Edit
            </button>
          )}
          
          <button 
            onClick={() => handleDelete(task.id)}
            style={{ 
              marginLeft: '8px', 
              background: '#dc3545', 
              color: 'white',
              border: 'none', 
              padding: '4px 8px',
              borderRadius: '4px'
            }}
          >
            Delete
          </button>
        </div>
      ))}
    </div>
  );
}

export default TaskList;