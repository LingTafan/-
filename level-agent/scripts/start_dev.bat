@echo off
REM 第 1 周：先跑通 CLI。本地 Web 在第 2 周再接。
REM 用法：在 level-agent 目录双击，或：scripts\start_dev.bat

cd /d "%~dp0\.."

if exist ".venv\Scripts\python.exe" (
  ".venv\Scripts\python.exe" run_cli.py --auto-approve %*
) else (
  echo [提示] 未找到 .venv，使用系统 python。建议先：python -m venv .venv ^&^& .venv\Scripts\activate ^&^& pip install -r requirements.txt
  python run_cli.py --auto-approve %*
)

pause
