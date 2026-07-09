# Local Setup Guide

Follow these steps to run the application on your machine:

## Prerequisites
- Python 3.8+
- pip (comes with Python)
- Git

## Installation Steps

### 1. Clone the Repository
```bash
git clone <your-repo-url>
cd repo_itproject
```

### 2. Create Virtual Environment
**On Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**On macOS/Linux:**
```bash
python -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment
```bash
cp .env.example .env
```

Edit `.env` if you need to change any settings (optional for local development).

### 5. Run the Application
```bash
python app.py
```

The app will be available at `http://localhost:5000`

## Troubleshooting

**"ModuleNotFoundError: No module named 'flask'"**
- Make sure you activated the virtual environment
- Run `pip install -r requirements.txt` again

**Port 5000 already in use**
- Edit `app.py` and change the port number in the last line
- Or kill the process using port 5000

**Template not found errors**
- Make sure you're running the command from the root project directory (where `app.py` is located)
