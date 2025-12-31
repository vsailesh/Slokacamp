# 🚀 How to Run the Complete Project

This guide will help you run both the **Django Backend** and **React Frontend** together.

## Prerequisites

- **Python 3.8+** (for Django backend)
- **Node.js 16+** and **Yarn** (for React frontend)
- **SQLite** (included with Python, no setup needed)

## Quick Start (Automated)

Run the startup script:

```bash
chmod +x start.sh
./start.sh
```

This will start both backend and frontend in separate terminal windows.

---

## Manual Setup

### Step 1: Backend Setup (Django)

1. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Create and activate virtual environment (recommended):**
   ```bash
   # Create virtual environment
   python3 -m venv venv
   
   # Activate it
   source venv/bin/activate  # On macOS/Linux
   # OR
   venv\Scripts\activate  # On Windows
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run migrations:**
   ```bash
   python manage.py migrate
   ```

5. **Create superuser (optional, for admin access):**
   ```bash
   python manage.py createsuperuser
   ```

6. **Seed sample data (optional):**
   ```bash
   python seed_data.py
   ```

7. **Start the Django server:**
   ```bash
   python manage.py runserver
   ```
   
   Backend will run on: **http://localhost:8000**

### Step 2: Frontend Setup (React)

1. **Open a new terminal and navigate to frontend:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   yarn install
   # OR
   npm install
   ```

3. **Create environment file (if needed):**
   ```bash
   # Create .env file in frontend directory
   echo "REACT_APP_BACKEND_URL=http://localhost:8000" > .env
   ```

4. **Start the React development server:**
   ```bash
   yarn start
   # OR
   npm start
   ```
   
   Frontend will run on: **http://localhost:3000**

---

## Running Both Services

### Option 1: Two Terminal Windows (Recommended)

**Terminal 1 - Backend:**
```bash
cd backend
source venv/bin/activate  # If using virtual environment
python manage.py runserver
```

**Terminal 2 - Frontend:**
```bash
cd frontend
yarn start
```

### Option 2: Background Processes

**Start backend in background:**
```bash
cd backend
source venv/bin/activate
python manage.py runserver > backend.log 2>&1 &
```

**Start frontend in background:**
```bash
cd frontend
yarn start > frontend.log 2>&1 &
```

**Stop background processes:**
```bash
# Find and kill processes
pkill -f "manage.py runserver"
pkill -f "react-scripts"
```

---

## Access Points

Once both services are running:

- **Frontend (React)**: http://localhost:3000
- **Backend API**: http://localhost:8000/api/
- **Django Admin**: http://localhost:8000/admin/
- **API Documentation**: http://localhost:8000/api/docs/

---

## Default Credentials

After running `seed_data.py`:

- **Email**: `admin@slokcamp.com`
- **Password**: `Admin@123`

---

## Troubleshooting

### Backend Issues

**Port already in use:**
```bash
# Use a different port
python manage.py runserver 8001
```

**Database errors:**
```bash
# Delete and recreate database
rm db.sqlite3
python manage.py migrate
python seed_data.py
```

**Module not found:**
```bash
# Make sure virtual environment is activated
source venv/bin/activate
pip install -r requirements.txt
```

### Frontend Issues

**Port 3000 already in use:**
```bash
# React will ask to use a different port, or:
PORT=3001 yarn start
```

**Backend connection errors:**
- Check that backend is running on port 8000
- Verify `.env` file has correct `REACT_APP_BACKEND_URL`
- Check browser console for CORS errors

**Module not found:**
```bash
# Reinstall dependencies
rm -rf node_modules
yarn install
```

### CORS Issues

If you see CORS errors, make sure backend `settings.py` has:
```python
CORS_ALLOWED_ORIGINS = ['http://localhost:3000']
```

---

## Environment Variables

### Backend (.env in backend directory)
```env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ORIGINS=http://localhost:3000
```

### Frontend (.env in frontend directory)
```env
REACT_APP_BACKEND_URL=http://localhost:8000
```

---

## Next Steps

1. ✅ Backend running on port 8000
2. ✅ Frontend running on port 3000
3. ✅ Open http://localhost:3000 in your browser
4. ✅ Sign in with admin credentials
5. ✅ Start developing!

---

## Production Build

### Build Frontend:
```bash
cd frontend
yarn build
```

### Run Backend with Gunicorn:
```bash
cd backend
gunicorn slokcamp.wsgi:application --bind 0.0.0.0:8000
```

---

## Need Help?

- Check `MIGRATION_COMPLETE.md` for detailed documentation
- Check `DEPLOYMENT_READY.md` for deployment info
- Check API docs at http://localhost:8000/api/docs/

