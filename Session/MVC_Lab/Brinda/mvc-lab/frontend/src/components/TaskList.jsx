import { useState, useEffect } from 'react'

const API_URL = 'http://127.0.0.1:8000'

export default function TaskList() {
  const [newTaskTitle, setNewTaskTitle] = useState('')
  const [tasks, setTasks] = useState([])
  const [editingId, setEditingId] = useState(null)
  const [editText, setEditText] = useState('')

  useEffect(() => {
    fetch(`${API_URL}/tasks/`)
      .then(res => res.json())
      .then(data => setTasks(data))
      .catch(err => console.error(err))
  }, [])

  const handleAddTask = async () => {
    if (newTaskTitle.trim() === '') return
    const res = await fetch(`${API_URL}/tasks/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ title: newTaskTitle, description: '', completed: false })
    })
    const newTask = await res.json()
    setTasks([...tasks, newTask])
    setNewTaskTitle('')
  }

  const handleDeleteTask = async (id) => {
    await fetch(`${API_URL}/tasks/${id}`, { method: 'DELETE' })
    setTasks(tasks.filter(task => task.id !== id))
  }

  const handleToggleTask = async (task) => {
    const res = await fetch(`${API_URL}/tasks/${task.id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        title: task.title,
        description: task.description || '',
        completed: !task.completed
      })
    })
    const updated = await res.json()
    setTasks(tasks.map(t => t.id === task.id ? updated : t))
  }

  const handleEditStart = (task) => {
    setEditingId(task.id)
    setEditText(task.title)
  }

  const handleEditSave = async (task) => {
    const res = await fetch(`${API_URL}/tasks/${task.id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        title: editText,
        description: task.description || '',
        completed: task.completed
      })
    })
    const updated = await res.json()
    setTasks(tasks.map(t => t.id === task.id ? updated : t))
    setEditingId(null)
    setEditText('')
  }

  const completedCount = tasks.filter(t => t.completed).length
  const pendingCount = tasks.length - completedCount

  return (
    <div style={{ 
      backgroundImage: 'url(https://images.unsplash.com/photo-1506744038136-46273834b3fb?q=80&w=2070)',
      backgroundSize: 'cover',
      backgroundPosition: 'center',
      backgroundRepeat: 'no-repeat',
      backgroundAttachment: 'fixed',
      minHeight: '100vh', 
      width: '100vw',
      margin: 0,
      padding: '40px 20px',
      fontFamily: 'system-ui, -apple-system, sans-serif',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center'
    }}>
      {/* Floating box - rounded corners, no border = no white lines */}
      <div style={{ 
        backgroundColor: 'rgba(255, 255, 255, 0.95)', 
        backdropFilter: 'blur(10px)',
        WebkitBackdropFilter: 'blur(10px)',
        padding: '35px', 
        borderRadius: '24px', 
        width: '520px', 
        boxShadow: '0 20px 60px rgba(0,0,0,0.3)',
        border: 'none'
      }}>
        <h1 style={{ textAlign: 'center', color: '#2d3748', marginTop: 0, marginBottom: '25px', fontSize: '28px', fontWeight: '700' }}>
          Task Manager
        </h1>
        
        {/* Stats badges */}
        <div style={{ display: 'flex', gap: '8px', justifyContent: 'center', marginBottom: '25px' }}>
          <span style={{ backgroundColor: '#e0e7ff', color: '#4c51bf', padding: '6px 14px', borderRadius: '20px', fontSize: '13px', fontWeight: '600' }}>
            {tasks.length} Total
          </span>
          <span style={{ backgroundColor: '#fef3c7', color: '#d97706', padding: '6px 14px', borderRadius: '20px', fontSize: '13px', fontWeight: '600' }}>
            {pendingCount} Pending
          </span>
          <span style={{ backgroundColor: '#d1fae5', color: '#059669', padding: '6px 14px', borderRadius: '20px', fontSize: '13px', fontWeight: '600' }}>
            {completedCount} Done
          </span>
        </div>

        {/* Input + Add button - orange to purple */}
        <div style={{ display: 'flex', gap: '10px', marginBottom: '20px' }}>
          <input
            type="text"
            placeholder="Add your task's here"
            value={newTaskTitle}
            onChange={(e) => setNewTaskTitle(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleAddTask()}
            style={{ 
              flex: 1, 
              padding: '14px', 
              border: '2px solid #e2e8f0', 
              borderRadius: '12px', 
              backgroundColor: 'white', 
              color: '#2d3748',
              fontSize: '15px',
              outline: 'none'
            }}
          />
          <button onClick={handleAddTask} style={{ 
            background: 'linear-gradient(135deg, #f97316 0%, #a855f7 100%)', 
            color: 'white', 
            border: 'none', 
            borderRadius: '12px', 
            padding: '14px 24px', 
            cursor: 'pointer',
            fontWeight: '600',
            fontSize: '15px',
            boxShadow: '0 4px 12px rgba(249, 115, 22, 0.4)'
          }}>
            Add
          </button>
        </div>

        {/* Task list */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
          {tasks.map((task, index) => (
            <div key={task.id} style={{ 
              backgroundColor: 'rgba(255, 255, 255, 0.98)', 
              padding: '14px 16px', 
              borderRadius: '12px', 
              border: 'none',
              display: 'flex', 
              alignItems: 'center', 
              gap: '12px'
            }}>
              
              <input 
                type="checkbox" 
                checked={task.completed}
                onChange={() => handleToggleTask(task)}
                style={{ cursor: 'pointer', width: '20px', height: '20px' }}
              />
              
              <span style={{ 
                backgroundColor: '#e0e7ff', 
                color: '#4c51bf', 
                padding: '3px 8px', 
                borderRadius: '6px', 
                fontSize: '12px',
                fontWeight: '700'
              }}>
                #{tasks.length - index}
              </span>

              {editingId === task.id ? (
                <input
                  type="text"
                  value={editText}
                  onChange={(e) => setEditText(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && handleEditSave(task)}
                  style={{ 
                    flex: 1, 
                    padding: '6px 10px', 
                    backgroundColor: 'white', 
                    color: '#2d3748', 
                    border: '2px solid #f97316', 
                    borderRadius: '8px',
                    fontSize: '15px',
                    outline: 'none'
                  }}
                  autoFocus
                />
              ) : (
                <span style={{ 
                  flex: 1, 
                  textDecoration: task.completed ? 'line-through' : 'none', 
                  opacity: task.completed ? 0.5 : 1,
                  color: '#2d3748',
                  fontSize: '15px'
                }}>
                  {task.title}
                </span>
              )}

              {/* Soft pastel buttons */}
              {editingId === task.id ? (
                <button onClick={() => handleEditSave(task)} style={{ 
                  backgroundColor: '#86efac', 
                  color: '#14532d', 
                  border: 'none', 
                  borderRadius: '8px', 
                  padding: '6px 12px', 
                  cursor: 'pointer',
                  fontWeight: '600'
                }}>
                  Save
                </button>
              ) : (
                <button onClick={() => handleEditStart(task)} style={{ 
                  backgroundColor: '#93c5fd', 
                  color: '#1e3a8a', 
                  border: 'none', 
                  borderRadius: '8px', 
                  padding: '6px 12px', 
                  cursor: 'pointer',
                  fontWeight: '600'
                }}>
                  Edit
                </button>
              )}
              
              <button onClick={() => handleDeleteTask(task.id)} style={{ 
                backgroundColor: '#fca5a5', 
                color: '#7f1d1d', 
                border: 'none', 
                borderRadius: '8px', 
                padding: '6px 12px', 
                cursor: 'pointer',
                fontWeight: '700',
                fontSize: '16px'
              }}>
                ×
              </button>
            </div>
          ))}
        </div>

        <p style={{ textAlign: 'center', color: '#64748b', marginTop: '20px', fontSize: '13px', fontWeight: '500' }}>
          {pendingCount} task{pendingCount !== 1 ? 's' : ''} remaining
        </p>
      </div>
    </div>
  )
}