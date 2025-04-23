# gui_gesture_list.py
import tkinter as tk
from tkinter import ttk

class GuiGestureListMixin:
    """GUI의 제스처 목록(왼쪽 프레임) UI 요소 생성을 담당하는 믹스인 클래스"""

    def _create_gesture_list_widgets(self, parent_frame):
        """왼쪽 프레임에 제스처 목록 관련 위젯들 생성"""
        print("DEBUG: Entering gui_gesture_list._create_gesture_list_widgets") # 함수 시작 확인

        # 제스처 리스트박스 및 스크롤바 (parent_frame에 직접 배치)
        gesture_scrollbar = ttk.Scrollbar(parent_frame) # gesture_frame -> parent_frame
        gesture_scrollbar.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 5), pady=(5, 2)) # 스크롤바 패딩 유지

        self.gesture_listbox = tk.Listbox(parent_frame, font=('Consolas', 11), # gesture_frame -> parent_frame, height 제거
                                         selectmode=tk.SINGLE, # 단일 선택 모드로 변경 (원본 EXTENDED는 다중 선택 로직 필요)
                                         exportselection=False)
        self.gesture_listbox.pack(fill=tk.BOTH, expand=True, padx=(5, 0), pady=(5, 2)) # 리스트박스 패딩 유지
        self.gesture_listbox.config(yscrollcommand=gesture_scrollbar.set,
                                   selectbackground='#4a6cd4', # 원본 스타일 유지
                                   selectforeground='white')
        gesture_scrollbar.config(command=self.gesture_listbox.yview)

        # 제스처 선택 및 포커스 관련 이벤트 바인딩 (커맨드는 다른 믹스인에서 정의됨)
        on_select_cmd = getattr(self, 'on_gesture_select', lambda event: print("on_gesture_select not implemented"))
        maintain_cmd = getattr(self, 'maintain_gesture_selection', lambda event: print("maintain_gesture_selection not implemented"))
        double_click_cmd = getattr(self, 'on_gesture_double_click', lambda event: print("on_gesture_double_click not implemented"))
        self.gesture_listbox.bind('<<ListboxSelect>>', on_select_cmd)
        self.gesture_listbox.bind('<FocusOut>', maintain_cmd)
        self.gesture_listbox.bind('<Double-1>', double_click_cmd)

        # 제스처 목록 아래 버튼 프레임 (parent_frame에 배치 - 기존 코드 유지)
        gesture_btn_frame = ttk.Frame(parent_frame)
        gesture_btn_frame.pack(fill=tk.X, pady=(2, 1))

        # 버튼 콜백 가져오기
        edit_cmd = getattr(self, 'edit_gesture', lambda: print("edit_gesture not found"))
        delete_cmd = getattr(self, 'delete_selected_gesture', lambda: print("delete_selected_gesture not found"))
        move_up_cmd = getattr(self, 'move_gesture_up', lambda: print("move_gesture_up not found"))
        move_down_cmd = getattr(self, 'move_gesture_down', lambda: print("move_gesture_down not found"))

        # 버튼 스타일 설정 변수 (폰트 크기, 패딩 축소, 고정 너비 추가)
        btn_padx_outer = 2
        btn_pady_outer = 1
        btn_font_size = 8
        btn_width = 14

        # --- Edit 버튼 (고정 너비 적용, fill/expand 제거) ---
        edit_button = tk.Button(gesture_btn_frame, text="Edit",
                 font=('Arial', btn_font_size),
                 bg='#e8e8e8',
                 relief=tk.RAISED,
                 borderwidth=2,
                 highlightthickness=0,
                 width=btn_width,
                 command=edit_cmd)
        edit_button.pack(side=tk.LEFT, padx=btn_padx_outer, pady=btn_pady_outer)

        # --- Delete 버튼 (고정 너비 적용, fill/expand 제거) ---
        delete_button = tk.Button(gesture_btn_frame, text="Delete",
                 font=('Arial', btn_font_size),
                 bg='#e8e8e8',
                 relief=tk.RAISED,
                 borderwidth=2,
                 highlightthickness=0,
                 width=btn_width,
                 command=delete_cmd)
        delete_button.pack(side=tk.LEFT, padx=btn_padx_outer, pady=btn_pady_outer)

        # --- 화살표 버튼 (기존 고정 크기 유지) ---
        down_arrow_button = tk.Button(gesture_btn_frame, text="↓",
                 font=('Arial', btn_font_size),
                 bg='#e8e8e8',
                 relief=tk.RAISED,
                 borderwidth=2,
                 highlightthickness=0,
                 width=3,
                 command=move_down_cmd)
        down_arrow_button.pack(side=tk.RIGHT, padx=btn_padx_outer, pady=btn_pady_outer)

        up_arrow_button = tk.Button(gesture_btn_frame, text="↑",
                 font=('Arial', btn_font_size),
                 bg='#e8e8e8',
                 relief=tk.RAISED,
                 borderwidth=2,
                 highlightthickness=0,
                 width=3,
                 command=move_up_cmd)
        up_arrow_button.pack(side=tk.RIGHT, padx=btn_padx_outer, pady=btn_pady_outer)

        # --- 반복 실행 제어 위젯 추가 (pady 최소화) ---
        repeat_frame = ttk.Frame(parent_frame)
        repeat_frame.pack(fill=tk.X, pady=(1, 1))

        ttk.Label(repeat_frame, text="Repeat Count:", font=('Arial', 9)).pack(side=tk.LEFT, padx=3)

        # GuiBase에서 정의된 변수 사용 (없으면 생성)
        if not hasattr(self, 'repeat_count'): self.repeat_count = tk.StringVar(value="1")
        self.repeat_count_entry = ttk.Entry(repeat_frame, textvariable=self.repeat_count, width=5)
        self.repeat_count_entry.pack(side=tk.LEFT, padx=(0,3))

        infinite_frame = ttk.Frame(parent_frame)
        infinite_frame.pack(fill=tk.X, pady=(1, 2))

        # GuiBase에서 정의된 변수 사용 (없으면 생성)
        if not hasattr(self, 'infinite_repeat'): self.infinite_repeat = tk.BooleanVar(value=False)
        # toggle_infinite_repeat 콜백 가져오기 (GuiPlaybackMixin 등에 있어야 함)
        toggle_infinite_cmd = getattr(self, 'toggle_infinite_repeat', lambda: print("toggle_infinite_repeat not found"))
        self.infinite_checkbox = ttk.Checkbutton(infinite_frame, text="Infinite Repeat", 
                                                variable=self.infinite_repeat,
                                                command=toggle_infinite_cmd)
        self.infinite_checkbox.pack(side=tk.LEFT, padx=3)

        print("DEBUG: Exiting gui_gesture_list._create_gesture_list_widgets") # 함수 끝 확인

    # on_gesture_double_click 메서드는 GuiPlaybackMixin 또는 다른 곳으로 이동될 수 있음
    # def on_gesture_double_click(self, event=None):
    #     """제스처 리스트박스 더블클릭 이벤트 핸들러 (플레이백 연결)"""
    #     play_cmd = getattr(self, 'play_gesture_macro', lambda: print("play_gesture_macro not implemented"))
    #     print("Gesture double-clicked. Attempting to play...")
    #     play_cmd()
