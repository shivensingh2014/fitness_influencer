@echo off
:: ── Genfluence One-Click Runner ─────────────────────────
:: Double-click this file to run the full pipeline.
cd /d "%~dp0"
call "..\env\Scripts\activate.bat"
python main.py
pause
