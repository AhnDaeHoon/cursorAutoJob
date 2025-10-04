@echo off
REM Cursor IDE 자동화 중단 도구 (Windows)

echo === Cursor IDE 자동화 중단 도구 ===

REM 가상환경 활성화 (있는 경우)
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
)

REM 자동화 프로세스 중단
python optimized_automation.py --stop

echo 중단 완료!
pause
