# tray_manager.py
import threading
import tkinter as tk
import os
import logging # 로깅 추가
from PIL import Image
import pystray

# 로거 설정 (main.py에서 설정된 로거를 사용하거나, 자체 로거 설정)
logger = logging.getLogger(__name__)

class TrayManager:
    """시스템 트레이 아이콘 관리를 위한 클래스"""

    def __init__(self, root_window, icon_path, app_name, app_exit_callback):
        """
        TrayManager 초기화

        Args:
            root_window (tk.Tk): 메인 애플리케이션 윈도우
            icon_path (str): 트레이 아이콘으로 사용할 .ico 파일 경로
            app_name (str): 애플리케이션 이름 (트레이 아이콘 툴팁 등에 사용)
            app_exit_callback (callable): 트레이 아이콘 'Exit' 메뉴 클릭 시 호출될 콜백 함수
        """
        logger.info(f"Initializing TrayManager for {app_name}...")
        self.root_window = root_window
        self.icon_path = icon_path
        self.app_name = app_name
        self.app_exit_callback = app_exit_callback

        self.tray_icon = None
        self.tray_thread = None
        self.is_hidden = False
        self._is_running = False # 트레이 아이콘 실행 상태 플래그 추가

        if not os.path.exists(self.icon_path):
            logger.warning(f"Tray icon file not found: {self.icon_path}")
            self.icon_path = None
        else:
             logger.info(f"Using tray icon: {self.icon_path}")

    def _setup_tray_icon(self):
        """pystray 아이콘 객체 설정"""
        if not self.icon_path:
            logger.warning("Cannot setup tray icon: icon path is None.")
            return None
        try:
            logger.info("Setting up pystray.Icon object...")
            image = Image.open(self.icon_path)
            menu = (
                pystray.MenuItem('Show', self.show_window, default=True),
                pystray.MenuItem('Exit', self._request_exit)
            )
            icon = pystray.Icon(self.app_name, image, self.app_name, menu)
            logger.info("pystray.Icon object created successfully.")
            return icon
        except FileNotFoundError:
            logger.error(f"Failed to open icon file: {self.icon_path}")
            return None
        except Exception as e:
            logger.error("Error setting up tray icon:", exc_info=True)
            return None

    def _run_tray_icon(self):
        """트레이 아이콘 실행 (별도 스레드에서)"""
        if self.tray_icon:
            thread_id = threading.get_ident()
            logger.info(f"Starting tray icon run loop in thread {thread_id}...")
            self._is_running = True # 실행 상태 설정
            try:
                self.tray_icon.run()
                # run()이 정상적으로 종료되면 (stop() 호출 시)
                logger.info(f"Tray icon run loop finished in thread {thread_id}.")
            except Exception as e:
                # 트레이 아이콘 스레드 종료 시 발생하는 일반적인 예외 처리
                if "main thread is not in main loop" in str(e).lower():
                    logger.info(f"Tray icon thread {thread_id} finished normally after main loop exit.")
                elif "AttributeError: 'NoneType' object has no attribute '_hwnd'" in str(e):
                     logger.warning(f"Known issue in pystray occurred during shutdown in thread {thread_id}.")
                else:
                    logger.error(f"Error during tray icon run in thread {thread_id}:", exc_info=True)
            finally:
                self._is_running = False # 종료 시 상태 업데이트
                logger.info(f"Tray icon thread {thread_id} is terminating.")
        else:
            logger.error("Cannot run tray icon: not setup correctly.")
            self._is_running = False

    def start(self):
        """트레이 아이콘 설정 및 스레드 시작"""
        if self.tray_thread and self.tray_thread.is_alive():
            logger.warning("Tray icon thread is already running.")
            return True

        self.tray_icon = self._setup_tray_icon()
        if self.tray_icon:
            logger.info("Starting tray icon thread...")
            # 데몬 스레드로 설정
            self.tray_thread = threading.Thread(target=self._run_tray_icon, daemon=True)
            self.tray_thread.start()
            logger.info(f"Tray icon thread started with ID: {self.tray_thread.ident}")
            # 스레드가 실제로 시작될 때까지 잠시 기다리는 것이 도움이 될 수 있음 (선택 사항)
            # time.sleep(0.1)
            return True
        else:
             logger.error("Failed to start tray icon: setup failed.")
             return False

    def stop(self):
        """트레이 아이콘 중지"""
        logger.info("Stop requested for TrayManager.")
        if self.tray_icon and self.tray_thread and self.tray_thread.is_alive():
            thread_id = self.tray_thread.ident
            logger.info(f"Attempting to stop tray icon and join thread {thread_id}...")
            try:
                self.tray_icon.stop()
                logger.info(f"pystray icon stop() called for thread {thread_id}.")
                # 스레드가 완전히 종료될 때까지 대기
                self.tray_thread.join(timeout=1.5) # 타임아웃 약간 늘림
                if self.tray_thread.is_alive():
                    logger.warning(f"Warning: Tray thread {thread_id} did not terminate within timeout.")
                else:
                    logger.info(f"Tray thread {thread_id} joined successfully.")
            except RuntimeError as e:
                 # pystray 내부에서 발생하는 경우 있음
                 logger.warning(f"RuntimeError during tray icon stop/join for thread {thread_id}: {e}")
            except Exception as e:
                logger.error(f"Error stopping tray icon for thread {thread_id}:", exc_info=True)
            finally:
                # 정리
                logger.info(f"Cleaning up resources for thread {thread_id}.")
                self.tray_icon = None
                self.tray_thread = None
                self._is_running = False # 상태 업데이트
        elif self.tray_icon:
             logger.warning("Tray icon exists but thread is not alive or not started. Cleaning up icon.")
             self.tray_icon = None
             self._is_running = False
        else:
            logger.info("Tray icon not running or already stopped/cleaned up.")
            self._is_running = False # 확실히 False로 설정

    def is_running(self):
         """트레이 아이콘이 현재 실행 중인지 확인"""
         return self._is_running and self.tray_thread and self.tray_thread.is_alive()

    def hide_window(self):
        """메인 윈도우 숨기기"""
        if self.root_window:
            logger.info("Hiding main window.")
            self.root_window.withdraw()
            self.is_hidden = True

    def show_window(self, icon=None, item=None):
        """메인 윈도우 보이기"""
        if self.root_window:
            logger.info("Showing main window.")
            # Tkinter 메인 스레드에서 실행되도록 예약
            self.root_window.after(0, self._show_window_action)
            self.is_hidden = False

    def _show_window_action(self):
        """실제 윈도우 표시 작업 (after 콜백용)"""
        if self.root_window:
            try:
                 # 윈도우 상태 복원 및 활성화 시도
                 self.root_window.deiconify()
                 self.root_window.lift()
                 self.root_window.focus_force()
                 logger.info("Window shown and activated.")
            except tk.TclError as e:
                 logger.warning(f"Error showing/activating window: {e}")

    def _request_exit(self, icon=None, item=None):
        """트레이 메뉴의 'Exit' 클릭 시 호출됨"""
        logger.info("Exit requested from tray menu.")
        if self.app_exit_callback:
            logger.info("Calling the application exit callback.")
            # 등록된 메인 애플리케이션 종료 콜백 함수 호출
            self.app_exit_callback()
        else:
            logger.error("No exit callback provided to TrayManager. Attempting fallback exit...")
            # 콜백이 없으면 직접 종료 시도 (최후의 수단)
            self.stop() # 트레이 아이콘 먼저 중지 시도
            if self.root_window:
                try:
                    logger.info("Attempting to destroy root window directly.")
                    self.root_window.quit()
                    self.root_window.destroy()
                except tk.TclError as e:
                    logger.error(f"Error destroying root window during fallback exit: {e}") 