@echo off
set "PYTHONPATH=%~dp0site-packages;%~dp0src;%PYTHONPATH%"
python web_ui_server.py
pause