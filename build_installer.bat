@echo off
setlocal EnableExtensions
cd /d "%~dp0"
title Criar instalador - Timer Task

set "APP_EXE=dist\Timer Task.exe"
set "SETUP_FILE=dist\installer\TimerTask-Setup.exe"
set "ISCC="

echo ============================================================
echo  Timer Task - Geracao do instalador
echo ============================================================
echo.

echo Etapa 1 de 2: criando o executavel...
call "%~dp0build_executavel.bat" --no-pause
if errorlevel 1 goto :error

if not exist "%APP_EXE%" (
    echo ERRO: o executavel necessario para o instalador nao foi encontrado.
    goto :error
)

echo.
echo Etapa 2 de 2: preparando o instalador...
call :find_inno
if errorlevel 1 goto :error

if exist "%SETUP_FILE%" del /q "%SETUP_FILE%"

echo.
echo Criando instalador...
"%ISCC%" "installer\setup.iss"
if errorlevel 1 goto :error

if not exist "%SETUP_FILE%" (
    echo ERRO: o instalador nao foi criado.
    goto :error
)

echo.
echo ============================================================
echo  Instalador criado com sucesso:
echo  %CD%\%SETUP_FILE%
echo ============================================================
start "" "%CD%\dist\installer"
pause
exit /b 0

:find_inno
for %%I in (
    "%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe"
    "%ProgramFiles%\Inno Setup 6\ISCC.exe"
    "%LocalAppData%\Programs\Inno Setup 6\ISCC.exe"
) do (
    if exist "%%~I" (
        set "ISCC=%%~I"
        exit /b 0
    )
)

where winget >nul 2>&1
if errorlevel 1 (
    echo Inno Setup 6 nao foi encontrado e o winget nao esta disponivel.
    echo Instale o Inno Setup 6 e execute este arquivo novamente.
    exit /b 1
)

echo.
echo Inno Setup 6 nao encontrado. Instalando pelo winget...
winget install --id JRSoftware.InnoSetup -e --accept-package-agreements --accept-source-agreements
if errorlevel 1 (
    echo Nao foi possivel instalar o Inno Setup automaticamente.
    exit /b 1
)

for %%I in (
    "%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe"
    "%ProgramFiles%\Inno Setup 6\ISCC.exe"
    "%LocalAppData%\Programs\Inno Setup 6\ISCC.exe"
) do (
    if exist "%%~I" (
        set "ISCC=%%~I"
        exit /b 0
    )
)

echo O Inno Setup foi instalado, mas o compilador ISCC.exe nao foi localizado.
exit /b 1

:error
echo.
echo ============================================================
echo  Nao foi possivel criar o instalador.
echo  Revise as mensagens acima.
echo ============================================================
pause
exit /b 1
