# gui_base.py
import tkinter as tk
from tkinter import ttk, messagebox

# 생성한 모든 GUI 모듈 임포트
from gui_setup import GuiSetupMixin
from gui_controls import GuiControlsMixin
from gui_event_list import GuiEventListMixin
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

        # 녹화 설정
        self.record_mouse_move = tk.BooleanVar(value=False)
        self.record_delay = tk.BooleanVar(value=True)
        self.use_relative_coords = tk.BooleanVar(value=False) # 상대 좌표 (기본값 False)
        self.use_absolute_coords = tk.BooleanVar(value=True)  # 절대 좌표 (기본값 True)
        self.record_keyboard = tk.BooleanVar(value=True)

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