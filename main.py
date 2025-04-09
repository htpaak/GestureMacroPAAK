import tkinter as tk
import os
import sys
import time
import ctypes
from recorder import MacroRecorder
from player import MacroPlayer
from editor import MacroEditor
from storage import MacroStorage
from simple_gui import SimpleGUI
from gesture_manager import GestureManager

# Windows 작업표시줄 아이콘 설정 (프로그램 시작 전에 수행)
if sys.platform == 'win32':
    try:
        myappid = "GestureMacro.App.1.0"  # 고유 애플리케이션 ID
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    except Exception as e:
        print("작업표시줄 아이콘 ID 설정 실패:", e)

def set_taskbar_icon(root, icon_path):
    """작업표시줄 아이콘을 설정하는 함수"""
    if sys.platform == 'win32' and os.path.exists(icon_path):
        try:
            # 윈도우 핸들 가져오기
            hwnd = ctypes.windll.user32.GetParent(root.winfo_id())
            # 큰 아이콘(ICON_BIG)과 작은 아이콘(ICON_SMALL) 모두 설정
            app_icon = ctypes.windll.shell32.ExtractIconW(0, icon_path, 0)
            if app_icon:
                ctypes.windll.user32.SendMessageW(hwnd, 0x0080, 0, app_icon)  # WM_SETICON, ICON_SMALL
                ctypes.windll.user32.SendMessageW(hwnd, 0x0080, 1, app_icon)  # WM_SETICON, ICON_BIG
        except Exception as e:
            print("작업표시줄 아이콘 설정 실패:", e)

def auto_enable_gesture():
    """자동으로 제스처 인식 활성화"""
    print("제스처 인식 자동 활성화")
    # 체크박스 대신 시작 버튼 기능 사용
    gui.start_gesture_recognition()

def delayed_icon_setup(root, icon_path):
    """일정 시간 후 아이콘 설정을 다시 시도"""
    set_taskbar_icon(root, icon_path)

def main():
    # 루트 윈도우 생성 - 처음에는 숨김 상태로 생성
    root = tk.Tk()
    root.withdraw()  # 윈도우 숨기기
    
    # 아이콘 설정
    icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets', 'icon.ico')
    if os.path.exists(icon_path):
        # 제목표시줄 아이콘 설정
        root.iconbitmap(icon_path)
        root.wm_iconbitmap(icon_path)
        
        # 애플리케이션 이름 설정
        root.title("제스처 매크로")
        
        # 작업표시줄 아이콘 설정
        set_taskbar_icon(root, icon_path)
    
    # 전역 변수 설정
    global gui, recorder, player, editor, storage, gesture_manager
    
    # 디버깅 정보 출력
    print("시스템 정보:", sys.platform)
    print("현재 디렉토리:", os.getcwd())
    
    # 인스턴스 생성
    storage = MacroStorage()
    recorder = MacroRecorder()
    player = MacroPlayer()
    editor = MacroEditor(storage)
    
    # 제스처 매니저 초기화
    gesture_manager = GestureManager(player, storage, recorder)
    
    # GUI 초기화
    gui = SimpleGUI(root, recorder, player, editor, storage, gesture_manager)
    gui.setup_ui()
    
    # 윈도우 표시 (GUI 설정이 완료된 후)
    root.deiconify()  # 윈도우 표시
    
    # 아이콘 다시 설정 (윈도우가 표시된 후)
    if os.path.exists(icon_path):
        root.after(10, lambda: set_taskbar_icon(root, icon_path))
        root.after(100, lambda: set_taskbar_icon(root, icon_path))
    
    # 자동으로 제스처 인식 활성화 (0.5초 후)
    root.after(500, auto_enable_gesture)
    
    # 메인 루프 시작
    root.mainloop()

if __name__ == "__main__":
    main()