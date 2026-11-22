@echo off
chcp 65001 >nul
title Instalar DROPIA Clips
cd /d "%~dp0"
echo.
echo  Instalando DROPIA Clips. Tarda unos minutos la primera vez.
echo.

set "PY_EXE="
if exist "%LOCALAPPDATA%\Programs\Python\Python313\python.exe" (
  set "PY_EXE=%LOCALAPPDATA%\Programs\Python\Python313\python.exe"
) else (
  for /f "tokens=*" %%i in ('where python 2^>nul') do (
    if not "%%i"=="C:\Program Files\Inkscape\bin\python.exe" (
      if not defined PY_EXE set "PY_EXE=%%i"
    )
  )
)

if not defined PY_EXE (
  echo  Instalando Python 3.13...
  winget install -e --id Python.Python.3.13 --scope user --accept-package-agreements --accept-source-agreements
  echo.
  echo  Python instalado. Cierra esta ventana y vuelve a abrir instalar.bat para terminar.
  pause
  exit /b
)

"%PY_EXE%" instalar.py
pause
