@echo off
REM Cursor IDE 자동화 백그라운드 실행 도구 (Windows)

echo === Cursor IDE 자동화 백그라운드 실행 도구 ===

REM 가상환경 활성화 (있는 경우)
if exist "venv\Scripts\activate.bat" (
    echo 가상환경 활성화 중...
    call venv\Scripts\activate.bat
    echo ✅ 가상환경 활성화 완료
) else (
    echo ⚠️  가상환경을 찾을 수 없습니다. 시스템 Python을 사용합니다.
)

REM 필요한 패키지 확인
echo 필요한 패키지 확인 중...
pip install -r requirements.txt

REM 백그라운드에서 자동화 시작
echo 백그라운드에서 자동화를 시작합니다...
python optimized_automation.py --daemon

echo ✅ 자동화가 백그라운드에서 시작되었습니다!
echo 📋 사용 가능한 명령어:
echo    상태 확인: status_automation.bat
echo    중단하기:  stop_automation.bat
echo    로그 보기:  type %TEMP%\optimized_automation.log

pause
