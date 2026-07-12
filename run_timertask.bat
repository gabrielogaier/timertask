@echo off
setlocal
cd /d "%~dp0"
title Timer Task - Inicializacao

call :find_python
if errorlevel 1 exit /b 1

if not exist ".venv\Scripts\python.exe" (
    echo Criando ambiente virtual...
    "%PYTHON_CMD%" -m venv .venv
    if errorlevel 1 (
        echo.
        echo Nao foi possivel criar o ambiente virtual.
        pause
        exit /b 1
    )
)

set "VENV_PYTHON=%CD%\.venv\Scripts\python.exe"
set "VENV_PYTHONW=%CD%\.venv\Scripts\pythonw.exe"

"%VENV_PYTHON%" -c "import PySide6" >nul 2>&1
if errorlevel 1 (
    echo Instalando dependencias do Timer Task...
    "%VENV_PYTHON%" -m pip install --upgrade pip
    if errorlevel 1 goto :install_error
    "%VENV_PYTHON%" -m pip install -r requirements.txt
    if errorlevel 1 goto :install_error
)

start "" "%VENV_PYTHONW%" "%CD%\app.py"
exit /b 0

:find_python
where py >nul 2>&1
if not errorlevel 1 (
    set "PYTHON_CMD=py"
    exit /b 0
)
where python >nul 2>&1
if not errorlevel 1 (
    set "PYTHON_CMD=python"
    exit /b 0
)
echo Python 3 nao foi encontrado.
echo Instale o Python 3 e marque a opcao "Add Python to PATH".
pause
exit /b 1

:install_error
echo.
echo Falha ao instalar as dependencias.
echo Execute run_debug.bat para ver mais detalhes.
pause
exit /b 1
