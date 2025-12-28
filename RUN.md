# How to Run All Applications

This guide will help you run all three components of LTrail: Backend, Frontend, and SDK.

## Prerequisites

- **Python 3.8+** (Python 3.11 or 3.12 recommended for best compatibility)
- **Node.js 16+** and npm
- **Gemini API Key** (for the example)

## Step-by-Step Instructions

### Option 1: Run in Separate Terminals (Recommended)

#### Terminal 1: Start the Backend

```bash
# Navigate to backend directory
cd backend

# Create virtual environment (if not already created)
python -m venv venv

# Activate virtual environment
# On Windows PowerShell:
.\venv\Scripts\Activate.ps1
# On Windows CMD:
venv\Scripts\activate.bat
# On Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Start the backend server
python main.py
```

The backend will run on `http://localhost:8000`

#### Terminal 2: Start the Frontend

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies (first time only)
npm install

# Start the frontend development server
npm start
```

The frontend will automatically open at `http://localhost:3000`

#### Terminal 3: Run the SDK Example

```bash
# Navigate to SDK directory
cd sdk

# Activate the SDK virtual environment (if using one)
# Or use the same venv as backend

# Install SDK in development mode (first time only)
pip install -e .

# Set your Gemini API key
# On Windows PowerShell:
$env:GEMINI_API_KEY='your-api-key-here'
# On Windows CMD:
set GEMINI_API_KEY=your-api-key-here
# On Linux/Mac:
export GEMINI_API_KEY='your-api-key-here'

# Run the example
python examples/competitor_selection.py
```

### Option 2: Using Scripts (Windows)

#### Create `start-backend.ps1`:

```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python main.py
```

#### Create `start-frontend.ps1`:

```powershell
cd frontend
npm install
npm start
```

#### Create `run-example.ps1`:

```powershell
cd sdk
$env:GEMINI_API_KEY='your-api-key-here'
python examples/competitor_selection.py
```

## Troubleshooting

### Backend Issues

**Problem: pydantic-core build error**
- **Solution**: Use Python 3.11 or 3.12 instead of 3.13, or upgrade pip:
  ```bash
  pip install --upgrade pip
  pip install pydantic --upgrade
  ```

**Problem: Port 8000 already in use**
- **Solution**: Change the port in `backend/main.py`:
  ```python
  uvicorn.run(app, host="0.0.0.0", port=8001)  # Change to 8001
  ```

### Frontend Issues

**Problem: npm install fails**
- **Solution**: Clear cache and reinstall:
  ```bash
  npm cache clean --force
  rm -rf node_modules package-lock.json
  npm install
  ```

**Problem: Port 3000 already in use**
- **Solution**: React will automatically use the next available port, or set it:
  ```bash
  PORT=3001 npm start
  ```

### SDK Issues

**Problem: Module not found errors**
- **Solution**: Install the SDK in development mode:
  ```bash
  cd sdk
  pip install -e .
  ```

**Problem: Backend connection errors**
- **Solution**: Make sure the backend is running on `http://localhost:8000` or set:
  ```bash
  $env:LTRAIL_BACKEND_URL='http://localhost:8000'
  ```

## Verification

1. **Backend**: Open `http://localhost:8000/api/health` - should return `{"status": "healthy"}`
2. **Frontend**: Open `http://localhost:3000` - should show the LTrail Dashboard
3. **SDK**: Run the example - traces should appear in the dashboard

## Quick Start (All-in-One)

If you want to start everything quickly:

```powershell
# Terminal 1
cd backend && python main.py

# Terminal 2 (new terminal)
cd frontend && npm start

# Terminal 3 (new terminal)
cd sdk && $env:GEMINI_API_KEY='your-key' && python examples/competitor_selection.py
```

## Environment Variables

- `GEMINI_API_KEY`: Required for the example (get from Google AI Studio)
- `LTRAIL_BACKEND_URL`: Optional, defaults to `http://localhost:8000`

## Next Steps

Once all three are running:
1. Open the dashboard at `http://localhost:3000`
2. Run the example script
3. Watch traces appear in real-time in the dashboard!

