# tray_manager.py
import threading
import tkinter as tk
import os
from PIL import Image
import pystray

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
        self.root_window = root_window
        self.icon_path = icon_path
        self.app_name = app_name
        self.app_exit_callback = app_exit_callback # 외부 종료 함수 참조

        self.tray_icon = None
        self.tray_thread = None
        self.is_hidden = False # 창 숨김 상태

        # 아이콘 파일 존재 여부 확인
        if not os.path.exists(self.icon_path):
            print(f"트레이 아이콘 파일을 찾을 수 없습니다: {self.icon_path}")
            self.icon_path = None # 아이콘 경로 없음 처리

    def _setup_tray_icon(self):
        """pystray 아이콘 객체 설정"""
        if not self.icon_path:
            return None

        try:
            image = Image.open(self.icon_path)
            menu = (
                pystray.MenuItem('Show', self.show_window, default=True), # 기본 동작 (더블 클릭)
                pystray.MenuItem('Exit', self._request_exit)
            )
            icon = pystray.Icon(self.app_name, image, self.app_name, menu)
            return icon
        except FileNotFoundError:
            print(f"아이콘 파일을 여는 데 실패했습니다: {self.icon_path}")
            return None
        except Exception as e:
            print(f"트레이 아이콘 설정 중 오류 발생: {e}")
            return None

    def _run_tray_icon(self):
        """트레이 아이콘 실행 (별도 스레드에서)"""
        if self.tray_icon:
            print("Starting tray icon run loop...")
            try:
                self.tray_icon.run()
                print("Tray icon run loop finished.")
            except Exception as e:
                # 트레이 아이콘 스레드 종료 시 발생하는 일반적인 예외 처리
                if "main thread is not in main loop" in str(e).lower():
                    print("Tray icon thread finished normally after main loop exit.")
                else:
                    print(f"Error during tray icon run: {e}")
        else:
             print("Cannot run tray icon: not setup correctly.")


    def start(self):
        """트레이 아이콘 설정 및 스레드 시작"""
        self.tray_icon = self._setup_tray_icon()
        if self.tray_icon:
            # 데몬 스레드로 설정하여 메인 앱 종료 시 함께 종료되도록 함
            self.tray_thread = threading.Thread(target=self._run_tray_icon, daemon=True)
            self.tray_thread.start()
            print("Tray icon thread started.")
            return True
        return False

    def stop(self):
        """트레이 아이콘 중지"""
        if self.tray_icon and self.tray_icon.visible:
            print("Stopping tray icon...")
            try:
                self.tray_icon.stop()
                # 스레드가 완전히 종료될 때까지 잠시 기다릴 수 있음 (선택 사항)
                if self.tray_thread and self.tray_thread.is_alive():
                     self.tray_thread.join(timeout=0.5) # 최대 0.5초 대기
            except Exception as e:
                print(f"Error stopping tray icon: {e}")
        else:
            print("Tray icon not running or already stopped.")


    def hide_window(self):
        """메인 윈도우 숨기기"""
        if self.root_window:
            self.root_window.withdraw()
            self.is_hidden = True
            print("Window hidden.")

    def show_window(self, icon=None, item=None):
        """메인 윈도우 보이기"""
        if self.root_window:
            # Tkinter 메인 스레드에서 실행되도록 예약
            self.root_window.after(0, self.root_window.deiconify)
            self.is_hidden = False
            print("Window shown.")
        # 창 표시 시 트레이 아이콘은 계속 실행 상태 유지

    def _request_exit(self, icon=None, item=None):
        """트레이 메뉴의 'Exit' 클릭 시 호출됨"""
        print("Exit requested from tray menu.")
        if self.app_exit_callback:
            # 등록된 메인 애플리케이션 종료 콜백 함수 호출
            self.app_exit_callback() # icon, item 인자 없이 호출
        else:
            print("No exit callback provided to TrayManager.")
            # 콜백이 없으면 직접 종료 시도 (최후의 수단)
            self.stop() # 트레이 아이콘 먼저 중지 시도
            if self.root_window:
                try:
                    self.root_window.quit()
                    self.root_window.destroy()
                except tk.TclError as e:
                    print(f"Error destroying root window during fallback exit: {e}") 