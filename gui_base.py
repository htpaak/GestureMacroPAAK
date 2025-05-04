# gui_base.py
import tkinter as tk
from tkinter import ttk, messagebox
import platform # 시스템 정보 확인을 위해 추가
import os       # 파일 경로 확인을 위해 추가
import sys      # 실행 파일 경로 확인을 위해 추가

# 생성한 모든 GUI 모듈 임포트
from gui_setup import GuiSetupMixin
from gui_controls import GuiControlsMixin
from gui_event_list import GuiEventListMixin
from gui_gesture_list import GuiGestureListMixin
from gui_recording import GuiRecordingMixin
from gui_playback import GuiPlaybackMixin
from gui_event_editor import GuiEventEditorMixin
from gui_gesture_manager import GuiGestureManagerMixin
from gui_recognition_control import GuiRecognitionControlMixin
from gui_advanced_editor import GuiAdvancedEditorMixin
from gui_utilities import GuiUtilitiesMixin

class GuiBase(
    GuiSetupMixin,
    GuiControlsMixin,
    GuiEventListMixin,
    GuiGestureListMixin,
    GuiRecordingMixin,
    GuiPlaybackMixin,
    GuiEventEditorMixin,
    GuiGestureManagerMixin,
    GuiRecognitionControlMixin,
    GuiAdvancedEditorMixin,
    GuiUtilitiesMixin
):
    """모든 GUI 믹스인을 통합하고 애플리케이션 GUI의 기반을 형성하는 클래스"""

    def __init__(self, root, recorder, player, editor, storage, gesture_manager=None):
        """GUI 초기화"""
        self.root = root
        self.recorder = recorder
        self.player = player
        self.editor = editor
        self.storage = storage
        self.gesture_manager = gesture_manager

        # --- 내부 상태 변수 초기화 (simple_gui.py __init__ 참조) ---
        # 제스처 인식 상태
        self.gesture_enabled = tk.BooleanVar(value=False)

        # 부팅 시 자동 실행 상태 변수 추가
        self.start_on_boot_var = tk.BooleanVar(value=False)

        # 녹화 설정
        self.record_mouse_move = tk.BooleanVar(value=False)
        self.record_delay = tk.BooleanVar(value=True)
        self.use_relative_coords = tk.BooleanVar(value=False) # 상대 좌표 (기본값 False)
        self.use_absolute_coords = tk.BooleanVar(value=True)  # 절대 좌표 (기본값 True)
        self.record_keyboard = tk.BooleanVar(value=True)
        # 좌표 선택 라디오 버튼용 변수 (기본값 'absolute')
        self.coord_selection_var = tk.StringVar(value="absolute")
        self.coord_mode_var = tk.StringVar(value='absolute')

        # 재생 설정
        self.infinite_repeat = tk.BooleanVar(value=False)
        self.repeat_count = tk.StringVar(value="1") # 반복 횟수

        # 이벤트 목록 선택 관련
        self.selected_events = []
        self.restore_selection = True  # 목록 업데이트 시 선택 복원 여부

        # 제스처 목록 선택 관련
        self.selected_gesture_index = None
        self.selected_gesture_name = None

        # 실시간 업데이트 타이머
        self.update_timer = None
        self.update_interval = 100 # ms

        # 상태 표시줄 위젯 (setup_ui 등에서 생성 후 할당 필요)
        self.status_label = None
        self.record_status = None # 녹화 상태 레이블

        # --- 믹스인 초기화 및 UI 설정 ---
        # 필요에 따라 각 믹스인의 초기화 메소드 호출 (예: super().__init__())
        # GuiSetupMixin 에서 UI 생성 메소드 호출
        self.setup_styles() # 스타일 설정 (gui_setup 가정)
        self.setup_ui()     # 기본 UI 구성 (gui_setup 가정)

        # 부팅 시 자동 실행 초기 상태 설정
        self._update_start_on_boot_checkbox_state()

        # 유틸리티 초기화 (예: 단축키 설정)
        self.setup_keyboard_shortcuts() # (gui_utilities 가정)

        # 초기 상태 업데이트 (필요시)
        self.update_gesture_list() # 제스처 목록 로드 (gui_gesture_manager 가정)
        self.update_status("Ready.")

    def update_status(self, message):
        """하단 상태 표시줄 메시지 업데이트"""
        if self.status_label:
            self.status_label.config(text=message)
        else:
            print(f"Status Update (No Label): {message}") # 레이블 없으면 콘솔 출력

    # --- 부팅 시 자동 실행 관련 메소드 추가 ---
    def _toggle_start_on_boot(self):
        """'Start on Boot' 체크박스 상태 변경 시 호출될 콜백 함수"""
        is_enabled = self.start_on_boot_var.get()
        try:
            if is_enabled:
                if self._add_to_startup():
                    self.update_status("Added to startup.")
                else:
                    self.update_status("Failed to add to startup (maybe permissions?).")
                    self.start_on_boot_var.set(False) # 실패 시 체크박스 원상복구
            else:
                if self._remove_from_startup():
                    self.update_status("Removed from startup.")
                else:
                    self.update_status("Failed to remove from startup.")
                    # 제거 실패 시 사용자에게 알리고 상태는 유지할 수 있음
        except Exception as e:
            messagebox.showerror("Startup Error", f"Failed to update startup settings: {e}")
            self.start_on_boot_var.set(not is_enabled) # 오류 발생 시 체크박스 상태 복구

    def _update_start_on_boot_checkbox_state(self):
        """현재 자동 실행 설정을 확인하고 체크박스 상태를 업데이트"""
        try:
            is_set = self._is_startup_enabled()
            self.start_on_boot_var.set(is_set)
            print(f"Initial startup state check: {'Enabled' if is_set else 'Disabled'}") # 디버깅 로그
        except Exception as e:
            print(f"Error checking initial startup state: {e}") # 오류 로깅
            self.start_on_boot_var.set(False) # 오류 시 비활성화 상태로 가정

    def _get_executable_path(self):
        """실행 파일의 경로를 반환 (PyInstaller 환경 고려)"""
        if getattr(sys, 'frozen', False):
            # PyInstaller 등으로 빌드된 경우
            return sys.executable
        else:
            # 일반 파이썬 스크립트로 실행된 경우 (main.py 경로 반환)
            # __file__은 gui_base.py를 가리키므로 main.py 경로를 찾아야 함
            # 가장 간단한 방법은 main.py를 직접 지정하는 것
            # 더 견고한 방법은 프로젝트 루트를 기준으로 찾는 것
            # 여기서는 main.py가 스크립트 실행의 진입점이라고 가정
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) # 프로젝트 루트 추정
            main_script = os.path.join(base_dir, "main.py")
            # main.py가 실제로 존재하는지 확인하는 로직 추가 가능
            # return main_script # 직접 스크립트 경로 반환
            # 스크립트 실행 시에는 python.exe와 스크립트 경로가 필요함
            return f'"{sys.executable}" "{main_script}"'


    def _is_startup_enabled(self):
        """애플리케이션이 시작 프로그램에 등록되어 있는지 확인 (Windows 전용)"""
        if platform.system() != "Windows":
            return False # Windows 외 OS는 지원 안 함

        import winreg
        app_name = "GestureMacroPAAK" # main.py의 app_name과 일치해야 함
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"

        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_READ) as key:
                winreg.QueryValueEx(key, app_name)
            return True # 키가 존재하면 등록된 것
        except FileNotFoundError:
            return False # 키가 없으면 등록 안 된 것
        except Exception as e:
            print(f"Error checking startup registry: {e}")
            return False # 기타 오류 발생 시

    def _add_to_startup(self):
        """애플리케이션을 시작 프로그램에 추가 (Windows 전용, --tray 인자 포함)"""
        if platform.system() != "Windows":
            messagebox.showwarning("Unsupported OS", "Auto-start feature is only available on Windows.")
            return False

        import winreg
        app_name = "GestureMacroPAAK"
        # 실행 경로 가져오기 (인자 없이)
        base_exe_path = self._get_executable_path()
        # 시작 프로그램에 등록할 최종 명령어 (기본 경로 + " --tray")
        startup_command = f'{base_exe_path} --tray'

        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"

        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_WRITE) as key:
                # 수정: startup_command 사용
                winreg.SetValueEx(key, app_name, 0, winreg.REG_SZ, startup_command)
            print(f"Added '{app_name}' to startup: {startup_command}") # 로그에 명령어 출력
            return True
        except Exception as e:
            print(f"Error adding to startup registry: {e}")
            messagebox.showerror("Startup Error", f"Could not add to startup registry:\n{e}\n\nPlease try running as administrator.")
            return False

    def _remove_from_startup(self):
        """애플리케이션을 시작 프로그램에서 제거 (Windows 전용)"""
        if platform.system() != "Windows":
            return False # Windows 외 OS는 지원 안 함

        import winreg
        app_name = "GestureMacroPAAK"
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"

        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_WRITE) as key:
                winreg.DeleteValue(key, app_name)
            print(f"Removed '{app_name}' from startup.")
            return True
        except FileNotFoundError:
            print(f"'{app_name}' not found in startup, nothing to remove.")
            return True # 이미 없는 경우도 성공으로 간주
        except Exception as e:
            print(f"Error removing from startup registry: {e}")
            messagebox.showerror("Startup Error", f"Could not remove from startup registry:\n{e}")
            return False

# --- Mixin 클래스 정의들 ---

class GuiSetupMixin:
    def setup_ui(self):
        """기본 UI 요소들을 설정하고 배치합니다."""
        # 메인 프레임 생성
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(expand=True, fill=tk.BOTH)

        # 상단 프레임 (녹화/재생 제어)
        top_frame = ttk.Frame(main_frame)
        top_frame.pack(side=tk.TOP, fill=tk.X, pady=(0, 10))
        self.setup_control_buttons(top_frame) # GuiControlsMixin 에서 정의

        # 중앙 분할 프레임 (왼쪽: 이벤트 목록, 오른쪽: 제스처 목록/설정)
        center_paned_window = ttk.PanedWindow(main_frame, orient=tk.HORIZONTAL)
        center_paned_window.pack(expand=True, fill=tk.BOTH)

        # 왼쪽 프레임 (이벤트 목록 및 편집)
        left_frame = ttk.Frame(center_paned_window, padding=5)
        center_paned_window.add(left_frame, weight=1)
        self.setup_event_list_ui(left_frame) # GuiEventListMixin 에서 정의
        # 여기에 이벤트 편집 관련 UI 추가 (예: GuiEventEditorMixin 호출)
        self.setup_event_editor_ui(left_frame) # 이벤트 편집기 추가
        self.setup_advanced_editor_ui(left_frame) # 고급 편집기 추가

        # 오른쪽 프레임 (제스처 목록, 설정, 제스처 관리)
        right_frame = ttk.Frame(center_paned_window, padding=5)
        center_paned_window.add(right_frame, weight=1)
        self.setup_gesture_list_ui(right_frame) # GuiGestureListMixin 에서 정의
        self.setup_recording_options(right_frame) # GuiRecordingMixin 에서 정의
        self.setup_playback_options(right_frame) # GuiPlaybackMixin 에서 정의
        self.setup_gesture_management_ui(right_frame) # GuiGestureManagerMixin 에서 정의
        self.setup_recognition_controls(right_frame) # GuiRecognitionControlMixin 에서 정의

        # 하단 프레임 (상태 표시줄 및 자동 실행 체크박스)
        bottom_frame = ttk.Frame(main_frame, padding=(5, 5, 5, 0)) # 하단 패딩 제거
        bottom_frame.pack(side=tk.BOTTOM, fill=tk.X)

        # 상태 표시줄 레이블
        self.status_label = ttk.Label(bottom_frame, text="Ready.", anchor=tk.W)
        self.status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # 부팅 시 자동 실행 체크박스 (Windows 에서만 표시)
        if platform.system() == "Windows":
            self.start_on_boot_checkbox = ttk.Checkbutton(
                bottom_frame,
                text="Start on Boot",
                variable=self.start_on_boot_var,
                command=self._toggle_start_on_boot
            )
            self.start_on_boot_checkbox.pack(side=tk.RIGHT, padx=(5, 0))

        # 녹화 상태 레이블 (필요 시 상태 표시줄 옆에 추가 가능)
        # self.record_status = ttk.Label(bottom_frame, text="", width=15)
        # self.record_status.pack(side=tk.RIGHT)

# 이하 다른 Mixin 클래스들 (GuiControlsMixin, GuiEventListMixin 등)
# ... (내용 생략)