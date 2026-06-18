# Running the Task App Locally

## Prerequisites
- Python 3.9+
- Node.js 16+

## Backend Setup

1. **Install Python dependencies:**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. **Start the backend server:**
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

You should see:
```
Uvicorn running on http://127.0.0.1:8000
```

Test the backend is working:
```bash
curl http://localhost:8000/users
```

You should get a JSON list of users.

## Frontend Setup (in another terminal)

1. **Install dependencies:**
   ```bash
   cd frontend
   npm install
   ```

2. **Start the dev server:**
   ```bash
   npm run dev
   ```

You should see:
```
VITE v... ready in ... ms

➜  Local:   http://localhost:3000/
```

## Test the App

1. Open http://localhost:3000 in your browser
2. You should see the Task app with a list of owners (Alice, Bob, Brinda, Deval, Lalit, Grishma, Sandrin)
3. Try:
   - Selecting an owner from the dropdown
   - Typing a task title
   - Clicking "Add task"
   - Edit/delete tasks

## Troubleshooting

**If you see "Failed to fetch tasks":**
- Ensure backend is running on port 8000
- Check browser console (F12) for network errors
- The vite.config.js proxy is set to `http://localhost:8000`

**If tasks don't persist:**
- Check that `backend/tasks.db` file exists and is writable

**Backend import errors:**
- Ensure you're in the `backend/` directory when installing requirements
- Run `pip install -r requirements.txt` again if needed

## Database Reset

To reset the database and start fresh:
```bash
rm backend/tasks.db
# Then restart the backend
```
