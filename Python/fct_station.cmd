@echo off
cd /d %~dp0

echo Activating virtual environment ...
call venv\Scripts\activate || goto exit

rem Start station server without bothering to return control to the parent
rem batch program. An undiagnosed bug in OpenHTF causes the server to hang
rem when a keyboard interrupt is received, which requires closing the window.
python -m tests.fct_test -v --config-file config.yaml

:exit
pause
