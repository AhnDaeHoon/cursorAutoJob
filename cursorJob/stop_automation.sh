#!/bin/bash

echo "=== Cursor IDE 자동화 중단 도구 ==="

# 가상환경 활성화
if [ -d "./venv" ]; then
    source ./venv/bin/activate
fi

# Python 스크립트로 중단 실행
python3 optimized_automation.py --stop

echo ""
echo "중단 완료!"
