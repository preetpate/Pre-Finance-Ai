@echo off
echo Starting Pre-Finance AI backend server...
call venv\Scripts\activate.bat
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
pause
