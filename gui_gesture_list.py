# gui_gesture_list.py
import tkinter as tk
from tkinter import ttk

class GuiGestureListMixin:
    """GUI의 제스처 목록(왼쪽 프레임) UI 요소 생성을 담당하는 믹스인 클래스"""

    def _create_gesture_list_widgets(self):
        """왼쪽 프레임에 제스처 목록 관련 위젯들 생성"""
        # 제스처 목록 프레임 (left_frame은 GuiSetupMixin에서 생성됨)
        gesture_frame = ttk.LabelFrame(self.left_frame, text="Gesture List", padding=10)
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
        self.gesture_listbox.bind('<Double-Button-1>', double_click_cmd)

        # 제스처 목록 아래 버튼 프레임
        gesture_btn_frame = ttk.Frame(gesture_frame)
        gesture_btn_frame.pack(fill=tk.X, pady=(10, 0))

        # 버튼 커맨드 가져오기 (다른 믹스인에서 정의됨)
        edit_cmd = getattr(self, 'edit_gesture', lambda: print("edit_gesture not implemented"))
        delete_cmd = getattr(self, 'delete_selected_gesture', lambda: print("delete_selected_gesture not implemented"))
        move_up_cmd = getattr(self, 'move_gesture_up', lambda: print("move_gesture_up not implemented"))
        move_down_cmd = getattr(self, 'move_gesture_down', lambda: print("move_gesture_down not implemented"))

        # 수정 버튼
        self.edit_gesture_btn = ttk.Button(gesture_btn_frame, text="Edit", width=10, command=edit_cmd)
        self.edit_gesture_btn.pack(side=tk.LEFT, padx=5)

        # 삭제 버튼
        self.delete_gesture_btn = ttk.Button(gesture_btn_frame, text="Delete", width=10, command=delete_cmd)
        self.delete_gesture_btn.pack(side=tk.LEFT, padx=5)

        # 제스처 위/아래 이동 버튼 프레임
        gesture_move_frame = ttk.Frame(gesture_frame)
        gesture_move_frame.pack(fill=tk.X, pady=(5,0))

        self.move_gesture_up_btn = ttk.Button(gesture_move_frame, text="Move Up", width=10, command=move_up_cmd)
        self.move_gesture_up_btn.pack(side=tk.LEFT, padx=5)

        self.move_gesture_down_btn = ttk.Button(gesture_move_frame, text="Move Down", width=10, command=move_down_cmd)
        self.move_gesture_down_btn.pack(side=tk.LEFT, padx=5)


    # on_gesture_double_click 메서드는 GuiPlaybackMixin 또는 다른 곳으로 이동될 수 있음
    # def on_gesture_double_click(self, event=None):
    #     """제스처 리스트박스 더블클릭 이벤트 핸들러 (플레이백 연결)"""
    #     play_cmd = getattr(self, 'play_gesture_macro', lambda: print("play_gesture_macro not implemented"))
    #     print("Gesture double-clicked. Attempting to play...")
    #     play_cmd()
