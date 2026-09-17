@echo off
title Astra SOAR Demo Launcher
echo ===================================================
echo   Astra SIEM & SOAR - Standalone Demo Launcher
echo ===================================================
echo.
echo Starting Backend (FastAPI on http://localhost:8000)...
start "Astra SOAR - Backend" cmd /k "cd soar_backend && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"

echo Starting Frontend (Vue 3 on http://localhost:5173)...
start "Astra SOAR - Frontend" cmd /k "cd soar_frontend && npm.cmd run dev"

echo.
echo ===================================================
echo Both services are starting in separate windows!
echo Opening browser at: http://localhost:5173 ...
echo ===================================================
timeout /t 4 >nul
start http://localhost:5173
