# Cursor IDE AI 자동화 도구 (크로스 플랫폼)

Windows, macOS, Linux에서 실행 가능한 Cursor IDE AI 자동화 도구입니다.

## 지원 플랫폼

- ✅ **Windows** (Windows 10/11)
- ✅ **macOS** (macOS 10.14+)
- ✅ **Linux** (Ubuntu, CentOS, etc.)

## 설치 및 설정

### 1. 공통 설정

1. Python 3.7+ 설치
2. 프로젝트 디렉토리로 이동
3. 가상환경 생성 (권장)

```bash
python -m venv venv
```

### 2. 플랫폼별 설치

#### Windows

```cmd
# 가상환경 활성화
venv\Scripts\activate

# Windows용 패키지 설치
pip install -r requirements_windows.txt
```

#### macOS

```bash
# 가상환경 활성화
source venv/bin/activate

# macOS용 패키지 설치
pip install -r requirements.txt
```

#### Linux

```bash
# 가상환경 활성화
source venv/bin/activate

# Linux용 패키지 설치
pip install -r requirements_linux.txt

# xdotool 설치 (선택사항)
sudo apt-get install xdotool  # Ubuntu/Debian
sudo yum install xdotool      # CentOS/RHEL
```

## 사용법

### Windows

```cmd
# 자동화 시작
start_automation.bat

# 상태 확인
status_automation.bat

# 중단
stop_automation.bat
```

### macOS/Linux

```bash
# 자동화 시작
./start_automation.sh

# 상태 확인
./status_automation.sh

# 중단
./stop_automation.sh
```

### 직접 실행

```bash
# 일반 모드
python optimized_automation.py

# 백그라운드 모드
python optimized_automation.py --daemon

# 상태 확인
python optimized_automation.py --status

# 중단
python optimized_automation.py --stop
```

## 설정 파일 (config.json)

```json
{
  "description": "Cursor IDE AI 자동화 설정",
  "version": "1.2",
  "activation_delay": 1.0,
  "keystroke_delay": 1.0,
  "enter_delay": 0.5,
  "final_delay": 2.0,
  "chat_focus_enabled": true,
  "chat_click_coordinates": [400, 700],
  "fallback_keyboard_shortcut": "Cmd+L",
  "commands": [
    {
      "interval": 5,
      "max_count": 3,
      "command": "@chainOfThinking.md"
    },
    {
      "interval": 5,
      "max_count": 2,
      "command": "@secondDirection.md"
    },
    {
      "interval": 6,
      "max_count": 4,
      "command": "@finalOrder.md"
    }
  ]
}
```

## 플랫폼별 특징

### Windows
- `pyautogui`와 `pygetwindow`를 사용한 UI 자동화
- `win32gui`를 통한 창 관리
- 배치 파일(.bat)로 쉬운 실행

### macOS
- AppleScript를 통한 네이티브 UI 자동화
- 기존 macOS 전용 기능 유지
- 셸 스크립트(.sh)로 실행

### Linux
- `pyautogui` 또는 `xdotool`을 사용한 UI 자동화
- 다양한 Linux 배포판 지원
- 셸 스크립트(.sh)로 실행

## 문제 해결

### Windows
- **Cursor 창을 찾을 수 없음**: Cursor가 실행 중인지 확인
- **권한 오류**: 관리자 권한으로 실행 시도
- **pyautogui 오류**: `pip install pyautogui` 재설치

### macOS
- **AppleScript 권한 오류**: 시스템 환경설정 > 보안 및 개인정보보호 > 개인정보보호 > 접근성에서 터미널/Python 허용
- **Cursor 활성화 실패**: Cursor가 실행 중인지 확인

### Linux
- **xdotool 오류**: `sudo apt-get install xdotool` 설치
- **pyautogui 오류**: `pip install pyautogui` 재설치
- **디스플레이 오류**: `export DISPLAY=:0` 설정

## 로그 확인

### Windows
```cmd
type %TEMP%\optimized_automation.log
```

### macOS/Linux
```bash
tail -f /tmp/optimized_automation.log
```

## 주의사항

1. **Cursor IDE 실행**: 자동화 실행 전에 Cursor IDE를 열어두세요
2. **채팅창 활성화**: 채팅창이 보이는 상태로 두세요
3. **창 이동 금지**: 자동화 중에는 Cursor IDE 창을 이동하거나 최소화하지 마세요
4. **권한 설정**: macOS에서는 접근성 권한이 필요합니다
5. **방화벽**: Windows 방화벽에서 Python 허용이 필요할 수 있습니다

## 라이선스

MIT License
