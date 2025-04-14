import tkinter as tk
import os
import sys
import time
import ctypes
import logging # 로깅 모듈 추가
from recorder import MacroRecorder
from player import MacroPlayer
from editor import MacroEditor
from storage import MacroStorage
# from simple_gui import SimpleGUI  # 주석 처리 또는 삭제
from gui_base import GuiBase      # GuiBase 임포트
from gesture_manager import GestureManager
from tray_manager import TrayManager

# 로깅 설정
log_format = '%(asctime)s - PID:%(process)d - %(levelname)s - %(message)s'
logging.basicConfig(level=logging.INFO, format=log_format)

# Windows 작업표시줄 아이콘 설정 (프로그램 시작 전에 수행)
if sys.platform == 'win32':
    try:
        myappid = "GestureMacro.App.1.0"  # 고유 애플리케이션 ID
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        logging.info(f"AppUserModelID set to: {myappid}")
    except Exception as e:
        logging.error("작업표시줄 아이콘 ID 설정 실패:", exc_info=True)

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
    global root_window, tray_manager, gesture_manager, recorder, gui
    logging.info("Starting graceful exit sequence...")
    
    # 1. 매크로 녹화 중지
    if recorder and recorder.recording:
        logging.info("Stopping macro recorder...")
        try:
            recorder.stop_recording()
            time.sleep(0.1) # 짧은 대기
            logging.info("Macro recorder stopped.")
        except Exception as e:
            logging.error("Error stopping macro recorder:", exc_info=True)
        finally:
             recorder = None # 참조 제거

    # 2. 제스처 리스너 중지
    if gesture_manager:
        logging.info("Stopping gesture listener...")
        try:
            gesture_manager.stop() # join 포함
            logging.info("Gesture listener stopped.")
        except Exception as e:
            logging.error("Error stopping gesture listener:", exc_info=True)
        finally:
            gesture_manager = None # 참조 제거

    # 3. 트레이 아이콘 중지 요청 (Tkinter 종료 전에 실행)
    if tray_manager:
        logging.info("Stopping tray icon...")
        try:
            tray_manager.stop() # 스레드 종료 대기 포함
            logging.info("Tray manager stopped.")
        except Exception as e:
            logging.error("Error stopping tray manager:", exc_info=True)
        finally:
             tray_manager = None # 참조 제거

    # 4. GUI 정리 (quit 전에)
    if gui:
        logging.info("Cleaning up GUI...")
        try:
            # GUI 객체에 정리 메서드가 있다면 호출 (예: gui.cleanup())
            # 현재 SimpleGUI에는 없으므로 참조만 제거
            pass
        except Exception as e:
            logging.error("Error cleaning up GUI:", exc_info=True)
        finally:
            gui = None

    # 5. Tkinter 메인 루프 종료 요청
    if root_window:
        logging.info("Requesting Tkinter main loop quit...")
        try:
            # quit()만 호출하여 mainloop가 종료되도록 함
            root_window.quit()
            # destroy()는 여기서 호출하지 않음
        except Exception as e:
             logging.error("Error requesting Tkinter quit:", exc_info=True)
        # root_window = None # 참조 제거는 finally 블록에서 할 수 있음

    logging.info("Graceful exit sequence complete. Main loop should terminate shortly.")

# --- 메인 함수 수정 ---
def main():
    logging.info("Application starting...")
    # 전역 변수 사용 선언
    global root_window, gui, recorder, player, editor, storage, gesture_manager, tray_manager, icon_path_global

    # 루트 윈도우 생성
    try:
        root_window = tk.Tk()
        root_window.withdraw()  # 시작 시 숨김
        logging.info("Root window created and hidden.")

        # --- 화면 해상도 기반 창 크기 및 위치 설정 --- 
        screen_width = root_window.winfo_screenwidth()
        screen_height = root_window.winfo_screenheight()
        logging.info(f"Screen resolution: {screen_width}x{screen_height}")

        # 창 크기를 화면의 가로 35%, 세로 50%로 설정
        window_width = int(screen_width * 0.33) # 55% -> 35%    
        window_height = int(screen_height * 0.6)
        logging.info(f"Initial window size set to 33% width, 60% height of screen: {window_width}x{window_height}")

        # 창을 화면 중앙에 배치하기 위한 x, y 좌표 계산
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        logging.info(f"Window centered at: x={x}, y={y}")

        # 창 크기와 위치 설정
        root_window.geometry(f"{window_width}x{window_height}+{x}+{y}")

        # 최소 창 크기 설정 (기존 로직 유지)
        min_width = 800 # 예시: 최소 너비
        min_height = 600 # 예시: 최소 높이
        root_window.minsize(min_width, min_height)
        logging.info(f"Minimum window size set to: {min_width}x{min_height}")
        # --- 설정 끝 --- 

    except Exception as e:
        logging.error("Failed to create root window or set geometry:", exc_info=True)
        return # 루트 윈도우 생성/설정 실패 시 종료

    # 아이콘 경로 설정
    try:
        base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
        icon_path_global = os.path.join(base_path, 'assets', 'icon.ico')
        app_name = "Gesture Macro"
        logging.info(f"Icon path set to: {icon_path_global}")
        if not os.path.exists(icon_path_global):
             logging.warning(f"Icon file not found at: {icon_path_global}")
    except Exception as e:
        logging.error("Error setting icon path:", exc_info=True)
        # 아이콘 경로 설정 실패해도 계속 진행

    # 제목 표시줄 아이콘 설정
    if root_window and icon_path_global and os.path.exists(icon_path_global):
        try:
            root_window.iconbitmap(default=icon_path_global)
            logging.info("Window title bar icon set.")
        except Exception as e:
             logging.warning(f"Failed to set title bar icon: {e}")

    # 애플리케이션 이름 설정
    if root_window:
        root_window.title(app_name)

    # 작업표시줄 아이콘 설정 (윈도우 표시 후)
    # set_taskbar_icon 함수는 AppUserModelID 설정으로 대체 가능성 있음 (테스트 필요)
    # if root_window and icon_path_global and os.path.exists(icon_path_global):
    #     root_window.after(100, lambda: set_taskbar_icon(root_window, icon_path_global))

    # --- TrayManager 초기화 및 시작 ---
    try:
        logging.info("Initializing TrayManager...")
        tray_manager = TrayManager(root_window, icon_path_global, app_name, graceful_exit)
        logging.info("Attempting to start TrayManager...")
        if not tray_manager.start():
            logging.warning("Failed to start system tray icon. Continuing without tray support.")
            # 트레이 아이콘 없이 계속 진행
        else:
             logging.info("TrayManager started successfully.")
    except Exception as e:
        logging.error("Failed to initialize or start TrayManager:", exc_info=True)
        tray_manager = None # 실패 시 None 처리

    # 디버깅 정보 출력
    logging.info(f"System: {sys.platform}, CWD: {os.getcwd()}")

    # 인스턴스 생성
    try:
        storage = MacroStorage()
        recorder = MacroRecorder()
        player = MacroPlayer()
        editor = MacroEditor(storage)
        gesture_manager = GestureManager(player, storage, recorder)
        # --- 디버깅 코드 추가 --- 
        print(f"[DEBUG main.py] gesture_manager 생성됨: {gesture_manager}")
        if hasattr(gesture_manager, 'storage'):
            print(f"[DEBUG main.py] gesture_manager.storage: {gesture_manager.storage}")
            print(f"[DEBUG main.py] type(gesture_manager.storage): {type(gesture_manager.storage)}")
        else:
            print("[DEBUG main.py] gesture_manager에 storage 속성 없음!")
        # --- 디버깅 코드 끝 --- 
        logging.info("Core components initialized.")
    except Exception as e:
        logging.error("Failed to initialize core components:", exc_info=True)
        graceful_exit() # 초기화 실패 시 정리 및 종료 시도
        return

    # GUI 초기화 - SimpleGUI 대신 GuiBase 사용
    try:
        gui = GuiBase(root_window, recorder, player, editor, storage, gesture_manager)
        # gui.setup_ui() # GuiBase __init__에서 호출되므로 여기서 제거
        logging.info("GUI initialized using GuiBase.") # 로그 메시지 수정
    except Exception as e:
        logging.error("Failed to initialize GUI:", exc_info=True)
        graceful_exit() # 초기화 실패 시 정리 및 종료 시도
        return

    # 윈도우 표시
    if root_window:
        root_window.deiconify()
        logging.info("Root window shown.")

    # 닫기(X) 버튼 클릭 시 동작 설정
    if root_window:
        if tray_manager and tray_manager.is_running(): # 트레이 매니저가 성공적으로 시작되었는지 확인
            root_window.protocol("WM_DELETE_WINDOW", tray_manager.hide_window)
            logging.info("WM_DELETE_WINDOW bound to hide_window.")
        else:
            root_window.protocol("WM_DELETE_WINDOW", graceful_exit)
            logging.info("WM_DELETE_WINDOW bound to graceful_exit.")

    # 자동으로 제스처 인식 활성화
    if root_window:
        root_window.after(500, auto_enable_gesture)

    # 메인 루프 시작
    try:
        logging.info("Starting Tkinter main loop...")
        if root_window:
            root_window.mainloop()
        # mainloop 정상 종료 후
        logging.info("Tkinter main loop has ended.")
    except KeyboardInterrupt:
        logging.info("KeyboardInterrupt received. Initiating graceful exit...")
        graceful_exit()
    except Exception as e:
         logging.error("Exception during main loop:", exc_info=True)
         graceful_exit() # 예외 발생 시에도 정리 시도
    finally:
        # mainloop가 종료된 후 항상 실행되는 최종 정리
        logging.info("Entering final cleanup phase (finally block)...")
        # graceful_exit가 이미 tray_manager 등을 None으로 만들었을 수 있음
        # 만약 graceful_exit가 호출되지 않은 비정상 종료 시에도 정리 시도
        if tray_manager: # 혹시 아직 남아있다면
             logging.warning("Tray manager still exists in finally block. Attempting stop again.")
             try:
                 tray_manager.stop()
             except Exception as e:
                 logging.error("Error stopping tray_manager in finally block:", exc_info=True)
             tray_manager = None

        # Tkinter 윈도우 파괴 (quit() 이후)
        if root_window:
             logging.info("Destroying Tkinter window in finally block...")
             try:
                 root_window.destroy()
                 logging.info("Tkinter window destroyed in finally block.")
             except Exception as e:
                 logging.warning(f"Error destroying root window in finally block: {e}")
             root_window = None

        # 다른 전역 객체들도 확실히 정리 (선택 사항)
        recorder = None
        gesture_manager = None
        storage = None
        gui = None

        logging.info("Application cleanup finished.")

if __name__ == "__main__":
    main()