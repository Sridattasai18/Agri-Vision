@echo off
echo Starting Crop Recommendation System...
echo.
echo Starting Backend...
start "Backend" cmd /k "cd backend && call venv\Scripts\activate.bat && python app.py"
timeout /t 3 /nobreak >nul
echo.
echo Starting Frontend...
start "Frontend" cmd /k "cd frontend && python -m http.server 8000"
echo.
echo Both servers started!
echo Frontend: http://127.0.0.1:8000
echo Backend: http://127.0.0.1:5000
pause
