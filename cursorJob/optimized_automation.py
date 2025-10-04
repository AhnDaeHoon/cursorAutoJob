#!/usr/bin/env python3
"""
최적화된 Cursor IDE AI 자동화 스크립트 (크로스 플랫폼)
UI 요소를 한 번 찾아서 재사용하는 방식
Windows, macOS, Linux 지원
"""

import time
import subprocess
import psutil
import os
import sys
import signal
import argparse
import json
import platform
from datetime import datetime

# 플랫폼별 UI 자동화 라이브러리 import
try:
    if platform.system() == "Windows":
        import pyautogui
        import pygetwindow as gw
        import win32gui
        import win32con
        import win32api
        import win32process
    elif platform.system() == "Darwin":  # macOS
        import subprocess
    elif platform.system() == "Linux":
        import subprocess
        try:
            import pyautogui
        except ImportError:
            pass
except ImportError as e:
    print(f"⚠️  일부 UI 자동화 라이브러리가 설치되지 않았습니다: {e}")
    print("Windows의 경우: pip install pyautogui pygetwindow pywin32")
    print("Linux의 경우: pip install pyautogui")

class OptimizedCursorAutomation:
    def __init__(self, daemon_mode=False):
        self.daemon_mode = daemon_mode
        self.config_file = "config.json"
        self.script_name = "optimized_automation.py"
        self.platform = platform.system()
        
        # 플랫폼별 파일 경로 설정
        if self.platform == "Windows":
            self.pid_file = os.path.join(os.environ.get('TEMP', 'C:\\temp'), 'optimized_automation.pid')
            self.log_file = os.path.join(os.environ.get('TEMP', 'C:\\temp'), 'optimized_automation.log')
        else:
            self.pid_file = "/tmp/optimized_automation.pid"
            self.log_file = "/tmp/optimized_automation.log"
        
        self.running = True
        
        # config 로드
        self.config = self.load_config()
        self.commands = self.config.get('commands', [])  # 명령 목록
        self.current_command_index = 0  # 현재 실행 중인 명령 인덱스
        self.count = 0
        self.total_commands = len(self.commands)
        
        # 첫 번째 명령이 있으면 기본값으로 설정
        if self.commands:
            self.current_command = self.commands[0]
            self.interval = self.current_command.get('interval', 10)
            self.max_count = self.current_command.get('max_count', 10)
            self.command = self.current_command.get('command', '@2.test.md')
        else:
            # 기본값 설정 (하위 호환성)
            self.interval = self.config.get('interval', 10)
            self.max_count = self.config.get('max_count', 10)
            self.command = self.config.get('command', '@2.test.md')
            self.current_command = {
                'interval': self.interval,
                'max_count': self.max_count,
                'command': self.command
            }
        
        # 딜레이 설정 (설정 파일에서 가져오거나 기본값 사용)
        self.delays = {
            'activation': self.config.get('activation_delay', 1.0),
            'keystroke': self.config.get('keystroke_delay', 1.0),
            'enter': self.config.get('enter_delay', 0.5),
            'final': self.config.get('final_delay', 2.0),
            'chat_click': self.config.get('chat_click_delay', 0.5)
        }
        
        # 채팅창 포커스 설정
        self.chat_focus_enabled = self.config.get('chat_focus_enabled', True)
        self.chat_click_coordinates = self.config.get('chat_click_coordinates', [400, 700])
        self.fallback_shortcut = self.config.get('fallback_keyboard_shortcut', 'Cmd+L')
    
    def load_config(self):
        """config.json 파일에서 설정을 로드"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.log_message(f"✅ 설정 파일 로드 성공: {self.config_file}")
                    return config
            else:
                self.log_message(f"⚠️  설정 파일이 없습니다: {self.config_file}")
                self.log_message("기본값을 사용합니다.")
                return {}
        except json.JSONDecodeError as e:
            self.log_message(f"❌ 설정 파일 JSON 파싱 오류: {e}")
            self.log_message("기본값을 사용합니다.")
            return {}
        except Exception as e:
            self.log_message(f"❌ 설정 파일 로드 오류: {e}")
            self.log_message("기본값을 사용합니다.")
            return {}
    
    def log_message(self, message):
        """로그 메시지 출력 (daemon 모드에서는 파일로, 일반 모드에서는 콘솔로)"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_msg = f"[{timestamp}] {message}"
        
        if self.daemon_mode:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(log_msg + '\n')
        else:
            print(log_msg)
    
    def write_pid_file(self):
        """PID 파일 생성"""
        try:
            with open(self.pid_file, 'w') as f:
                f.write(str(os.getpid()))
            self.log_message(f"PID 파일 생성: {self.pid_file}")
        except Exception as e:
            self.log_message(f"PID 파일 생성 오류: {e}")
    
    def remove_pid_file(self):
        """PID 파일 삭제"""
        try:
            if os.path.exists(self.pid_file):
                os.remove(self.pid_file)
                self.log_message("PID 파일 삭제 완료")
        except Exception as e:
            self.log_message(f"PID 파일 삭제 오류: {e}")
    
    def signal_handler(self, signum, frame):
        """시그널 핸들러 (중단 신호 처리)"""
        self.log_message(f"시그널 {signum} 수신 - 종료 중...")
        self.running = False
        self.remove_pid_file()
        sys.exit(0)
    
    def daemonize(self):
        """데몬 프로세스로 실행 (크로스 플랫폼)"""
        if self.platform == "Windows":
            # Windows에서는 fork가 없으므로 간단한 백그라운드 실행
            self.log_message("Windows에서 백그라운드 모드로 시작됨")
            self.write_pid_file()
            
            # Windows 시그널 핸들러 등록
            signal.signal(signal.SIGTERM, self.signal_handler)
            signal.signal(signal.SIGINT, self.signal_handler)
            signal.signal(signal.SIGBREAK, self.signal_handler)
        else:
            # Unix 계열 (macOS, Linux) 데몬화
            try:
                # 첫 번째 fork
                pid = os.fork()
                if pid > 0:
                    sys.exit(0)  # 부모 프로세스 종료
            except OSError as e:
                self.log_message(f"첫 번째 fork 실패: {e}")
                sys.exit(1)
            
            # 세션 리더가 되기
            os.setsid()
            
            try:
                # 두 번째 fork
                pid = os.fork()
                if pid > 0:
                    sys.exit(0)  # 부모 프로세스 종료
            except OSError as e:
                self.log_message(f"두 번째 fork 실패: {e}")
                sys.exit(1)
            
            # 작업 디렉토리 변경
            os.chdir('/')
            
            # 파일 권한 마스크 설정
            os.umask(0)
            
            # 표준 입출력 리다이렉션
            sys.stdout.flush()
            sys.stderr.flush()
            
            # PID 파일 생성
            self.write_pid_file()
            
            # 시그널 핸들러 등록
            signal.signal(signal.SIGTERM, self.signal_handler)
            signal.signal(signal.SIGINT, self.signal_handler)
            
            self.log_message("데몬 모드로 시작됨")
    
    def check_and_terminate_existing_process(self):
        """기존에 실행 중인 optimized_automation.py 프로세스가 있는지 확인하고 중단"""
        try:
            current_pid = os.getpid()
            terminated_count = 0
            
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    # 프로세스 정보 가져오기
                    proc_info = proc.info
                    cmdline = proc_info.get('cmdline', [])
                    
                    # 현재 프로세스가 아니고, optimized_automation.py를 실행하는 프로세스인지 확인
                    if (proc_info['pid'] != current_pid and 
                        cmdline and 
                        any(self.script_name in arg for arg in cmdline)):
                        
                        print(f"🔍 기존 프로세스 발견: PID {proc_info['pid']}")
                        print(f"   명령어: {' '.join(cmdline)}")
                        
                        # 프로세스 중단
                        proc.terminate()
                        terminated_count += 1
                        
                        # 프로세스가 완전히 종료될 때까지 대기
                        try:
                            proc.wait(timeout=5)
                            print(f"✅ 프로세스 {proc_info['pid']} 중단 완료")
                        except psutil.TimeoutExpired:
                            # 강제 종료
                            proc.kill()
                            print(f"⚠️  프로세스 {proc_info['pid']} 강제 종료")
                            
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    # 프로세스가 이미 종료되었거나 접근 권한이 없는 경우
                    continue
            
            if terminated_count > 0:
                print(f"🛑 총 {terminated_count}개의 기존 프로세스를 중단했습니다.")
                time.sleep(2)  # 프로세스 종료 대기
            else:
                print("✅ 실행 중인 기존 프로세스가 없습니다. 작업을 시작합니다. 채팅창을 클릭해서 채팅창에 커서를 두세요")
                
            return True
            
        except Exception as e:
            print(f"❌ 기존 프로세스 확인 중 오류: {e}")
            return False
        
    def send_command_to_cursor(self, command):
        """크로스 플랫폼 방식으로 Cursor IDE 채팅창에 AI 명령 전송"""
        try:
            if self.platform == "Windows":
                return self._send_command_windows(command)
            elif self.platform == "Darwin":  # macOS
                return self._send_command_macos(command)
            elif self.platform == "Linux":
                return self._send_command_linux(command)
            else:
                self.log_message(f"지원하지 않는 플랫폼: {self.platform}")
                return False
                
        except Exception as e:
            self.log_message(f"명령 전송 중 오류: {e}")
            return False
    
    def _send_command_windows(self, command):
        """Windows용 Cursor IDE 명령 전송"""
        try:
            # Cursor 창 찾기
            cursor_windows = gw.getWindowsWithTitle('Cursor')
            if not cursor_windows:
                # 다른 가능한 창 제목들 시도
                possible_titles = ['Cursor', 'cursor', 'Cursor.exe']
                for title in possible_titles:
                    cursor_windows = gw.getWindowsWithTitle(title)
                    if cursor_windows:
                        break
            
            if not cursor_windows:
                self.log_message("❌ Cursor 창을 찾을 수 없습니다.")
                return False
            
            # 첫 번째 Cursor 창 활성화
            cursor_window = cursor_windows[0]
            cursor_window.activate()
            time.sleep(self.delays['activation'])
            
            # 채팅창 열기 (Ctrl+L)
            pyautogui.hotkey('ctrl', 'l')
            time.sleep(1.5)
            pyautogui.hotkey('ctrl', 'l')
            time.sleep(self.delays['keystroke'])
            
            # 채팅창 영역 클릭 (일반적인 위치)
            window_center = cursor_window.center
            chat_x = window_center.x
            chat_y = window_center.y + 100  # 창 중앙에서 아래쪽
            pyautogui.click(chat_x, chat_y)
            time.sleep(0.3)
            
            # 명령어 입력
            pyautogui.write(command)
            time.sleep(self.delays['enter'])
            
            # 엔터 두 번
            pyautogui.press('enter')
            time.sleep(self.delays['enter'])
            pyautogui.press('enter')
            time.sleep(self.delays['final'])
            
            self.log_message(f"AI 명령 전송 (Windows): {command}")
            return True
            
        except Exception as e:
            self.log_message(f"Windows 명령 전송 중 오류: {e}")
            return False
    
    def _send_command_macos(self, command):
        """macOS용 Cursor IDE 명령 전송 (AppleScript)"""
        try:
            applescript = f'''
            tell application "Cursor"
                activate
                delay {self.delays['activation']}
            end tell
            
            tell application "System Events"
                tell process "Cursor"
                    -- Cursor가 완전히 활성화될 때까지 대기
                    delay 2.0
                    
                    -- 채팅창이 보이도록 보장 (Cmd+L 두 번으로 확실히 열기)
                    key code 37 using command down
                    delay 1.5
                    key code 37 using command down
                    delay {self.delays['keystroke']}
                    
                    -- 채팅창 텍스트 필드 찾기 및 클릭
                    try
                        set chatField to first text field of first window whose description contains "chat" or description contains "message" or description contains "input" or description contains "Ask"
                        click chatField
                        delay 0.3
                    on error
                        -- 대안: 채팅창 영역 클릭 (일반적인 위치)
                        click at {{500, 600}}
                        delay 0.3
                    end try
                    
                    -- 명령어 입력
                    keystroke "{command}"
                    delay {self.delays['enter']}
                    
                    -- 엔터 두 번
                    key code 36
                    delay {self.delays['enter']}
                    key code 36
                    delay {self.delays['final']}
                end tell
            end tell
            '''
            
            # AppleScript 실행
            subprocess.run(['osascript', '-e', applescript], check=True)
            
            self.log_message(f"AI 명령 전송 (macOS): {command}")
            return True
            
        except Exception as e:
            self.log_message(f"macOS 명령 전송 중 오류: {e}")
            return False
    
    def _send_command_linux(self, command):
        """Linux용 Cursor IDE 명령 전송"""
        try:
            # Linux에서는 xdotool이나 pyautogui 사용
            if 'pyautogui' in globals():
                # pyautogui 사용
                # Cursor 창 활성화 (간단한 방법)
                pyautogui.hotkey('alt', 'tab')  # 창 전환
                time.sleep(self.delays['activation'])
                
                # 채팅창 열기 (Ctrl+L)
                pyautogui.hotkey('ctrl', 'l')
                time.sleep(1.5)
                pyautogui.hotkey('ctrl', 'l')
                time.sleep(self.delays['keystroke'])
                
                # 채팅창 영역 클릭
                pyautogui.click(500, 600)
                time.sleep(0.3)
                
                # 명령어 입력
                pyautogui.write(command)
                time.sleep(self.delays['enter'])
                
                # 엔터 두 번
                pyautogui.press('enter')
                time.sleep(self.delays['enter'])
                pyautogui.press('enter')
                time.sleep(self.delays['final'])
                
                self.log_message(f"AI 명령 전송 (Linux): {command}")
                return True
            else:
                # xdotool 사용 (설치 필요)
                subprocess.run(['xdotool', 'search', '--name', 'Cursor', 'windowactivate'], check=True)
                time.sleep(self.delays['activation'])
                
                subprocess.run(['xdotool', 'key', 'ctrl+l'], check=True)
                time.sleep(1.5)
                subprocess.run(['xdotool', 'key', 'ctrl+l'], check=True)
                time.sleep(self.delays['keystroke'])
                
                subprocess.run(['xdotool', 'mousemove', '500', '600'], check=True)
                subprocess.run(['xdotool', 'click', '1'], check=True)
                time.sleep(0.3)
                
                subprocess.run(['xdotool', 'type', command], check=True)
                time.sleep(self.delays['enter'])
                
                subprocess.run(['xdotool', 'key', 'Return'], check=True)
                time.sleep(self.delays['enter'])
                subprocess.run(['xdotool', 'key', 'Return'], check=True)
                time.sleep(self.delays['final'])
                
                self.log_message(f"AI 명령 전송 (Linux): {command}")
                return True
                
        except Exception as e:
            self.log_message(f"Linux 명령 전송 중 오류: {e}")
            return False
    
    def run_automation(self):
        """자동화 실행"""
        self.log_message("=== 최적화된 Cursor IDE AI 자동화 시작 ===")
        self.log_message(f"총 명령 개수: {self.total_commands}개")
        self.log_message(f"채팅창 포커스: {'활성화' if self.chat_focus_enabled else '비활성화'}")
        if self.chat_focus_enabled:
            self.log_message(f"채팅창 클릭 좌표: {self.chat_click_coordinates}")
            self.log_message(f"대체 단축키: {self.fallback_shortcut}")
        self.log_message("=" * 50)
        
        # 각 명령별 정보 출력
        for i, cmd in enumerate(self.commands):
            self.log_message(f"명령 {i+1}: {cmd['command']} (간격: {cmd['interval']}초, 횟수: {cmd['max_count']}회)")
        self.log_message("=" * 50)
        
        # 기존 프로세스 확인 및 중단
        self.log_message("🔍 기존 프로세스 확인 중...")
        self.check_and_terminate_existing_process()
        
        # Cursor IDE 활성화 안내
        self.log_message("⚠️  주의사항:")
        self.log_message("1. Cursor IDE를 열고 채팅창이 보이는 상태로 두세요")
        self.log_message("2. 채팅창을 클릭하여 커서를 두세요")
        self.log_message("3. 3초 후 자동화가 시작됩니다...")
        self.log_message("4. 자동화 중에는 Cursor IDE 창을 건드리지 마세요")
        if not self.daemon_mode:
            self.log_message("5. 중단하려면 Ctrl+C를 누르세요")
        
        time.sleep(3)
        
        # 최초 한번만 채팅창 활성화
        self.log_message("🔧 최초 채팅창 활성화 중...")
        try:
            if self.platform == "Windows":
                # Windows용 초기 활성화
                cursor_windows = gw.getWindowsWithTitle('Cursor')
                if cursor_windows:
                    cursor_window = cursor_windows[0]
                    cursor_window.activate()
                    time.sleep(2.0)
                    pyautogui.hotkey('ctrl', 'l')
                    time.sleep(1.0)
                    self.log_message("✅ 최초 채팅창 활성화 완료 (Windows)")
                else:
                    self.log_message("⚠️  Cursor 창을 찾을 수 없습니다.")
            elif self.platform == "Darwin":  # macOS
                initial_activation_script = '''
                tell application "Cursor"
                    activate
                    delay 1.0
                end tell
                
                tell application "System Events"
                    tell process "Cursor"
                        delay 2.0
                        key code 37 using command down
                        delay 1.0
                    end tell
                end tell
                '''
                subprocess.run(['osascript', '-e', initial_activation_script], check=True)
                self.log_message("✅ 최초 채팅창 활성화 완료 (macOS)")
            elif self.platform == "Linux":
                if 'pyautogui' in globals():
                    pyautogui.hotkey('alt', 'tab')
                    time.sleep(2.0)
                    pyautogui.hotkey('ctrl', 'l')
                    time.sleep(1.0)
                    self.log_message("✅ 최초 채팅창 활성화 완료 (Linux)")
                else:
                    subprocess.run(['xdotool', 'search', '--name', 'Cursor', 'windowactivate'], check=True)
                    time.sleep(2.0)
                    subprocess.run(['xdotool', 'key', 'ctrl+l'], check=True)
                    time.sleep(1.0)
                    self.log_message("✅ 최초 채팅창 활성화 완료 (Linux)")
        except Exception as e:
            self.log_message(f"⚠️  최초 채팅창 활성화 실패: {e}")
        
        # 모든 명령을 순차적으로 실행
        for command_index, command_config in enumerate(self.commands):
            if not self.running:
                break
                
            self.current_command_index = command_index
            self.current_command = command_config
            self.interval = command_config.get('interval', 10)
            self.max_count = command_config.get('max_count', 10)
            self.command = command_config.get('command', '@2.test.md')
            self.count = 0  # 각 명령마다 카운터 리셋
            
            self.log_message(f"🚀 명령 {command_index + 1}/{self.total_commands} 시작: {self.command}")
            self.log_message(f"   간격: {self.interval}초, 최대 횟수: {self.max_count}회")
            
            # 현재 명령 실행
            while self.count < self.max_count and self.running:
                try:
                    self.count += 1
                    
                    # 명령 전송
                    success = self.send_command_to_cursor(self.command)
                    if success:
                        self.log_message(f"✅ 명령 {command_index + 1} - {self.count}번째 전송 성공")
                    else:
                        self.log_message(f"❌ 명령 {command_index + 1} - {self.count}번째 전송 실패")
                    
                    # 최대 실행 횟수 도달 시 다음 명령으로
                    if self.count >= self.max_count:
                        self.log_message(f"🎉 명령 {command_index + 1} 완료! 총 {self.count}회 실행됨")
                        break
                    
                    # 다음 반복까지 대기 (첫 번째 실행 후부터 interval 적용)
                    self.log_message(f"다음 실행까지 {self.interval}초 대기...")
                    time.sleep(self.interval)
                    
                except KeyboardInterrupt:
                    self.log_message("⏹️  사용자에 의해 중단됨")
                    self.running = False
                    break
                except Exception as e:
                    self.log_message(f"오류 발생: {e}")
                    time.sleep(5)  # 오류 시 5초 대기 후 재시도
            
            # 명령 간 대기 (마지막 명령이 아닌 경우)
            if command_index < self.total_commands - 1 and self.running:
                self.log_message(f"⏳ 다음 명령까지 3초 대기...")
                time.sleep(3)
        
        if self.running:
            self.log_message("🎉 모든 명령 실행 완료!")
        
        # 정리 작업
        self.remove_pid_file()

def main():
    """메인 함수"""
    parser = argparse.ArgumentParser(description='Cursor IDE AI 자동화 도구')
    parser.add_argument('-d', '--daemon', action='store_true', 
                       help='백그라운드 데몬 모드로 실행')
    parser.add_argument('--stop', action='store_true', 
                       help='실행 중인 자동화 프로세스 중단')
    parser.add_argument('--status', action='store_true', 
                       help='실행 상태 확인')
    
    args = parser.parse_args()
    
    if args.stop:
        stop_automation()
        return
    
    if args.status:
        check_status()
        return
    
    if args.daemon:
        print("백그라운드 데몬 모드로 시작합니다...")
        automation = OptimizedCursorAutomation(daemon_mode=True)
        automation.daemonize()
    else:
        automation = OptimizedCursorAutomation(daemon_mode=False)
        print("최적화된 Cursor IDE AI 자동화 도구")
        print(f"총 {automation.total_commands}개의 명령을 순차적으로 실행합니다.")
        for i, cmd in enumerate(automation.commands):
            print(f"명령 {i+1}: {cmd['command']} (간격: {cmd['interval']}초, 횟수: {cmd['max_count']}회)")
        print()
    
    automation.run_automation()

def stop_automation():
    """실행 중인 자동화 프로세스 중단"""
    pid_file = "/tmp/optimized_automation.pid"
    
    if not os.path.exists(pid_file):
        print("❌ 실행 중인 자동화 프로세스가 없습니다.")
        return
    
    try:
        with open(pid_file, 'r') as f:
            pid = int(f.read().strip())
        
        # 프로세스 존재 확인
        if psutil.pid_exists(pid):
            process = psutil.Process(pid)
            if "optimized_automation.py" in ' '.join(process.cmdline()):
                process.terminate()
                print(f"✅ 프로세스 {pid} 중단 요청됨")
                
                # 프로세스 종료 대기
                try:
                    process.wait(timeout=5)
                    print("✅ 프로세스가 정상적으로 종료되었습니다.")
                except psutil.TimeoutExpired:
                    process.kill()
                    print("⚠️  프로세스를 강제 종료했습니다.")
            else:
                print("❌ 해당 PID는 자동화 프로세스가 아닙니다.")
        else:
            print("❌ 프로세스가 이미 종료되었습니다.")
            os.remove(pid_file)
            
    except Exception as e:
        print(f"❌ 중단 중 오류 발생: {e}")

def check_status():
    """실행 상태 확인"""
    pid_file = "/tmp/optimized_automation.pid"
    log_file = "/tmp/optimized_automation.log"
    
    if not os.path.exists(pid_file):
        print("❌ 자동화 프로세스가 실행 중이지 않습니다.")
        return
    
    try:
        with open(pid_file, 'r') as f:
            pid = int(f.read().strip())
        
        if psutil.pid_exists(pid):
            process = psutil.Process(pid)
            if "optimized_automation.py" in ' '.join(process.cmdline()):
                print(f"✅ 자동화 프로세스가 실행 중입니다. (PID: {pid})")
                print(f"   시작 시간: {datetime.fromtimestamp(process.create_time()).strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"   CPU 사용률: {process.cpu_percent()}%")
                print(f"   메모리 사용량: {process.memory_info().rss / 1024 / 1024:.1f} MB")
                
                if os.path.exists(log_file):
                    print(f"\n📋 최근 로그 (마지막 5줄):")
                    with open(log_file, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                        for line in lines[-5:]:
                            print(f"   {line.strip()}")
            else:
                print("❌ 해당 PID는 자동화 프로세스가 아닙니다.")
        else:
            print("❌ 프로세스가 종료되었습니다. PID 파일을 정리합니다.")
            os.remove(pid_file)
            
    except Exception as e:
        print(f"❌ 상태 확인 중 오류 발생: {e}")

if __name__ == "__main__":
    main()
