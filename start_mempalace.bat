@echo off
setlocal

rem GitHub-safe launcher template for Windows users.
rem Override any of these before calling the script if your setup is different.

if not defined ENV_NAME set "ENV_NAME=mempalace"
if not defined PROJECT_DIR set "PROJECT_DIR=%~dp0"
if not defined PALACE_PATH set "PALACE_PATH=%USERPROFILE%\.mempalace\palace"
if not defined MEMPALACE_EMBEDDING_CACHE_PATH set "MEMPALACE_EMBEDDING_CACHE_PATH=%USERPROFILE%\.mempalace\cache\onnx_models"

if not defined CONDA_ROOT (
  if exist "D:\anaconda\Scripts\activate.bat" (
    set "CONDA_ROOT=D:\anaconda"
  ) else if exist "%USERPROFILE%\anaconda3\Scripts\activate.bat" (
    set "CONDA_ROOT=%USERPROFILE%\anaconda3"
  ) else if exist "%USERPROFILE%\miniconda3\Scripts\activate.bat" (
    set "CONDA_ROOT=%USERPROFILE%\miniconda3"
  )
)

if not defined CONDA_ROOT (
  echo [ERROR] Could not find a Conda installation.
  echo         Set CONDA_ROOT before running this script.
  echo         Example: set CONDA_ROOT=D:\anaconda
  pause
  exit /b 1
)

if not exist "%CONDA_ROOT%\Scripts\activate.bat" (
  echo [ERROR] Conda activate script not found:
  echo         %CONDA_ROOT%\Scripts\activate.bat
  pause
  exit /b 1
)

if not exist "%PROJECT_DIR%" (
  echo [ERROR] Project directory not found:
  echo         %PROJECT_DIR%
  pause
  exit /b 1
)

if not exist "%PALACE_PATH%" mkdir "%PALACE_PATH%"
if not exist "%MEMPALACE_EMBEDDING_CACHE_PATH%" mkdir "%MEMPALACE_EMBEDDING_CACHE_PATH%"

call "%CONDA_ROOT%\Scripts\activate.bat" %ENV_NAME%
if errorlevel 1 (
  echo [ERROR] Failed to activate conda environment: %ENV_NAME%
  pause
  exit /b 1
)

cd /d "%PROJECT_DIR%"
set "MEMPALACE_PALACE_PATH=%PALACE_PATH%"
title MemPalace Extended Shell

echo.
echo MemPalace Extended shell is ready.
echo.
echo   Conda env       : %ENV_NAME%
echo   Project         : %PROJECT_DIR%
echo   Palace DB       : %PALACE_PATH%
echo   Embedding cache : %MEMPALACE_EMBEDDING_CACHE_PATH%
echo.
echo Common commands:
echo   mempalace status
echo   mempalace init "C:\path\to\your\project"
echo   mempalace mine "C:\path\to\your\project"
echo   mempalace watch start "C:\path\to\your\project"
echo   mempalace search "query"
echo   python -m mempalace.mcp_server --palace "%PALACE_PATH%"
echo.

cmd /k
