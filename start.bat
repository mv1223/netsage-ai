@echo off
title NetSage AI launcher
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
  echo Python venv is missing. Run: python -m venv .venv
  echo Then: .venv\Scripts\activate
  echo Then: pip install -r requirements.txt
  pause
  exit /b 1
)

if not exist "frontend\node_modules\" (
  echo Installing frontend packages. This is only needed once.
  cd frontend
  call npm install
  cd ..
)

echo Starting the API on port 8000...
start "NetSage API" cmd /k "cd /d "%~dp0backend" && "%~dp0.venv\Scripts\python.exe" -m uvicorn main:app --reload --port 8000"

echo Starting the website on port 5173...
start "NetSage UI" cmd /k "cd /d "%~dp0frontend" && npm run dev"

echo Waiting a few seconds, then opening the browser...
timeout /t 4 /nobreak >nul
start http://127.0.0.1:5173

echo.
echo Open this address in the browser:
echo   http://127.0.0.1:5173
echo.
echo Do NOT use http://127.0.0.1:8000 for the website.
echo Keep both new windows open while you use the app.
echo.
pause
