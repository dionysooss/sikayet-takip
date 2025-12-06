@echo off
chcp 65001 >nul
cd /d "%~dp0"
"C:\Users\devra\AppData\Local\Python\pythoncore-3.14-64\python.exe" main.py
if errorlevel 1 pause
