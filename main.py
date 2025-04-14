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
from tray_manager import TrayManager

# Windows 작업표시줄 아이콘 설정 (프로그램 시작 전에 수행)
if sys.platform == 'win32':
    try:
        myappid = "GestureMacro.App.1.0"  # 고유 애플리케이션 ID
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    except Exception as e:
        print("작업표시줄 아이콘 ID 설정 실패:", e)

# 전역 변수 선언 (트레이 관련 변수 제거, tray_manager 객체 추가)
root_window = None
gui = None
recorder = None
player = None
editor = None
storage = None
gesture_manager = None
tray_manager = None # TrayManager 인스턴스
icon_path_global = None

def set_taskbar_icon(root, icon_path):
    """작업표시줄 아이콘을 설정하는 함수"""
    if sys.platform == 'win32' and os.path.exists(icon_path):
        try:
            hwnd = ctypes.windll.user32.GetParent(root.winfo_id())
            h_icon_small = ctypes.windll.shell32.ExtractIconW(0, icon_path, 1)
            h_icon_big = ctypes.windll.shell32.ExtractIconW(0, icon_path, 0)
            if h_icon_small:
                ctypes.windll.user32.SendMessageW(hwnd, 0x0080, 0, h_icon_small)
            if h_icon_big:
                ctypes.windll.user32.SendMessageW(hwnd, 0x0080, 1, h_icon_big)
        except Exception as e:
            print(f"작업표시줄 아이콘 설정 실패: {e}")

def auto_enable_gesture():
    """자동으로 제스처 인식 활성화"""
    print("제스처 인식 자동 활성화")
    if gui:
        gui.start_gesture_recognition()

def graceful_exit():
    """애플리케이션 종료 로직 (TrayManager 콜백)"""
    global root_window, tray_manager, gesture_manager, recorder
    print("Starting graceful exit sequence...")
    
    # 1. 트레이 아이콘 중지 요청 (TrayManager가 담당)
    if tray_manager:
        tray_manager.stop() # 스레드 종료 대기 포함
            
    # 2. 매크로 녹화 중지
    if recorder and recorder.recording:
        print("Stopping macro recorder...")
        recorder.stop_recording()
        time.sleep(0.1)

    # 3. 제스처 리스너 중지
    if gesture_manager:
        print("Stopping gesture listener...")
        gesture_manager.stop() # join 포함

    # 4. Tkinter 메인 루프 종료 및 윈도우 파괴
    if root_window:
        print("Quitting Tkinter main loop and destroying window...")
        try:
            root_window.quit()
            root_window.destroy()
        except tk.TclError as e:
            print(f"Error during Tkinter quit/destroy: {e}")
        time.sleep(0.2)

    print("Graceful exit sequence complete.")
    # sys.exit(0) # 필요한 경우 명시적 종료

# --- 메인 함수 수정 ---
def main():
    # 전역 변수 사용 선언
    global root_window, gui, recorder, player, editor, storage, gesture_manager, tray_manager, icon_path_global

    # 루트 윈도우 생성
    root_window = tk.Tk()
    root_window.withdraw()  # 시작 시 숨김

    # 아이콘 경로 설정
    icon_path_global = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets', 'icon.ico')
    app_name = "Gesture Macro"

    # 제목 표시줄 아이콘 설정
    if os.path.exists(icon_path_global):
        try:
            root_window.iconbitmap(default=icon_path_global)
        except Exception as e:
             print(f"제목표시줄 아이콘 설정 오류: {e}")

    # 애플리케이션 이름 설정
    root_window.title(app_name)

    # 작업표시줄 아이콘 설정 (윈도우 표시 후)
    if os.path.exists(icon_path_global):
        root_window.after(100, lambda: set_taskbar_icon(root_window, icon_path_global))

    # --- TrayManager 초기화 및 시작 --- (기존 트레이 코드 대체)
    tray_manager = TrayManager(root_window, icon_path_global, app_name, graceful_exit)
    if not tray_manager.start(): # 트레이 아이콘 시작 시도
        print("시스템 트레이 아이콘을 시작할 수 없습니다.")
        # 트레이 아이콘 없이 계속 진행하거나, 여기서 종료 처리 가능

    # 디버깅 정보 출력
    print("System:", sys.platform)
    print("Current Directory:", os.getcwd())

    # 인스턴스 생성
    storage = MacroStorage()
    recorder = MacroRecorder()
    player = MacroPlayer()
    editor = MacroEditor(storage)
    gesture_manager = GestureManager(player, storage, recorder)

    # GUI 초기화
    gui = SimpleGUI(root_window, recorder, player, editor, storage, gesture_manager)
    gui.setup_ui()

    # 윈도우 표시
    root_window.deiconify()

    # 닫기(X) 버튼 클릭 시 동작을 TrayManager의 hide_window로 변경
    if tray_manager:
        root_window.protocol("WM_DELETE_WINDOW", tray_manager.hide_window)
    else:
        # 트레이 매니저가 없으면 그냥 종료하도록 설정 (선택 사항)
        root_window.protocol("WM_DELETE_WINDOW", graceful_exit)

    # 최소화 버튼 클릭 시 트레이 이동 로직 (선택 사항)
    # if tray_manager:
    #     root_window.bind("<Unmap>", lambda event: tray_manager.hide_window() if root_window.state() == 'iconic' else None)

    # 자동으로 제스처 인식 활성화
    root_window.after(500, auto_enable_gesture)

    # 메인 루프 시작
    try:
        root_window.mainloop()
    except KeyboardInterrupt:
        print("KeyboardInterrupt received. Exiting gracefully...")
        graceful_exit() # Ctrl+C 종료 시에도 정리 수행
    finally:
        # 메인 루프가 정상/비정상 종료된 후 최종 정리
        # (graceful_exit에서 이미 처리하지만, 만약을 대비)
        if tray_manager:
             tray_manager.stop() # 혹시 모를 트레이 아이콘 정리
        print("Application main loop ended.")

if __name__ == "__main__":
    main()