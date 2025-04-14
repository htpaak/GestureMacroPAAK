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

            self.gesture_start_btn = ttk.Button(gesture_button_frame, text="Start Recognition (F11)", width=20,
                               command=start_cmd, style='Big.TButton')
            self.gesture_start_btn.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)

            self.gesture_stop_btn = ttk.Button(gesture_button_frame, text="Stop Recognition (F12)", width=20,
                               command=stop_cmd, state=tk.DISABLED, style='Big.TButton')
            self.gesture_stop_btn.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)
        else:
            # 제스처 매니저가 없을 경우
            no_gesture_label = ttk.Label(self.gesture_control_frame, text="Gesture Manager not available.")
            no_gesture_label.pack(fill=tk.X, pady=5)


    def _create_macro_controls(self):
        """매크로 제어 관련 버튼 및 상태 레이블 생성"""
        # 이 메서드는 self.control_frame이 _create_main_layout에서 생성되었다고 가정합니다.
        if not hasattr(self, 'control_frame'):
             print("Error: control_frame not found in GuiControlsMixin._create_macro_controls")
             return

        # 제어 버튼 프레임
        button_frame = ttk.Frame(self.control_frame)
        button_frame.pack(fill=tk.X, pady=10)

        # 버튼 커맨드에 연결될 메서드들은 다른 믹스인(GuiRecordingMixin 등)에 정의되어야 합니다.
        start_gesture_rec_cmd = getattr(self, 'start_gesture_recording', lambda: print("Start Gesture Recording method not found"))
        start_macro_rec_cmd = getattr(self, 'start_recording_for_selected_gesture', lambda: print("Start Recording for Selected Gesture method not found"))
        stop_rec_cmd = getattr(self, 'stop_recording', lambda: print("Stop Recording method not found"))
        save_macro_cmd = getattr(self, 'save_macro', lambda: print("Save Macro method not found"))

        # 제스처 녹화 버튼 (GestureManager가 있을 경우)
        if hasattr(self, 'gesture_manager') and self.gesture_manager:
            self.gesture_record_btn = ttk.Button(button_frame, text="Record Gesture", width=15,
                     command=start_gesture_rec_cmd)
            self.gesture_record_btn.pack(side=tk.LEFT, padx=10)

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
                                  command=save_macro_cmd, state=tk.NORMAL) # 저장 버튼은 항상 활성화 가정
        self.save_btn.pack(side=tk.LEFT, padx=10)

        # 녹화 상태 표시 레이블
        self.record_status = ttk.Label(self.control_frame, text="Ready", foreground="black", font=('Arial', 9))
        self.record_status.pack(anchor=tk.W, pady=(5, 0))
