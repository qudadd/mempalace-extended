@echo off
setlocal

rem GitHub-safe MCP launcher for Windows.
rem This script is intended for MCP clients that need one stable command path.
rem Override any of these variables in the client config if your setup differs.

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
  echo [ERROR] Could not find a Conda installation. 1>&2
  echo         Set CONDA_ROOT before launching this script. 1>&2
  exit /b 1
)

if not exist "%CONDA_ROOT%\Scripts\activate.bat" (
  echo [ERROR] Conda activate script not found: %CONDA_ROOT%\Scripts\activate.bat 1>&2
  exit /b 1
)

call "%CONDA_ROOT%\Scripts\activate.bat" %ENV_NAME%
if errorlevel 1 (
  echo [ERROR] Failed to activate conda environment: %ENV_NAME% 1>&2
  exit /b 1
)

cd /d "%PROJECT_DIR%"
set "MEMPALACE_PALACE_PATH=%PALACE_PATH%"
set "PYTHONIOENCODING=utf-8"

if /i "%~1"=="--check" (
  echo MemPalace Extended MCP launcher
  echo   Conda env       : %ENV_NAME%
  echo   Project         : %PROJECT_DIR%
  echo   Palace DB       : %PALACE_PATH%
  echo   Embedding cache : %MEMPALACE_EMBEDDING_CACHE_PATH%
  python -c "import sys; print('  Python          :', sys.executable)"
  exit /b 0
)

python -m mempalace.mcp_server --palace "%PALACE_PATH%"
