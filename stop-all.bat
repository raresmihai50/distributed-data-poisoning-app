@echo off
title Distributed Data Poisoning App Terminator
echo ==========================================================
echo Oprire servicii (Porturile 5173, 8000, 8001, 8080)...
echo ==========================================================

powershell -Command "Get-NetTCPConnection -LocalPort 5173, 8000, 8001, 8080 -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess -Unique | ForEach-Object { Stop-Process -Id $_ -Force -ErrorAction SilentlyContinue }"

echo Gata! Toate cele 4 servicii au fost oprite si porturile eliberate.
timeout /t 3