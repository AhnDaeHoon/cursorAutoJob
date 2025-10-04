@echo off
REM Cursor IDE 자동화 상태 확인 도구 (Windows)

echo === Cursor IDE 자동화 상태 확인 도구 ===

REM 가상환경 활성화 (있는 경우)
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
)

REM 자동화 상태 확인
python optimized_automation.py --status

pause
