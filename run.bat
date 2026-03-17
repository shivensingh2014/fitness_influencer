@echo off
:: ── Genfluence One-Click Runner ─────────────────────────
:: Double-click this file to run the full pipeline.
cd /d "%~dp0"
call ".venv\Scripts\activate.bat"
python main.py
pause
