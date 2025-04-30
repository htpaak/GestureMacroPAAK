# gui_setup.py
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import os
import sys
from PIL import Image, ImageTk  # PIL 추가 - 아이콘 로드용

class GuiSetupMixin:
    """GUI의 기본 설정 및 레이아웃 구성을 담당하는 믹스인 클래스"""

    def _setup_styles(self):
        """애플리케이션 전체에 적용될 스타일 설정"""
        style = ttk.Style()
        style.theme_use('clam') # 더 현대적인 테마 사용

        # 기본 버튼 스타일 - 모든 버튼은 기본적으로 작게
        style.configure('TButton', font=('Arial', 9), padding=3, width=10)
        style.map('TButton',
                  foreground=[('pressed', 'black'), ('active', 'black')],
                  background=[('pressed', '!disabled', '#bbb'), ('active', '#eee')])

        # 큰 버튼 스타일 (제스처 시작/중지)
        style.configure('Big.TButton', font=('Arial', 11, 'bold'), padding=10)

        # 리스트박스 선택 스타일
        # tk.Listbox는 ttk 스타일을 직접 적용받지 않으므로, config에서 설정

        # 레이블 프레임 스타일
        style.configure('TLabelframe', padding=10, relief="groove")
        style.configure('TLabelframe.Label', font=('Arial', 10, 'bold'), padding=(5, 2))

        # 구분선 스타일
        style.configure('TSeparator', background='#ccc')

    def _setup_window(self, window_width=1200, window_height=1200, min_width=1000, min_height=650):
        """윈도우 크기, 위치, 제목 설정"""
        self.root.title("GestureMacroPAAK")

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
        self.gesture_control_frame.pack(fill=tk.X, pady=(0, 5))
        title_label = ttk.Label(self.gesture_control_frame, text="GestureMacroPAAK", font=('Arial', 12))
        title_label.pack(side=tk.TOP, pady=(0, 5))

        # 구분선
        separator = ttk.Separator(self.main_frame, orient='horizontal')
        separator.pack(fill=tk.X, pady=3)

        # 상단 제어 프레임 (매크로 제어)
        self.control_frame = ttk.LabelFrame(self.main_frame, text="Macro Control", padding=5)
        self.control_frame.pack(fill=tk.X, pady=(0, 5))

        # 메인 컨텐츠 영역 (좌우 분할)
        self.content_frame = ttk.Frame(self.main_frame)
        self.content_frame.pack(fill=tk.BOTH, expand=True)

        # 왼쪽 프레임 (제스처 목록)
        self.left_frame = ttk.Frame(self.content_frame, width=350)
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=(0, 5))
        self.left_frame.pack_propagate(False)

        # 오른쪽 프레임 (이벤트 목록)
        self.right_frame = ttk.Frame(self.content_frame)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))

        # 하단 상태 표시줄 프레임
        self.status_frame = ttk.Frame(self.main_frame, padding=(3, 3))
        self.status_frame.pack(side=tk.BOTTOM, fill=tk.X)

    def _create_status_bar(self):
        """하단 상태 표시줄 생성"""
        self.status_label = ttk.Label(self.status_frame, text="Ready", anchor=tk.W)
        self.status_label.pack(fill=tk.X)

    def setup_styles(self):
        """버튼 스타일 설정 (추출된 코드)"""
        style = ttk.Style()
        # 기본 버튼 스타일 - 원래 크기로 복원 (width 속성 제거)
        style.configure('TButton', font=('Arial', 9), padding=5)
        # 큰 버튼 스타일
        style.configure('Big.TButton', font=('Arial', 11, 'bold'), padding=10)

    def setup_ui(self):
        """간소화된 GUI 구성 (PanedWindow 사용) - 1366x768 크기 최적화"""
        # 메인 프레임 (패딩 최소화)
        main_frame = ttk.Frame(self.root, padding=3) # padding 5 -> 3
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 윈도우 전체에 클릭 이벤트 바인딩 - 제스처 선택 유지
        if hasattr(self, 'ensure_gesture_selection'):
            self.root.bind('<Button-1>', lambda e: self.root.after(10, self.ensure_gesture_selection))

        # 최상단 제스처 인식 제어 프레임 (pady 최소화)
        gesture_control_frame = ttk.Frame(main_frame)
        gesture_control_frame.pack(fill=tk.X, expand=False, pady=(0, 3)) # pady (0, 5) -> (0, 3)

        # 제목 레이블과 아이콘 추가 (pady 최소화)
        title_frame = ttk.Frame(gesture_control_frame)
        title_frame.pack(side=tk.TOP, pady=(0, 3)) # pady (0, 5) -> (0, 3)
        
        # 아이콘 로드 및 표시
        try:
            # 아이콘 파일 경로
            base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
            icon_path = os.path.join(base_path, 'assets', 'icon.ico')
            
            if os.path.exists(icon_path):
                # PIL을 사용하여 아이콘 로드 (ico 파일 지원)
                icon_image = Image.open(icon_path)
                icon_image = icon_image.resize((24, 24), Image.LANCZOS)  # 크기 조정
                
                # Tkinter에서 사용할 수 있는 PhotoImage로 변환
                self.title_icon = ImageTk.PhotoImage(icon_image)
                
                # 아이콘 레이블
                icon_label = ttk.Label(title_frame, image=self.title_icon)
                icon_label.pack(side=tk.LEFT, padx=(0, 5))
                
                # 텍스트 레이블
                text_label = ttk.Label(title_frame, text="GestureMacroPAAK", font=('Arial', 11)) # 12 -> 11 (Optional)
                text_label.pack(side=tk.LEFT)
            else:
                # 아이콘이 없으면 텍스트만 표시
                text_label = ttk.Label(title_frame, text="GestureMacroPAAK", font=('Arial', 11))
                text_label.pack(side=tk.LEFT)
                print("Warning: Icon file not found at:", icon_path)
        except Exception as e:
            # 오류 발생 시 텍스트만 표시
            text_label = ttk.Label(title_frame, text="GestureMacroPAAK", font=('Arial', 11))
            text_label.pack(side=tk.LEFT)
            print(f"Error loading icon: {e}")

        # 제스처 인식 시작/중지 버튼 (폰트, 높이, 테두리, padx 축소)
        if hasattr(self, 'gesture_manager'):
            gesture_button_frame = ttk.Frame(gesture_control_frame)
            gesture_button_frame.pack(fill=tk.X, pady=(2,0)) # 상단 버튼과의 간격 추가
            start_gesture_cmd = getattr(self, 'start_gesture_recognition', lambda: print("start_gesture_recognition not found"))
            stop_gesture_cmd = getattr(self, 'stop_gesture_recognition', lambda: print("stop_gesture_recognition not found"))

            self.gesture_start_btn = tk.Button(
                gesture_button_frame, 
                text="Start Recognition (F11)",
                font=('Arial', 10),  # 11 -> 10
                bg='#e8e8e8',  # 배경색
                relief=tk.RAISED,  # 테두리 스타일
                borderwidth=2,  # 3 -> 2
                command=start_gesture_cmd,
                highlightthickness=0,  # 하이라이트 테두리 제거
                height=1  # 2 -> 1
            )
            self.gesture_start_btn.pack(side=tk.LEFT, padx=3, fill=tk.X, expand=True) # padx 5 -> 3

            self.gesture_stop_btn = tk.Button(
                gesture_button_frame, 
                text="Stop Recognition (F12)",
                font=('Arial', 10),  # 11 -> 10
                bg='#e8e8e8',
                relief=tk.RAISED,
                borderwidth=2,  # 3 -> 2
                command=stop_gesture_cmd,
                state=tk.DISABLED,
                highlightthickness=0,
                height=1  # 2 -> 1
            )
            self.gesture_stop_btn.pack(side=tk.LEFT, padx=3, fill=tk.X, expand=True) # padx 5 -> 3

        # 구분선 추가 (pady 최소화)
        separator = ttk.Separator(main_frame, orient='horizontal')
        separator.pack(fill=tk.X, pady=2) # pady 3 -> 2

        # 상단 제어 프레임 (패딩, pady 최소화)
        control_frame = ttk.LabelFrame(main_frame, text="Macro Control", padding=3) # padding 5 -> 3
        control_frame.pack(fill=tk.X, expand=False, pady=(0, 3)) # pady (0, 5) -> (0, 3)

        # 제어 버튼 프레임 (pady 최소화)
        button_frame = tk.Frame(control_frame) # height, bg 제거
        button_frame.pack(fill=tk.X, expand=True, pady=1) # pady 2 -> 1

        start_gesture_rec_cmd = getattr(self, 'start_gesture_recording', lambda: print("start_gesture_recording not found"))
        start_macro_rec_cmd = getattr(self, 'start_recording_for_selected_gesture', lambda: print("start_recording_for_selected_gesture not found"))
        toggle_rec_cmd = getattr(self, 'toggle_recording', lambda: print("Toggle Recording method not found"))
        save_macro_cmd = getattr(self, 'save_macro', lambda: print("save_macro not found"))

        # 제어 버튼 (폰트, padx, pady 축소)
        if hasattr(self, 'gesture_manager'):
            self.record_gesture_btn = tk.Button(
                button_frame, 
                text="Start Recording Gesture",
                font=('Arial', 9), # 10 -> 9
                bg='#e8e8e8',  # 배경색
                relief=tk.RAISED,  # 테두리 스타일
                borderwidth=2,  # 테두리 두께
                command=lambda: self.gesture_manager.start_gesture_recording(), # gesture_manager의 start_gesture_recording 직접 호출
                highlightthickness=0  # 하이라이트 테두리 제거
            )
            self.record_gesture_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2, pady=2) # 3 -> 2
        
        self.record_btn = tk.Button(
            button_frame, 
            text="Start Recording Macro (F9)",
            font=('Arial', 9), # 10 -> 9
            bg='#e8e8e8',
            relief=tk.RAISED,
            borderwidth=2,
            command=toggle_rec_cmd,
            highlightthickness=0
        )
        self.record_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2, pady=2) # 3 -> 2

        self.save_macro_btn = tk.Button(
            button_frame,
            text="Save Macro",
            font=('Arial', 9), # 10 -> 9
            bg='#e8e8e8',
            relief=tk.RAISED,
            borderwidth=2,
            command=save_macro_cmd,
            highlightthickness=0
        )
        self.save_macro_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2, pady=2) # 3 -> 2

        # 녹화 상태 레이블 프레임 (pady 최소화, 높이 축소)
        status_label_frame = tk.Frame(control_frame, height=25, bg='#f0f0f0') # height 30->25
        status_label_frame.pack(fill=tk.X, expand=True, pady=(1, 0)) # pady (2, 0) -> (1, 0)

        self.record_status = tk.Label(status_label_frame, text="Ready", bg='#f0f0f0', font=('Arial', 9))
        self.record_status.place(relx=0.5, rely=0.5, anchor='center')

        # 구분선 추가 (pady 최소화)
        separator2 = ttk.Separator(main_frame, orient='horizontal')
        separator2.pack(fill=tk.X, pady=2) # pady 3 -> 2

        # PanedWindow 생성 (pady 최소화)
        paned_window = ttk.PanedWindow(main_frame, orient=tk.HORIZONTAL)
        paned_window.pack(fill=tk.BOTH, expand=True, pady=(0, 2)) # pady (0, 3) -> (0, 2)

        # 왼쪽 프레임 (Frame -> LabelFrame 변경, text 복원)
        left_frame = ttk.LabelFrame(paned_window, text="Gesture List", padding=2) # Frame -> LabelFrame, text 복원
        paned_window.add(left_frame, weight=1) # weight 유지
        if hasattr(self, '_create_gesture_list_widgets'):
            self._create_gesture_list_widgets(left_frame) # 이 함수는 내부 LabelFrame을 만들지 않음

        # 오른쪽 프레임 (Event List - LabelFrame 유지)
        right_frame = ttk.LabelFrame(paned_window, text="Event List", padding=2) # padding 3 -> 2
        paned_window.add(right_frame, weight=2) # weight 유지
        if hasattr(self, '_create_event_list_widgets'):
            self._create_event_list_widgets(right_frame)

        # 하단 상태 표시줄 프레임 (패딩 최소화)
        self.status_frame = ttk.Frame(main_frame, padding=(2, 2)) # padding (3, 3) -> (2, 2)
        self.status_frame.pack(side=tk.BOTTOM, fill=tk.X)
        self._create_status_bar() # 상태 표시줄 생성 호출

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