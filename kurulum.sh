#!/bin/bash
cd "$(dirname "$0")"
echo "Kurulum basliyor..."
python3 -m venv .venv
source .venv/bin/activate
pip install customtkinter pillow psycopg2-binary python-dotenv reportlab tkcalendar
echo "Kurulum tamamlandi!"
python main.py
