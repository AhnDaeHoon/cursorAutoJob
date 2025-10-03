#!/bin/bash

echo "=== Cursor IDE 자동화 백그라운드 실행 도구 ==="

# 가상환경 활성화
if [ -d "./venv" ]; then
    echo "가상환경 활성화 중..."
    source ./venv/bin/activate
    echo "✅ 가상환경 활성화 완료"
else
    echo "❌ venv 디렉토리를 찾을 수 없습니다!"
    exit 1
fi

# 필요한 패키지 설치
echo "필요한 패키지 확인 중..."
pip install -r requirements.txt

echo ""
echo "백그라운드에서 자동화를 시작합니다..."
echo ""

# 백그라운드 데몬 모드로 실행
python3 optimized_automation.py --daemon

echo ""
echo "✅ 자동화가 백그라운드에서 시작되었습니다!"
echo ""
echo "📋 사용 가능한 명령어:"
echo "   상태 확인: ./status_automation.sh"
echo "   중단하기:  ./stop_automation.sh"
echo "   로그 보기:  tail -f /tmp/optimized_automation.log"
