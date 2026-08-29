@echo off
setlocal EnableExtensions
cd /d "%~dp0"
title Criar executavel - Timer Task

set "APP_EXE=dist\Timer Task.exe"
set "NO_PAUSE=0"
set "BUILD_ICON=.build-assets\timertask.ico"
if /I "%~1"=="--no-pause" set "NO_PAUSE=1"

echo ============================================================
echo  Timer Task - Geracao do executavel
echo ============================================================
echo.

call :find_python
if errorlevel 1 goto :error

if not exist ".venv-build\Scripts\python.exe" (
    echo Criando ambiente de compilacao...
    "%PYTHON_CMD%" -m venv .venv-build
    if errorlevel 1 goto :error
)

set "BUILD_PYTHON=%CD%\.venv-build\Scripts\python.exe"

"%BUILD_PYTHON%" -c "import PyInstaller, PySide6, shiboken6; from PySide6 import QtCore; assert PySide6.__version__ == shiboken6.__version__" >nul 2>&1
if errorlevel 1 (
    echo Reparando ferramentas de compilacao e bibliotecas Qt...
    "%BUILD_PYTHON%" -m pip install --upgrade pip
    if errorlevel 1 goto :error
    "%BUILD_PYTHON%" -m pip install --upgrade --force-reinstall --no-cache-dir -r requirements.txt -r requirements-build.txt
    if errorlevel 1 goto :error
    "%BUILD_PYTHON%" -c "import PyInstaller, PySide6, shiboken6; from PySide6 import QtCore; assert PySide6.__version__ == shiboken6.__version__"
    if errorlevel 1 goto :error
)

if exist build rmdir /s /q build
if exist "%APP_EXE%" del /q "%APP_EXE%"
if exist "Timer Task.spec" del /q "Timer Task.spec"
if not exist ".build-assets" mkdir ".build-assets"
if exist "%BUILD_ICON%" del /q "%BUILD_ICON%"

set "SOURCE_ICON="
for /f "delims=" %%I in ('dir /b /a-d /on "icons\*.ico" 2^>nul') do (
    if not defined SOURCE_ICON set "SOURCE_ICON=icons\%%I"
)

if not defined SOURCE_ICON (
    echo ERRO: nenhum arquivo .ico foi encontrado na pasta icons.
    goto :error
)

echo Usando o icone: %SOURCE_ICON%
copy /y "%SOURCE_ICON%" "%BUILD_ICON%" >nul
if errorlevel 1 goto :error

if not exist "%BUILD_ICON%" (
    echo ERRO: o icone de compilacao nao foi criado.
    goto :error
)

echo.
echo Criando executavel do Timer Task...
"%BUILD_PYTHON%" -m PyInstaller ^
    --noconfirm ^
    --clean ^
    --onefile ^
    --windowed ^
    --name "Timer Task" ^
    --icon "%BUILD_ICON%" ^
    --collect-all PySide6 ^
    --collect-all shiboken6 ^
    --add-data "icons;icons" ^
    --version-file "installer\version_info.txt" ^
    "app.py"
if errorlevel 1 goto :error

if not exist "%APP_EXE%" (
    echo ERRO: o executavel nao foi criado.
    goto :error
)

echo.
echo ============================================================
echo  Executavel criado com sucesso:
echo  %CD%\%APP_EXE%
echo ============================================================

if "%NO_PAUSE%"=="0" (
    start "" "%CD%\dist"
    pause
)
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
echo Instale o Python 3 e marque a opcao Add Python to PATH.
exit /b 1

:error
echo.
echo ============================================================
echo  Nao foi possivel criar o executavel.
echo  Revise as mensagens acima.
echo ============================================================
if "%NO_PAUSE%"=="0" pause
exit /b 1
