@echo off
cd /d %~dp0

echo Installing packages ...
call choco install packages.config -y || goto exit
call refreshenv || goto exit

set /p PYENV_VERSION=<.python-version
echo Installing Python %PYENV_VERSION% ...
call pyenv install %PYENV_VERSION% || goto exit
call pyenv rehash || goto exit

echo Creating virtual environment ...
call python -m venv venv || goto exit

echo Activating virtual environment ...
call venv\Scripts\activate || goto exit

echo Installing dependencies ...
call python -m pip install --upgrade pip || goto exit
call python -m pip install -r requirements.txt || goto exit

:exit
pause
