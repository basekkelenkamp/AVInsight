@echo off

where curl >nul 2>nul
if errorlevel 1 (
    echo curl is not installed. Please download and install curl from https://curl.se/windows/ and add it to the PATH.
    echo.
    pause
    exit /b
)

echo Checking if Python 3.8 is installed...
python --version 2>nul | findstr /R "^Python 3.8" >nul
if errorlevel 1 (
    echo Downloading Python 3.8.12 installer...
    curl -o python38.exe https://www.python.org/ftp/python/3.8.12/python-3.8.12-amd64.exe

    echo Installing Python 3.8.12...
    python38.exe /quiet InstallAllUsers=1 PrependPath=1

    echo.
    echo Python installation complete. Please close this Command Prompt and open a new one before proceeding to the next steps.
    pause
) else (
    echo Python 3.8 is already installed.
)

echo Checking if Poetry is installed...
where poetry >nul 2>nul
if errorlevel 1 (
    echo Installing Poetry...
    powershell -Command "Set-ExecutionPolicy RemoteSigned -scope CurrentUser; iwr -useb get.poetry.sh | iex"

    echo.
    echo Poetry installation complete. Please close this Command Prompt and open a new one before proceeding to the next steps.
    pause
) else (
    echo Poetry is already installed.
)

echo Running 'poetry install'...
poetry install

echo.
echo All dependencies installed. You can now use your project.
pause
