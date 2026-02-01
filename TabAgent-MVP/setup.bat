@echo off
REM Tab Agent MVP - Windows Setup Script

echo ============================================================
echo Tab Agent MVP - Automated Setup
echo ============================================================
echo.

REM Check Python
echo Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found. Install Python 3.8+ from python.org
    pause
    exit /b 1
)

python --version
echo.

REM Create virtual environment
echo Creating virtual environment...
if exist env\ (
    echo ⚠️  env\ already exists. Skipping...
) else (
    python -m venv env
    echo ✅ Virtual environment created
)
echo.

REM Activate
echo Activating virtual environment...
call env\Scripts\activate.bat

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip -q

REM Install dependencies
echo Installing dependencies...
echo (This may take 2-3 minutes)
echo.

pip install -r requirements.txt

echo.
echo ✅ Dependencies installed
echo.

REM Test installation
echo Testing installation...
python test_pipeline.py

echo.
echo ============================================================
echo ✅ SETUP COMPLETE
echo ============================================================
echo.
echo Next steps:
echo   1. env\Scripts\activate.bat
echo   2. Add audio to input\
echo   3. python main.py your_song.wav
echo.
echo See QUICKSTART.md for more details
echo.
pause
