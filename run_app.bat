@echo off
set VENV_DIR=venv

REM Check if virtual environment exists
if not exist "%VENV_DIR%\Scripts\activate.bat" (
    echo [INFO] Creating virtual environment...
    python -m venv %VENV_DIR%

    echo [INFO] Installing packages from requirements.txt...
    call %VENV_DIR%\Scripts\activate.bat
    pip install --upgrade pip
    pip install -r requirements.txt
) else (
    echo [INFO] Virtual environment already exists.
)

REM Activate the virtual environment
call %VENV_DIR%\Scripts\activate.bat

REM Start the Streamlit app
echo [INFO] Starting Streamlit app...
streamlit run main.py
