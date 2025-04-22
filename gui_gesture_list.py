# gui_gesture_list.py
import tkinter as tk
from tkinter import ttk

class GuiGestureListMixin:
    """GUI의 제스처 목록(왼쪽 프레임) UI 요소 생성을 담당하는 믹스인 클래스"""

    def _create_gesture_list_widgets(self, parent_frame):
        """왼쪽 프레임에 제스처 목록 관련 위젯들 생성"""
        print("DEBUG: Entering gui_gesture_list._create_gesture_list_widgets") # 함수 시작 확인

        # 제스처 목록 프레임 (self.left_frame 대신 parent_frame 사용)
        gesture_frame = ttk.LabelFrame(parent_frame, text="Gesture List", padding=10)
        gesture_frame.pack(fill=tk.BOTH, expand=True)

        # 제스처 리스트박스 및 스크롤바
        gesture_scrollbar = ttk.Scrollbar(gesture_frame)
        gesture_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.gesture_listbox = tk.Listbox(gesture_frame, font=('Consolas', 11), height=15,
                                         selectmode=tk.SINGLE, # 단일 선택 모드로 변경 (원본 EXTENDED는 다중 선택 로직 필요)
                                         exportselection=False)
        self.gesture_listbox.pack(fill=tk.BOTH, expand=True)
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

        # 제스처 목록 아래 버튼 프레임
        # print("DEBUG: Creating gesture_btn_frame...") # 디버깅 제거
        gesture_btn_frame = ttk.Frame(gesture_frame)
        gesture_btn_frame.pack(fill=tk.X, pady=(10, 0))
        # print("DEBUG: gesture_btn_frame created and packed.") # 디버깅 제거

        # 버튼 콜백 가져오기
        # print("DEBUG: Getting button callbacks...") # 디버깅 제거
        edit_cmd = getattr(self, 'edit_gesture', lambda: print("edit_gesture not found"))
        delete_cmd = getattr(self, 'delete_selected_gesture', lambda: print("delete_selected_gesture not found"))
        move_up_cmd = getattr(self, 'move_gesture_up', lambda: print("move_gesture_up not found"))
        move_down_cmd = getattr(self, 'move_gesture_down', lambda: print("move_gesture_down not found"))
        # print("DEBUG: Button callbacks retrieved.") # 디버깅 제거

        # 버튼 스타일 설정 변수
        btn_width_pixel = 90 # Edit/Delete 버튼 프레임 너비 (85 -> 90으로 수정)
        btn_width_arrow = 3  # 화살표 버튼 너비 (문자 단위)
        btn_padx_outer = 2   # 프레임 간 간격

        # --- Edit 버튼 --- 
        # print("DEBUG: Creating edit_frame...") # 디버깅 제거
        edit_frame = tk.Frame(gesture_btn_frame, width=btn_width_pixel, height=32) # 고정 크기 프레임 (height 30 -> 32)
        # print("DEBUG: edit_frame created.") # 디버깅 제거
        # print("DEBUG: Configuring edit_frame pack_propagate...") # 디버깅 제거
        edit_frame.pack_propagate(False) # 프레임 크기 고정
        # print("DEBUG: Packing edit_frame...") # 디버깅 제거
        edit_frame.pack(side=tk.LEFT, padx=btn_padx_outer)
        # print("DEBUG: edit_frame packed.") # 디버깅 제거

        # print("DEBUG: Creating edit_button...") # 디버깅 제거
        edit_button = tk.Button(edit_frame, text="Edit",
                 font=('Arial', 9),
                 bg='#e8e8e8',
                 relief=tk.RAISED,
                 borderwidth=2,
                 highlightthickness=0,
                 # width, padx 제거 -> 프레임에 채우기
                 command=edit_cmd)
        # print("DEBUG: edit_button created.") # 디버깅 제거
        # print("DEBUG: Packing edit_button...") # 디버깅 제거
        edit_button.pack(fill=tk.BOTH, expand=True) # 프레임 채우기
        # print("DEBUG: edit_button packed.") # 디버깅 제거

        # --- Delete 버튼 --- 
        # print("DEBUG: Creating delete_frame...") # 디버깅 제거
        delete_frame = tk.Frame(gesture_btn_frame, width=btn_width_pixel, height=32) # 고정 크기 프레임 (height 30 -> 32)
        # print("DEBUG: delete_frame created.") # 디버깅 제거
        # print("DEBUG: Configuring delete_frame pack_propagate...") # 디버깅 제거
        delete_frame.pack_propagate(False) # 프레임 크기 고정
        # print("DEBUG: Packing delete_frame...") # 디버깅 제거
        delete_frame.pack(side=tk.LEFT, padx=btn_padx_outer)
        # print("DEBUG: delete_frame packed.") # 디버깅 제거

        # print("DEBUG: Creating delete_button...") # 디버깅 제거
        delete_button = tk.Button(delete_frame, text="Delete",
                 font=('Arial', 9),
                 bg='#e8e8e8',
                 relief=tk.RAISED,
                 borderwidth=2,
                 highlightthickness=0,
                 # width, padx 제거 -> 프레임에 채우기
                 command=delete_cmd)
        # print("DEBUG: delete_button created.") # 디버깅 제거
        # print("DEBUG: Packing delete_button...") # 디버깅 제거
        delete_button.pack(fill=tk.BOTH, expand=True) # 프레임 채우기
        # print("DEBUG: delete_button packed.") # 디버깅 제거

        # --- 디버깅 코드 (위치 이동) --- 
        # print("DEBUG: Updating idletasks for size check...") # 디버깅 제거
        # gesture_btn_frame.update_idletasks() # 지오메트리 업데이트
        # print("--- Gesture Button Debug (Before Arrows) --- ") # 디버깅 제거
        # print(f"Edit Frame Requested Size: ({btn_width_pixel}px, 25px)") # 디버깅 제거
        # print(f"Edit Frame Actual Size: ({edit_frame.winfo_width()}px, {edit_frame.winfo_height()}px)") # 디버깅 제거
        # print(f"Edit Button Actual Size: ({edit_button.winfo_width()}px, {edit_button.winfo_height()}px)") # 디버깅 제거
        # print(f"Delete Frame Requested Size: ({btn_width_pixel}px, 25px)") # 디버깅 제거
        # print(f"Delete Frame Actual Size: ({delete_frame.winfo_width()}px, {delete_frame.winfo_height()}px)") # 디버깅 제거
        # print(f"Delete Button Actual Size: ({delete_button.winfo_width()}px, {delete_button.winfo_height()}px)") # 디버깅 제거
        # print("---------------------------------------------") # 디버깅 제거
        # --- 디버깅 코드 끝 ---

        # 이벤트 이동 버튼 (오른쪽 정렬)
        # print("DEBUG: Creating down arrow button...") # 디버깅 제거
        tk.Button(gesture_btn_frame, text="↓",
                 font=('Arial', 9),
                 bg='#e8e8e8',
                 relief=tk.RAISED,
                 borderwidth=2,
                 highlightthickness=0,
                 width=btn_width_arrow, # 화살표 너비 적용
                 command=move_down_cmd).pack(side=tk.RIGHT, padx=btn_padx_outer)
        # print("DEBUG: Down arrow button created and packed.") # 디버깅 제거

        # print("DEBUG: Creating up arrow button...") # 디버깅 제거
        tk.Button(gesture_btn_frame, text="↑",
                 font=('Arial', 9),
                 bg='#e8e8e8',
                 relief=tk.RAISED,
                 borderwidth=2,
                 highlightthickness=0,
                 width=btn_width_arrow, # 화살표 너비 적용
                 command=move_up_cmd).pack(side=tk.RIGHT, padx=btn_padx_outer)
        # print("DEBUG: Up arrow button created and packed.") # 디버깅 제거

        # --- 반복 실행 제어 위젯 추가 (복원) --- 
        repeat_frame = ttk.Frame(gesture_frame)
        repeat_frame.pack(fill=tk.X, pady=(5, 0))

        ttk.Label(repeat_frame, text="Repeat Count:").pack(side=tk.LEFT, padx=5)

        # GuiBase에서 정의된 변수 사용 (없으면 생성)
        if not hasattr(self, 'repeat_count'): self.repeat_count = tk.StringVar(value="1")
        self.repeat_count_entry = ttk.Entry(repeat_frame, textvariable=self.repeat_count, width=5)
        self.repeat_count_entry.pack(side=tk.LEFT, padx=5)

        infinite_frame = ttk.Frame(gesture_frame)
        infinite_frame.pack(fill=tk.X, pady=(5, 0))

        # GuiBase에서 정의된 변수 사용 (없으면 생성)
        if not hasattr(self, 'infinite_repeat'): self.infinite_repeat = tk.BooleanVar(value=False)
        # toggle_infinite_repeat 콜백 가져오기 (GuiPlaybackMixin 등에 있어야 함)
        toggle_infinite_cmd = getattr(self, 'toggle_infinite_repeat', lambda: print("toggle_infinite_repeat not found"))
        self.infinite_checkbox = ttk.Checkbutton(infinite_frame, text="Infinite Repeat", 
                                                variable=self.infinite_repeat,
                                                command=toggle_infinite_cmd)
        self.infinite_checkbox.pack(side=tk.LEFT, padx=5)
        # --- 반복 실행 제어 위젯 끝 --- 

        print("DEBUG: Exiting gui_gesture_list._create_gesture_list_widgets") # 함수 끝 확인

    # on_gesture_double_click 메서드는 GuiPlaybackMixin 또는 다른 곳으로 이동될 수 있음
    # def on_gesture_double_click(self, event=None):
    #     """제스처 리스트박스 더블클릭 이벤트 핸들러 (플레이백 연결)"""
    #     play_cmd = getattr(self, 'play_gesture_macro', lambda: print("play_gesture_macro not implemented"))
    #     print("Gesture double-clicked. Attempting to play...")
    #     play_cmd()
