# gui_setup.py
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

class GuiSetupMixin:
    """GUI의 기본 설정 및 레이아웃 구성을 담당하는 믹스인 클래스"""

    def _setup_styles(self):
        """애플리케이션 전체에 적용될 스타일 설정"""
        style = ttk.Style()
        style.theme_use('clam') # 더 현대적인 테마 사용

        # 기본 버튼 스타일
        style.configure('TButton', padding=6, relief="flat", background="#ccc", font=('Arial', 10))
        style.map('TButton',
                  foreground=[('pressed', 'black'), ('active', 'black')],
                  background=[('pressed', '!disabled', '#bbb'), ('active', '#eee')])

        # 큰 버튼 스타일 (제스처 시작/중지)
        style.configure('Big.TButton', font=('Arial', 12, 'bold'), padding=10)

        # 리스트박스 선택 스타일
        # tk.Listbox는 ttk 스타일을 직접 적용받지 않으므로, config에서 설정

        # 레이블 프레임 스타일
        style.configure('TLabelframe', padding=10, relief="groove")
        style.configure('TLabelframe.Label', font=('Arial', 10, 'bold'), padding=(5, 2))

        # 구분선 스타일
        style.configure('TSeparator', background='#ccc')

    def _setup_window(self, window_width=1200, window_height=1200, min_width=1000, min_height=800):
        """윈도우 크기, 위치, 제목 설정"""
        self.root.title("Gesture Macro")

        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2

        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.root.minsize(min_width, min_height)

        self.root.lift() # 창을 맨 앞으로
        self.root.focus_force() # 강제로 포커스

    def _create_main_layout(self):
        """메인 프레임 및 기본 레이아웃 구조 생성"""
        self.main_frame = ttk.Frame(self.root, padding=20)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # 최상단 제스처 인식 제어 프레임
        self.gesture_control_frame = ttk.Frame(self.main_frame)
        self.gesture_control_frame.pack(fill=tk.X, pady=(0, 15))
        title_label = ttk.Label(self.gesture_control_frame, text="Gesture Macro", font=('Arial', 12, 'bold'))
        title_label.pack(side=tk.TOP, pady=(0, 10))

        # 구분선
        separator = ttk.Separator(self.main_frame, orient='horizontal')
        separator.pack(fill=tk.X, pady=10)

        # 상단 제어 프레임 (매크로 제어)
        self.control_frame = ttk.LabelFrame(self.main_frame, text="Macro Control", padding=15)
        self.control_frame.pack(fill=tk.X, pady=(0, 15))

        # 메인 컨텐츠 영역 (좌우 분할)
        self.content_frame = ttk.Frame(self.main_frame)
        self.content_frame.pack(fill=tk.BOTH, expand=True)

        # 왼쪽 프레임 (제스처 목록)
        self.left_frame = ttk.Frame(self.content_frame, width=300)
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=(0, 5))
        self.left_frame.pack_propagate(False)

        # 오른쪽 프레임 (이벤트 목록)
        self.right_frame = ttk.Frame(self.content_frame)
        self.right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 0))

        # 하단 상태 표시줄 프레임
        self.status_frame = ttk.Frame(self.main_frame, padding=(5, 5))
        self.status_frame.pack(side=tk.BOTTOM, fill=tk.X)

    def _create_status_bar(self):
        """하단 상태 표시줄 생성"""
        self.status_label = ttk.Label(self.status_frame, text="Ready", anchor=tk.W)
        self.status_label.pack(fill=tk.X)

    def setup_styles(self):
        """버튼 스타일 설정 (추출된 코드)"""
        style = ttk.Style()
        style.configure('Big.TButton', font=('Arial', 11, 'bold'), padding=10)

    def setup_ui(self):
        """간소화된 GUI 구성 (추출된 코드)"""
        # 메인 프레임
        main_frame = ttk.Frame(self.root, padding=20)  # 패딩 증가
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 윈도우 전체에 클릭 이벤트 바인딩 - 제스처 선택 유지
        if hasattr(self, 'ensure_gesture_selection'):
            self.root.bind('<Button-1>', lambda e: self.root.after(10, self.ensure_gesture_selection))

        # 최상단 제스처 인식 제어 프레임 (전체 UI 위에 배치)
        gesture_control_frame = ttk.Frame(main_frame)
        gesture_control_frame.pack(fill=tk.X, pady=(0, 15))

        # 제목 레이블 추가
        title_label = ttk.Label(gesture_control_frame, text="Gesture Macro", font=('Arial', 12, 'bold')) # UI 텍스트는 영어로
        title_label.pack(side=tk.TOP, pady=(0, 10))

        # 제스처 인식 시작/중지 버튼
        if hasattr(self, 'gesture_manager'):
            gesture_button_frame = ttk.Frame(gesture_control_frame)
            gesture_button_frame.pack(fill=tk.X)

            start_gesture_cmd = getattr(self, 'start_gesture_recognition', lambda: print("start_gesture_recognition not found"))
            stop_gesture_cmd = getattr(self, 'stop_gesture_recognition', lambda: print("stop_gesture_recognition not found"))

            self.gesture_start_btn = ttk.Button(gesture_button_frame, text="Start Recognition (F11)", width=20,
                               command=start_gesture_cmd, style='Big.TButton')
            self.gesture_start_btn.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)

            self.gesture_stop_btn = ttk.Button(gesture_button_frame, text="Stop Recognition (F12)", width=20,
                               command=stop_gesture_cmd, state=tk.DISABLED, style='Big.TButton')
            self.gesture_stop_btn.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)

        # 구분선 추가
        separator = ttk.Separator(main_frame, orient='horizontal')
        separator.pack(fill=tk.X, pady=10)

        # 상단 제어 프레임 (매크로 녹화 등)
        control_frame = ttk.LabelFrame(main_frame, text="Macro Control", padding=15) # UI 텍스트는 영어로
        control_frame.pack(fill=tk.X, pady=(0, 15))

        # 제어 버튼 프레임
        button_frame = ttk.Frame(control_frame)
        button_frame.pack(fill=tk.X, pady=10)

        start_gesture_rec_cmd = getattr(self, 'start_gesture_recording', lambda: print("start_gesture_recording not found"))
        start_macro_rec_cmd = getattr(self, 'start_recording_for_selected_gesture', lambda: print("start_recording_for_selected_gesture not found"))
        stop_rec_cmd = getattr(self, 'stop_recording', lambda: print("stop_recording not found"))
        save_macro_cmd = getattr(self, 'save_macro', lambda: print("save_macro not found"))

        # 제스처 녹화 버튼
        if hasattr(self, 'gesture_manager'):
            ttk.Button(button_frame, text="Record Gesture", width=15,
                     command=start_gesture_rec_cmd).pack(side=tk.LEFT, padx=10)

        # 매크로 녹화 버튼
        self.record_btn = ttk.Button(button_frame, text="Record Macro (F9)",
                                    width=15,
                                    command=start_macro_rec_cmd)
        self.record_btn.pack(side=tk.LEFT, padx=10)

        # 녹화 중지 버튼
        self.stop_btn = ttk.Button(button_frame, text="Stop Recording (F10)",
                                  width=15,
                                  command=stop_rec_cmd, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=10)

        # 저장 버튼
        self.save_btn = ttk.Button(button_frame, text="Save Macro",
                                  width=15,
                                  command=save_macro_cmd, state=tk.NORMAL)
        self.save_btn.pack(side=tk.LEFT, padx=10)

        # 녹화 상태 표시
        self.record_status = ttk.Label(control_frame, text="Ready", foreground="black")
        self.record_status.pack(anchor=tk.W, pady=(5, 0))

        # 메인 컨텐츠 영역 - 좌우 분할
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True)

        # 왼쪽 프레임 - 제스처 목록 (가로 크기를 줄임)
        self.left_frame = ttk.Frame(content_frame, width=300) # Make left_frame an instance variable
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=(0, 5))
        self.left_frame.pack_propagate(False)

        # 오른쪽 프레임 - 이벤트 목록
        self.right_frame = ttk.Frame(content_frame) # Make right_frame an instance variable
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))

        # --- 각 영역 위젯 생성 호출 --- (다른 믹스인에서 구현)
        if hasattr(self, '_create_gesture_list_widgets') and callable(self._create_gesture_list_widgets):
            self._create_gesture_list_widgets(self.left_frame)
        else:
             print("Warning: _create_gesture_list_widgets method not found.")

        if hasattr(self, '_create_event_list_widgets') and callable(self._create_event_list_widgets):
            self._create_event_list_widgets(self.right_frame)
        else:
             print("Warning: _create_event_list_widgets method not found.")

        # 상태 표시줄
        self.status_label = ttk.Label(main_frame, text="Ready", relief=tk.SUNKEN, anchor=tk.W)
        self.status_label.pack(fill=tk.X, side=tk.BOTTOM, pady=(10, 0))

        # --- Add Gesture Manager Callbacks (extracted from backup) ---
        if hasattr(self, 'gesture_manager') and self.gesture_manager:
            print("Setting up Gesture Manager callbacks...")
            update_list_cb = getattr(self, 'update_gesture_list', None)
            record_macro_cb = getattr(self, 'start_macro_for_gesture', None)

            # 제스처 목록 업데이트 콜백
            if hasattr(self.gesture_manager, 'set_update_gesture_list_callback') and callable(update_list_cb):
                 self.gesture_manager.set_update_gesture_list_callback(update_list_cb)
                 print("Gesture list update callback set.")
            else:
                 print("Warning: Could not set gesture list update callback.")

            # 매크로 녹화 요청 콜백
            if hasattr(self.gesture_manager, 'set_macro_record_callback') and callable(record_macro_cb):
                 self.gesture_manager.set_macro_record_callback(record_macro_cb)
                 print("Macro record callback set.")
            else:
                 print("Warning: Could not set macro record callback.")

            # GUI 참조 콜백 (주석 해제)
            if hasattr(self.gesture_manager, 'set_gui_callback'):
                 self.gesture_manager.set_gui_callback(self)
                 print("GUI reference callback set.")
            else:
                 print("Warning: Could not set GUI reference callback.")