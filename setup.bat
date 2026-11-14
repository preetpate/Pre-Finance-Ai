@echo off
echo ============================================================
echo  Pre-Finance AI – First-time setup
echo ============================================================
echo.

REM 1. Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found. Install Python 3.11+ from python.org
    pause & exit /b 1
)
echo [OK] Python found

REM 2. Create virtual environment
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)
echo [OK] Virtual environment ready

REM 3. Activate and install
call venv\Scripts\activate.bat
echo Installing Python dependencies (this may take a few minutes)...
pip install -r requirements.txt --quiet

REM 4. Copy .env if missing
if not exist ".env" (
    copy ".env.example" ".env"
    echo [OK] .env file created from template. Edit it if needed.
)

REM 5. Create data directories
if not exist "data\uploads" mkdir "data\uploads"
if not exist "data\vector_store" mkdir "data\vector_store"

echo.
echo ============================================================
echo  Setup complete!
echo.
echo  To start the server run:
echo    start_server.bat
echo.
echo  Then open:
echo    http://localhost:5500/frontend/login.html  (user)
echo    Admin login: admin@prefinance.ai / Admin@123456
echo ============================================================
pause
