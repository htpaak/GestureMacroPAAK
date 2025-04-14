import tkinter as tk
import os
import sys
import time
import ctypes
import threading
from PIL import Image
import pystray
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

# 전역 변수 선언
tray_icon = None
root_window = None # root -> root_window 이름 변경 및 전역 선언
icon_path_global = None # 아이콘 경로 전역 변수 추가
is_window_hidden = False # 창 숨김 상태 추적 변수 추가

def set_taskbar_icon(root, icon_path):
    """작업표시줄 아이콘을 설정하는 함수"""
    if sys.platform == 'win32' and os.path.exists(icon_path):
        try:
            hwnd = ctypes.windll.user32.GetParent(root.winfo_id())
            h_icon_small = ctypes.windll.shell32.ExtractIconW(0, icon_path, 1) # 작은 아이콘 인덱스 1
            h_icon_big = ctypes.windll.shell32.ExtractIconW(0, icon_path, 0) # 큰 아이콘 인덱스 0
            if h_icon_small:
                ctypes.windll.user32.SendMessageW(hwnd, 0x0080, 0, h_icon_small) # WM_SETICON, ICON_SMALL=0
            if h_icon_big:
                ctypes.windll.user32.SendMessageW(hwnd, 0x0080, 1, h_icon_big) # WM_SETICON, ICON_BIG=1
        except Exception as e:
            print(f"작업표시줄 아이콘 설정 실패: {e}")

def auto_enable_gesture():
    """자동으로 제스처 인식 활성화"""
    print("제스처 인식 자동 활성화")
    gui.start_gesture_recognition()

def hide_window():
    """창을 숨김 상태로 전환"""
    global root_window, is_window_hidden
    if root_window:
        root_window.withdraw()
        is_window_hidden = True # 창 숨김 상태 업데이트
        print("Window hidden, tray icon should be visible.")

def show_window(icon=None, item=None):
    """창을 표시 상태로 전환"""
    global root_window, is_window_hidden
    # if tray_icon: # 트레이 아이콘 중지 로직 제거
    #     tray_icon.stop()
    if root_window:
        # Tkinter의 메인 스레드에서 실행되도록 예약
        root_window.after(0, root_window.deiconify)
        is_window_hidden = False # 창 표시 상태 업데이트
        print("Window shown.")
        # 트레이 아이콘 자체는 계속 실행 중이므로 여기서 stop()을 호출하지 않음


def on_exit(icon, item):
    """애플리케이션 종료"""
    global root_window, tray_icon, gesture_manager, recorder # recorder 전역 변수 추가
    print("Exiting application...")
    
    # 1. 트레이 아이콘 중지 (에러 발생 방지)
    if tray_icon:
        try:
            tray_icon.stop()
        except Exception as e:
            print(f"Error stopping tray icon: {e}")
            
    # 2. 매크로 녹화 중지 (recorder 스레드 종료)
    if recorder and recorder.recording: # is_recording -> recording 으로 수정
        print("Stopping macro recorder...")
        recorder.stop_recording() # unhook 호출
        # recorder의 스레드가 데몬이 아닐 수 있으므로 약간의 시간 부여
        time.sleep(0.1) 

    # 3. 제스처 리스너 중지 (pynput 리스너 스레드 종료)
    if gesture_manager:
        print("Stopping gesture listener...")
        gesture_manager.stop() # 내부적으로 join() 호출됨
        # gesture_manager.stop()에서 join 대기 시간이 길어질 수 있으므로 추가 sleep은 불필요

    # 4. Tkinter 메인 루프 종료 및 윈도우 파괴
    if root_window:
        print("Quitting Tkinter main loop and destroying window...")
        try:
            root_window.quit() # Tkinter 메인 루프 종료 요청
            # quit() 호출 후 destroy()를 호출하여 윈도우 리소스 정리
            root_window.destroy()
        except tk.TclError as e:
            # 이미 윈도우가 파괴된 경우 등 예외 처리
            print(f"Error during Tkinter quit/destroy: {e}")
        # 메인 루프 종료 후 실제로 프로세스가 정리될 때까지 약간의 시간 추가
        time.sleep(0.2) 

    print("Exit sequence complete.") # 모든 종료 단계 완료 로그

def run_tray_icon(icon):
    """트레이 아이콘을 별도 스레드에서 실행"""
    icon.run()

def setup_tray_icon(icon_path):
    """시스템 트레이 아이콘 설정 및 실행 준비"""
    # global tray_icon 제거 (함수 내에서 지역 변수로 사용)
    try:
        image = Image.open(icon_path)
        # 메뉴 설정: 'Show' (기본 동작, 더블 클릭 시 실행), 'Exit'
        menu = (pystray.MenuItem('Show', show_window, default=True), # 더블클릭 시 show_window 실행
                pystray.MenuItem('Exit', on_exit))
        # 아이콘 생성
        icon = pystray.Icon("GestureMacro", image, "Gesture Macro", menu)
        return icon # 생성된 아이콘 객체 반환
    except FileNotFoundError:
        print(f"아이콘 파일을 찾을 수 없습니다: {icon_path}")
        return None
    except Exception as e:
        print(f"트레이 아이콘 설정 중 오류 발생: {e}")
        return None

# --- 메인 함수 수정 ---
def main():
    # 전역 변수 사용 선언
    global root_window, gui, recorder, player, editor, storage, gesture_manager, tray_icon, icon_path_global

    # 루트 윈도우 생성 (이름 변경: root -> root_window)
    root_window = tk.Tk()
    root_window.withdraw()  # 시작 시 숨김

    # 아이콘 경로 설정 (전역 변수 사용)
    icon_path_global = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets', 'icon.ico')

    # 아이콘 설정
    if os.path.exists(icon_path_global):
        try:
            # 제목 표시줄 아이콘 (Tkinter 기본 방식)
            root_window.iconbitmap(default=icon_path_global)
        # except tk.TclError as e: # 좀 더 상세한 예외 처리
        #      print(f"제목표시줄 아이콘 설정 오류 (TclError): {e}. 파일 경로 확인: {icon_path_global}")
        except Exception as e: # 포괄적인 예외 처리
             print(f"제목표시줄 아이콘 설정 오류: {e}")

        # 애플리케이션 이름 설정
        root_window.title("Gesture Macro")

        # 작업표시줄 아이콘 (ctypes 사용, 윈도우 표시 후 약간의 딜레이 권장)
        root_window.after(100, lambda: set_taskbar_icon(root_window, icon_path_global))

        # 시스템 트레이 아이콘 설정
        tray_icon = setup_tray_icon(icon_path_global)
        if tray_icon:
             # 트레이 아이콘을 별도 스레드에서 시작
             tray_thread = threading.Thread(target=run_tray_icon, args=(tray_icon,), daemon=True)
             tray_thread.start()
             print("Tray icon thread started.")
    else:
        print(f"아이콘 파일({icon_path_global})을 찾을 수 없어 아이콘 관련 기능을 설정할 수 없습니다.") # 오류 메시지 명확화
        root_window.title("Gesture Macro (No Icon)") # 아이콘 없을 때 대체 타이틀


    # 전역 변수 설정은 위에서 이미 선언됨
    # global gui, recorder, player, editor, storage, gesture_manager

    # 디버깅 정보 출력
    print("System:", sys.platform)
    print("Current Directory:", os.getcwd())

    # 인스턴스 생성
    storage = MacroStorage()
    recorder = MacroRecorder()
    player = MacroPlayer()
    editor = MacroEditor(storage)

    # 제스처 매니저 초기화
    gesture_manager = GestureManager(player, storage, recorder)

    # GUI 초기화 (root_window 전달)
    gui = SimpleGUI(root_window, recorder, player, editor, storage, gesture_manager)
    gui.setup_ui()

    # 윈도우 표시
    root_window.deiconify()

    # 닫기(X) 버튼 클릭 시 동작을 hide_window 함수로 변경
    root_window.protocol("WM_DELETE_WINDOW", hide_window)

    # 최소화 버튼 클릭 시 트레이로 이동 주석 제거 및 적용
    # root_window.bind("<Unmap>", lambda event: hide_window() if root_window.state() == 'iconic' else None)


    # 자동으로 제스처 인식 활성화 (0.5초 후)
    root_window.after(500, auto_enable_gesture)

    # 메인 루프 시작 (root_window 사용)
    root_window.mainloop()

    # 메인 루프 종료 후 트레이 아이콘 스레드가 남아있을 수 있으므로 확실히 종료
    if tray_icon and tray_icon.visible: # tray_icon 객체가 존재하고 visible 상태일 때만 stop 호출
        print("Stopping tray icon...")
        tray_icon.stop()
    print("Application finished.") # 종료 메시지 추가


if __name__ == "__main__":
    main()