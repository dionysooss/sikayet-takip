@echo off
cd /d "%~dp0"
if exist ".venv\Scripts\pythonw.exe" (
    start "" ".venv\Scripts\pythonw.exe" main.py
) else (
    echo Virtual environment not found. Trying global python...
    start "" pythonw main.py
)
exit
