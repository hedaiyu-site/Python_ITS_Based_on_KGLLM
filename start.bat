@echo off
echo Starting Python Learning Assistant...
echo.
echo Starting FastAPI server...
start /b python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

timeout /t 3 /nobreak > nul

echo.
echo Server is running at:
echo   - API: http://localhost:8000
echo   - Web: http://localhost:8000/
echo   - Docs: http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop the server
pause
