#!/bin/bash

echo "=== Cursor IDE 자동화 상태 확인 도구 ==="

# 가상환경 활성화
if [ -d "./venv" ]; then
    source ./venv/bin/activate
fi

# Python 스크립트로 상태 확인
python3 optimized_automation.py --status
