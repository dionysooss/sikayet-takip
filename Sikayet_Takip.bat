@echo off
REM Şikayet Takip Sistemi Başlatıcı
cd /d "%~dp0"
call .venv\Scripts\activate.bat
python main.py
pause
