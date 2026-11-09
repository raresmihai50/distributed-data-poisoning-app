@echo off
title Distributed Data Poisoning App Launcher
echo ==========================================================
echo Pornire servicii Distributed Data Poisoning App...
echo ==========================================================

start "Python AI Worker (Port 8000)" powershell -NoExit -Command "cd worker-python; .\venv\Scripts\Activate.ps1; uvicorn main:app --reload --port 8000"
start "Python Blind Evaluator (Port 8001)" powershell -NoExit -Command "cd worker-python; .\venv\Scripts\Activate.ps1; uvicorn evaluator:app --reload --port 8001"
start "Java Backend Spring Boot (Port 8080)" powershell -NoExit -Command "cd backend-java; mvn spring-boot:run"

echo Toate serviciile au fost pornite!