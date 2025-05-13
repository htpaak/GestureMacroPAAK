# gui_controls.py
import tkinter as tk
from tkinter import ttk

class GuiControlsMixin:
    """GUI의 주요 제어 버튼 및 상태 표시 생성을 담당하는 믹스인 클래스"""

    def _create_gesture_controls(self):
        """최상단 제스처 인식 시작/중지 버튼 생성"""
        # 이 메서드는 self.gesture_manager와 self.gesture_control_frame이
        # __init__과 _create_main_layout에서 생성되었다고 가정합니다.
        if not hasattr(self, 'gesture_control_frame'):
             print("Error: gesture_control_frame not found in GuiControlsMixin._create_gesture_controls")
             return

        if hasattr(self, 'gesture_manager') and self.gesture_manager:
            gesture_button_frame = ttk.Frame(self.gesture_control_frame)
            gesture_button_frame.pack(fill=tk.X)

            # 버튼 커맨드에 연결될 메서드 (start/stop_gesture_recognition)는
            # GuiRecognitionControlMixin 등에 정의되어 있어야 합니다.
            start_cmd = getattr(self, 'start_gesture_recognition', lambda: print("Start Recognition method not found"))
            stop_cmd = getattr(self, 'stop_gesture_recognition', lambda: print("Stop Recognition method not found"))

            self.gesture_start_btn = ttk.Button(gesture_button_frame, text="Start Recognition (Ctrl+F11)", width=20,
                               command=start_cmd, style='Big.TButton')
            self.gesture_start_btn.pack(side=tk.LEFT, padx=5, pady=5)

            self.gesture_stop_btn = ttk.Button(gesture_button_frame, text="Stop Recognition (Ctrl+F12)", width=20,
                               command=stop_cmd, state=tk.DISABLED, style='Big.TButton')
            self.gesture_stop_btn.pack(side=tk.LEFT, padx=5, pady=5)
        else:
            # 제스처 매니저가 없을 경우
            no_gesture_label = ttk.Label(self.gesture_control_frame, text="Gesture Manager not available.")
            no_gesture_label.pack(fill=tk.X, pady=5)


    def _create_macro_controls(self):
        """매크로 제어 관련 버튼 및 상태 레이블 생성"""
        if not hasattr(self, 'control_frame'):
             print("Error: control_frame not found in GuiControlsMixin._create_macro_controls")
             return

        # 버튼 프레임을 일반 tk.Frame으로 생성
        button_frame = tk.Frame(self.control_frame, bg='#f0f0f0', height=45)
        button_frame.pack(fill=tk.X, pady=10)
        # 프레임 크기 고정
        button_frame.pack_propagate(False)

        # 버튼 커맨드 정의
        start_gesture_rec_cmd = getattr(self, 'start_gesture_recording', lambda: print("Start Gesture Recording method not found"))
        toggle_rec_cmd = getattr(self, 'toggle_recording', lambda: print("Toggle Recording method not found"))
        save_macro_cmd = getattr(self, 'save_macro', lambda: print("Save Macro method not found"))
        
        # 레이아웃 계산을 위한 변수
        btn_count = 4 if hasattr(self, 'gesture_manager') and self.gesture_manager else 3
        btn_width = 1.0 / btn_count  # 균등 분할
        
        # 버튼 생성 - 일반 tk.Button 사용 (ttk와 완전히 분리)
        # 각 버튼에 고정 크기와 색상, 글꼴 등을 설정
        
        btn_idx = 0
        
        # 제스처 녹화 버튼
        if hasattr(self, 'gesture_manager') and self.gesture_manager:
            self.record_gesture_btn = tk.Button(
                button_frame, 
                text="Start Recording Gesture",
                font=('Arial', 9),
                bg='#e8e8e8',  # 배경색
                relief=tk.RAISED,  # 테두리 스타일
                borderwidth=2,  # 테두리 두께
                command=lambda: self.gui_gesture_manager.prompt_start_gesture_recording(
                    is_user_initiated=True
                ),
                highlightthickness=0  # 하이라이트 테두리 제거
            )
            # place로 절대 위치 지정
            self.record_gesture_btn.place(
                relx=btn_width * btn_idx + 0.01,  # 1% 여백
                rely=0.5,
                relwidth=btn_width - 0.02,  # 2% 여백
                relheight=0.8,
                anchor='w'
            )
            btn_idx += 1
        
        # 매크로 녹화 버튼
        self.record_btn = ttk.Button(
            button_frame, 
            text="Start Recording Macro (Ctrl+F9)",
            width=20,
            command=toggle_rec_cmd,
            style='Big.TButton'
        )
        self.record_btn.pack(side=tk.LEFT, padx=5, pady=5)
        btn_idx += 1
        
        # 저장 버튼
        self.save_btn = tk.Button(
            button_frame, 
            text="Save Macro",
            font=('Arial', 9),
            bg='#e8e8e8',
            relief=tk.RAISED,
            borderwidth=2,
            command=save_macro_cmd,
            highlightthickness=0
        )
        self.save_btn.place(
            relx=btn_width * btn_idx + 0.01,
            rely=0.5,
            relwidth=btn_width - 0.02,
            relheight=0.8,
            anchor='w'
        )

        # 녹화 상태 표시 레이블
        self.record_status = ttk.Label(self.control_frame, text="Ready", foreground="black", font=('Arial', 9))
        self.record_status.pack(anchor=tk.W, pady=(5, 0))
