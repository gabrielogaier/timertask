@echo off
setlocal
cd /d "%~dp0"
title Finalizar Timer Task

echo Procurando processos do Timer Task iniciados por esta pasta...
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0finalizar_timertask.ps1"

echo.
pause
