import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import time
import mouse
import keyboard

class MacroGUI:
    def __init__(self, root, recorder, player, editor, storage):
        self.root = root
        self.recorder = recorder
        self.player = player
        self.editor = editor
        self.storage = storage
        
        # 윈도우 설정
        self.root.title("고급 매크로 프로그램")
        
        # 창 크기 설정 (width x height)
        window_width = 1200
        window_height = 800
        
        # 화면 크기 가져오기
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # 창 크기가 화면보다 크면 화면 크기의 80%로 조정
        if window_width > screen_width:
            window_width = int(screen_width * 0.8)
        if window_height > screen_height:
            window_height = int(screen_height * 0.8)
        
        # 창을 화면 중앙에 배치하기 위한 x, y 좌표 계산
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        # 창 크기와 위치 설정
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # 최소 창 크기 설정 (width, height)
        self.root.minsize(1000, 700)
        
        # 창 크기 조절 가능 설정
        self.root.resizable(True, True)
        
        # 포커스 및 상태 설정 (normal, iconic, withdrawn, zoomed)
        self.root.state('normal')  # 정상 상태로 시작
        self.root.lift()  # 다른 창 위에 표시
        self.root.focus_force()  # 강제로 포커스 지정
        
        # 매크로 목록
        self.macro_list = []
        
        # GUI 구성요소
        self.notebook = None
        self.macro_listbox = None
        self.event_listbox = None
        self.status_label = None
        
        # 실시간 업데이트 관련
        self.update_timer = None
        self.update_interval = 100  # 0.1초마다 업데이트 (더 빠른 업데이트)
        
        # 녹화 설정
        self.record_mouse_move = tk.BooleanVar(value=False)
        self.use_relative_coords = tk.BooleanVar(value=False)
        self.record_keyboard = tk.BooleanVar(value=True)
        
        # 좌표 설정 변수
        self.coord_var = tk.StringVar(value="absolute")
        
        # 단축키 설정
        self.setup_keyboard_shortcuts()
    
    def setup_ui(self):
        """GUI 구성"""
        self.create_menu()
        self.create_notebook()
        self.create_status_bar()
        
        # 매크로 목록 업데이트
        self.update_macro_list()
        
        # UI 설정 후 창 업데이트 (레이아웃 적용)
        self.root.update_idletasks()
    
    def create_menu(self):
        """메뉴바 생성"""
        menubar = tk.Menu(self.root)
        
        # 파일 메뉴
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="새 매크로 녹화 (Ctrl+R)", command=self.start_recording)
        file_menu.add_command(label="매크로 저장 (Ctrl+S)", command=self.save_macro)
        file_menu.add_command(label="매크로 불러오기", command=self.load_macro)
        file_menu.add_separator()
        file_menu.add_command(label="종료", command=self.root.quit)
        menubar.add_cascade(label="파일", menu=file_menu)
        
        # 편집 메뉴
        edit_menu = tk.Menu(menubar, tearoff=0)
        edit_menu.add_command(label="전체 선택 (Ctrl+A)", command=self.select_all_events)
        edit_menu.add_command(label="선택 삭제", command=self.delete_selected_event)
        edit_menu.add_command(label="딜레이 추가", command=self.add_delay_to_event)
        edit_menu.add_separator()
        edit_menu.add_command(label="선택 영역 복제", command=self.duplicate_selected_events)
        menubar.add_cascade(label="편집", menu=edit_menu)
        
        # 실행 메뉴
        play_menu = tk.Menu(menubar, tearoff=0)
        play_menu.add_command(label="매크로 실행 (F5)", command=self.play_macro)
        play_menu.add_command(label="매크로 중지 (F6)", command=self.stop_macro)
        play_menu.add_separator()
        play_menu.add_command(label="단축키 설정", command=self.configure_hotkeys)
        menubar.add_cascade(label="실행", menu=play_menu)
        
        # 설정 메뉴
        settings_menu = tk.Menu(menubar, tearoff=0)
        settings_menu.add_checkbutton(label="마우스 이동 녹화", variable=self.record_mouse_move, 
                                     command=self.update_record_settings)
        settings_menu.add_checkbutton(label="상대 좌표 사용", variable=self.use_relative_coords,
                                     command=self.update_record_settings)
        settings_menu.add_checkbutton(label="키보드 녹화", variable=self.record_keyboard,
                                     command=self.update_record_settings)
        menubar.add_cascade(label="설정", menu=settings_menu)
        
        # 도움말 메뉴
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="사용 방법", command=self.show_help)
        help_menu.add_command(label="정보", command=self.show_about)
        menubar.add_cascade(label="도움말", menu=help_menu)
        
        self.root.config(menu=menubar)
    
    def create_notebook(self):
        """노트북(탭) 인터페이스 생성"""
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 통합 매크로 탭
        integrated_frame = ttk.Frame(self.notebook)
        self.notebook.add(integrated_frame, text="매크로 관리")
        
        # 좌우 분할 프레임
        paned_window = ttk.PanedWindow(integrated_frame, orient=tk.HORIZONTAL)
        paned_window.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 왼쪽 매크로 목록 및 녹화 제어 프레임
        left_frame = ttk.Frame(paned_window)
        paned_window.add(left_frame, weight=1)
        
        # 중앙 이벤트 리스트 프레임
        center_event_frame = ttk.Frame(paned_window)
        paned_window.add(center_event_frame, weight=2)
        
        # 오른쪽 편집 도구 프레임
        right_edit_frame = ttk.Frame(paned_window)
        paned_window.add(right_edit_frame, weight=1)
        
        # 왼쪽 프레임 구성 - 매크로 목록
        macro_list_frame = ttk.LabelFrame(left_frame, text="매크로 목록")
        macro_list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 매크로 목록 레이블
        list_label = ttk.Label(macro_list_frame, text="저장된 매크로:")
        list_label.pack(anchor=tk.W, padx=5, pady=5)
        
        # 매크로 목록 리스트박스
        list_scrollbar = ttk.Scrollbar(macro_list_frame)
        list_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.macro_listbox = tk.Listbox(macro_list_frame, font=('Consolas', 10))
        self.macro_listbox.pack(fill=tk.BOTH, expand=True)
        self.macro_listbox.config(yscrollcommand=list_scrollbar.set)
        list_scrollbar.config(command=self.macro_listbox.yview)
        
        # 리스트박스 스타일 설정
        self.macro_listbox.config(selectbackground='#4a6cd4', selectforeground='white', font=('Consolas', 11))
        
        # 반복 횟수 설정 프레임
        repeat_frame = ttk.Frame(macro_list_frame)
        repeat_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(repeat_frame, text="반복 횟수:").pack(side=tk.LEFT, padx=5)
        
        # 반복 횟수 변수 및 기본값
        self.repeat_count = tk.StringVar(value="1")
        self.repeat_count_entry = ttk.Entry(repeat_frame, textvariable=self.repeat_count, width=5)
        self.repeat_count_entry.pack(side=tk.LEFT, padx=5)
        
        # 무한 반복 체크박스
        self.infinite_repeat = tk.BooleanVar(value=False)
        infinite_check = ttk.Checkbutton(repeat_frame, text="무한 반복",
                                        variable=self.infinite_repeat,
                                        command=self.toggle_repeat_entry)
        infinite_check.pack(side=tk.LEFT, padx=5)
        
        # 매크로 동작 버튼 프레임
        macro_btn_frame = ttk.Frame(macro_list_frame)
        macro_btn_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # 매크로 동작 버튼들 (단축키 표시 추가)
        ttk.Button(macro_btn_frame, text="실행 (F5)", 
                  command=self.play_macro).pack(side=tk.LEFT, padx=5)
        ttk.Button(macro_btn_frame, text="중지 (F6)", 
                  command=self.stop_macro).pack(side=tk.LEFT, padx=5)
        ttk.Button(macro_btn_frame, text="편집", 
                  command=self.edit_macro).pack(side=tk.LEFT, padx=5)
        ttk.Button(macro_btn_frame, text="삭제", 
                  command=self.delete_macro).pack(side=tk.LEFT, padx=5)
        ttk.Button(macro_btn_frame, text="새로고침", 
                  command=self.update_macro_list).pack(side=tk.RIGHT, padx=5)
        
        # 왼쪽 프레임 - 녹화 설정 
        record_setting_frame = ttk.LabelFrame(left_frame, text="녹화 설정")
        record_setting_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # 녹화 설정 체크박스
        ttk.Checkbutton(record_setting_frame, text="마우스 이동 녹화", 
                      variable=self.record_mouse_move, 
                      command=self.update_record_settings).pack(anchor=tk.W, padx=5, pady=2)
        
        # 좌표 설정 - 라디오 버튼으로 변경
        coord_frame = ttk.Frame(record_setting_frame)
        coord_frame.pack(fill=tk.X, padx=5, pady=2)
        
        ttk.Label(coord_frame, text="좌표 설정:").pack(side=tk.LEFT, padx=5)
        
        ttk.Radiobutton(coord_frame, text="절대 좌표", variable=self.coord_var, 
                      value="absolute", command=self.update_coord_settings).pack(side=tk.LEFT, padx=5)
        
        ttk.Radiobutton(coord_frame, text="상대 좌표", variable=self.coord_var, 
                      value="relative", command=self.update_coord_settings).pack(side=tk.LEFT, padx=5)
        
        ttk.Checkbutton(record_setting_frame, text="키보드 녹화", 
                      variable=self.record_keyboard, 
                      command=self.update_record_settings).pack(anchor=tk.W, padx=5, pady=2)
        
        # 녹화 버튼 프레임
        record_btn_frame = ttk.LabelFrame(left_frame, text="녹화 제어")
        record_btn_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # 녹화 시작/중지 버튼
        self.record_btn = ttk.Button(record_btn_frame, text="녹화 시작 (Ctrl+R)", command=self.start_recording)
        self.record_btn.pack(fill=tk.X, padx=5, pady=5)
        
        # 녹화 이어서 시작 버튼 추가
        self.continue_btn = ttk.Button(record_btn_frame, text="녹화 이어서 시작 (Ctrl+E)", command=self.continue_recording)
        self.continue_btn.pack(fill=tk.X, padx=5, pady=5)
        
        self.stop_btn = ttk.Button(record_btn_frame, text="녹화 중지 (Ctrl+R)", command=self.stop_recording, state=tk.DISABLED)
        self.stop_btn.pack(fill=tk.X, padx=5, pady=5)
        
        # 녹화 저장 버튼
        self.save_btn = ttk.Button(record_btn_frame, text="녹화 저장 (Ctrl+S)", command=self.save_macro, state=tk.DISABLED)
        self.save_btn.pack(fill=tk.X, padx=5, pady=5)
        
        # 녹화 상태 표시
        self.record_status = ttk.Label(record_btn_frame, text="준비됨", foreground="black", anchor=tk.CENTER)
        self.record_status.pack(fill=tk.X, padx=5, pady=5)
        
        # 마우스 현재 위치 표시 프레임
        mouse_pos_frame = ttk.LabelFrame(left_frame, text="마우스 위치")
        mouse_pos_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # 마우스 위치 표시 라벨
        self.mouse_pos_label = ttk.Label(mouse_pos_frame, text="X: 0, Y: 0", anchor=tk.CENTER)
        self.mouse_pos_label.pack(fill=tk.X, padx=5, pady=5)
        
        # 마우스 위치 관련 버튼들
        button_frame = ttk.Frame(mouse_pos_frame)
        button_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # 마우스 위치 업데이트 버튼
        ttk.Button(button_frame, text="현재 위치 가져오기 (F9)", 
                 command=self.update_mouse_position).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5, pady=5)
        
        # 현재 위치 이벤트 추가 버튼
        ttk.Button(button_frame, text="현재 위치 이벤트 추가 (F10)", 
                 command=self.add_current_position).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5, pady=5)
        
        # 중앙 프레임 구성 - 이벤트 목록
        event_frame = ttk.LabelFrame(center_event_frame, text="이벤트 목록")
        event_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 검색 및 필터 프레임
        filter_frame = ttk.Frame(event_frame)
        filter_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # 검색 필드
        ttk.Label(filter_frame, text="검색:").pack(side=tk.LEFT, padx=5)
        self.search_var = tk.StringVar()
        ttk.Entry(filter_frame, textvariable=self.search_var).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # 필터 드롭다운
        ttk.Label(filter_frame, text="필터:").pack(side=tk.LEFT, padx=5)
        self.event_filter = ttk.Combobox(filter_frame, values=["모든 이벤트", "키보드 이벤트", "마우스 이벤트", "딜레이 이벤트"])
        self.event_filter.current(0)
        self.event_filter.pack(side=tk.LEFT, padx=5)
        
        # 검색 및 필터 적용 버튼
        ttk.Button(filter_frame, text="적용", command=self.filter_events).pack(side=tk.LEFT, padx=5)
        
        # 이벤트 수 표시 라벨
        self.event_count_label = ttk.Label(event_frame, text="총 이벤트: 0", anchor=tk.W)
        self.event_count_label.pack(fill=tk.X, padx=5, pady=2)
        
        # 이벤트 리스트박스
        event_scrollbar = ttk.Scrollbar(event_frame)
        event_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.event_listbox = tk.Listbox(event_frame, font=('Consolas', 11), selectmode=tk.EXTENDED, height=20, activestyle='dotbox')
        self.event_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.event_listbox.config(yscrollcommand=event_scrollbar.set)
        event_scrollbar.config(command=self.event_listbox.yview)
        
        # 리스트박스 스타일 설정
        self.event_listbox.config(selectbackground='#4a6cd4', selectforeground='white')
        
        # 이벤트 선택 정보 라벨
        self.selection_info_label = ttk.Label(event_frame, text="", anchor=tk.W)
        self.selection_info_label.pack(fill=tk.X, padx=5, pady=2)
        
        # 오른쪽 프레임 구성 - 편집 도구
        edit_tool_frame = ttk.LabelFrame(right_edit_frame, text="편집 도구")
        edit_tool_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 편집 도구 설명 라벨
        edit_desc_label = ttk.Label(edit_tool_frame, text="선택한 이벤트를 편집합니다", anchor=tk.CENTER, wraplength=150)
        edit_desc_label.pack(fill=tk.X, padx=5, pady=10)
        
        # 편집 버튼들 - 전체 선택 버튼을 맨 위로 이동
        ttk.Button(edit_tool_frame, text="전체 선택 (Ctrl+A)", 
                 command=self.select_all_events).pack(fill=tk.X, padx=5, pady=5)
                 
        ttk.Button(edit_tool_frame, text="선택 영역 삭제", 
                 command=self.delete_selected_event).pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(edit_tool_frame, text="딜레이 추가", 
                 command=self.add_delay_to_event).pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(edit_tool_frame, text="선택 영역 복제", 
                 command=self.duplicate_selected_events).pack(fill=tk.X, padx=5, pady=5)
        
        # 이벤트 선택 변경 시 호출될 함수 바인딩
        self.event_listbox.bind('<<ListboxSelect>>', self.on_event_select)
        
        # 검색창 변경 시 필터 적용
        self.search_var.trace_add("write", lambda name, index, mode: self.filter_events())
        self.event_filter.bind("<<ComboboxSelected>>", self.filter_events)
        
        # 이벤트 목록의 컨텍스트 메뉴
        self.create_event_context_menu()
    
    def create_status_bar(self):
        """상태 표시줄 생성"""
        status_frame = ttk.Frame(self.root)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        self.status_label = ttk.Label(status_frame, text="준비", relief=tk.SUNKEN, anchor=tk.W)
        self.status_label.pack(fill=tk.X)
    
    def update_status(self, message):
        """상태 메시지 업데이트"""
        self.status_label.config(text=message)
    
    def update_macro_list(self):
        """매크로 목록 업데이트"""
        self.macro_listbox.delete(0, tk.END)
        self.macro_list = self.storage.list_macros()
        
        for macro in self.macro_list:
            self.macro_listbox.insert(tk.END, macro)
    
    def update_event_list(self):
        """이벤트 목록 업데이트"""
        # 현재 선택된 항목 기억
        selected_indices = self.event_listbox.curselection()
        
        # 리스트박스 초기화 (녹화 중에는 목록을 보존)
        if not self.recorder.recording:
            self.event_listbox.delete(0, tk.END)
        
        # 녹화 중이면 recorder에서, 아니면 editor에서 이벤트 가져오기
        if self.recorder.recording:
            events = self.recorder.events
            
            # 녹화 중에는 현재 표시된 이벤트 수 확인
            current_displayed = self.event_listbox.size()
            
            # 새로 추가된 이벤트만 업데이트
            for i in range(current_displayed, len(events)):
                event = events[i]
                event_type = event['type']
                
                # 이벤트 유형에 따라 표시 방식 다르게 처리
                if event_type == 'delay':
                    # 딜레이 이벤트는 독립적으로 표시
                    delay_time = event['delay']
                    event_details = f"⏱️ 딜레이: {delay_time:.2f}초"
                    self.event_listbox.insert(tk.END, f"[{i+1}] {event_details}")
                    # 딜레이 이벤트는 배경색 설정
                    self.event_listbox.itemconfig(tk.END, {'bg': '#FFE0E0'})
                    
                elif event_type == 'keyboard':
                    key_event = event['event_type']
                    key_symbol = "⌨️ "
                    # 키보드 이벤트 아이콘 구분
                    if key_event == 'down':
                        key_symbol = "⌨️⬇ "
                    elif key_event == 'up':
                        key_symbol = "⌨️⬆ "
                    
                    event_details = f"{key_symbol}키보드 {event['event_type']} - {event['key']}"
                    self.event_listbox.insert(tk.END, f"[{i+1}] {event_details}")
                    # 키보드 이벤트는 배경색 설정
                    self.event_listbox.itemconfig(tk.END, {'bg': '#E0FFFF'})
                    
                elif event_type == 'mouse':
                    mouse_event_type = event['event_type']
                    mouse_symbol = "🖱️ "
                    
                    # 마우스 이벤트별 아이콘 추가
                    if mouse_event_type == 'move':
                        mouse_symbol = "🖱️➡️ "
                        pos_str = f"위치: {event['position']}"
                        # 상대 좌표인 경우 표시
                        if event.get('is_relative', False):
                            pos_str += " (상대)"
                        event_details = f"{mouse_symbol}마우스 이동 - {pos_str}"
                    elif mouse_event_type == 'down':
                        mouse_symbol = "🖱️⬇ "
                        pos_str = f"위치: {event['position']}"
                        if event.get('is_relative', False):
                            pos_str += " (상대)"
                        event_details = f"{mouse_symbol}마우스 {mouse_event_type} - 버튼: {event['button']} - {pos_str}"
                    elif mouse_event_type == 'up':
                        mouse_symbol = "🖱️⬆ "
                        pos_str = f"위치: {event['position']}"
                        if event.get('is_relative', False):
                            pos_str += " (상대)"
                        event_details = f"{mouse_symbol}마우스 {mouse_event_type} - 버튼: {event['button']} - {pos_str}"
                    elif mouse_event_type == 'double':
                        mouse_symbol = "🖱️🔄 "
                        pos_str = f"위치: {event['position']}"
                        if event.get('is_relative', False):
                            pos_str += " (상대)"
                        event_details = f"{mouse_symbol}마우스 더블클릭 - 버튼: {event['button']} - {pos_str}"
                    elif mouse_event_type == 'scroll':
                        mouse_symbol = "🖱️🔄 "
                        pos_str = f"위치: {event['position']}"
                        if event.get('is_relative', False):
                            pos_str += " (상대)"
                        event_details = f"{mouse_symbol}마우스 스크롤 - 델타: {event['delta']} - {pos_str}"
                    
                    self.event_listbox.insert(tk.END, f"[{i+1}] {event_details}")
                    # 마우스 이벤트는 배경색 설정
                    self.event_listbox.itemconfig(tk.END, {'bg': '#E0FFE0'})
                
                # 새 이벤트가 추가될 때마다 항상 마지막 항목으로 스크롤
                self.event_listbox.see(tk.END)
        else:
            events = self.editor.get_events()
            # 필터링을 위해 모든 이벤트 저장
            self._all_events = events.copy()
            
            if not events:
                # 이벤트 수 업데이트
                self.event_count_label.config(text=f"총 이벤트: 0")
                self.update_selection_info()
                return
            
            # 이벤트 표시
            for i, event in enumerate(events):
                event_type = event['type']
                
                # 이벤트 유형에 따라 표시 방식 다르게 처리
                if event_type == 'delay':
                    # 딜레이 이벤트는 독립적으로 표시
                    delay_time = event['delay']
                    event_details = f"⏱️ 딜레이: {delay_time:.2f}초"
                    self.event_listbox.insert(tk.END, f"[{i+1}] {event_details}")
                    # 딜레이 이벤트 배경색
                    self.event_listbox.itemconfig(tk.END, {'bg': '#FFE0E0'})
                    
                elif event_type == 'keyboard':
                    key_event = event['event_type']
                    key_symbol = "⌨️ "
                    # 키보드 이벤트 아이콘 구분
                    if key_event == 'down':
                        key_symbol = "⌨️⬇ "
                    elif key_event == 'up':
                        key_symbol = "⌨️⬆ "
                    
                    event_details = f"{key_symbol}키보드 {event['event_type']} - {event['key']}"
                    self.event_listbox.insert(tk.END, f"[{i+1}] {event_details}")
                    # 키보드 이벤트는 배경색 설정
                    self.event_listbox.itemconfig(tk.END, {'bg': '#E0FFFF'})
                    
                elif event_type == 'mouse':
                    mouse_event_type = event['event_type']
                    mouse_symbol = "🖱️ "
                    
                    # 마우스 이벤트별 아이콘 추가
                    if mouse_event_type == 'move':
                        mouse_symbol = "🖱️➡️ "
                        pos_str = f"위치: {event['position']}"
                        # 상대 좌표인 경우 표시
                        if event.get('is_relative', False):
                            pos_str += " (상대)"
                        event_details = f"{mouse_symbol}마우스 이동 - {pos_str}"
                    elif mouse_event_type == 'down':
                        mouse_symbol = "🖱️⬇ "
                        pos_str = f"위치: {event['position']}"
                        if event.get('is_relative', False):
                            pos_str += " (상대)"
                        event_details = f"{mouse_symbol}마우스 {mouse_event_type} - 버튼: {event['button']} - {pos_str}"
                    elif mouse_event_type == 'up':
                        mouse_symbol = "🖱️⬆ "
                        pos_str = f"위치: {event['position']}"
                        if event.get('is_relative', False):
                            pos_str += " (상대)"
                        event_details = f"{mouse_symbol}마우스 {mouse_event_type} - 버튼: {event['button']} - {pos_str}"
                    elif mouse_event_type == 'double':
                        mouse_symbol = "🖱️🔄 "
                        pos_str = f"위치: {event['position']}"
                        if event.get('is_relative', False):
                            pos_str += " (상대)"
                        event_details = f"{mouse_symbol}마우스 더블클릭 - 버튼: {event['button']} - {pos_str}"
                    elif mouse_event_type == 'scroll':
                        mouse_symbol = "🖱️🔄 "
                        pos_str = f"위치: {event['position']}"
                        if event.get('is_relative', False):
                            pos_str += " (상대)"
                        event_details = f"{mouse_symbol}마우스 스크롤 - 델타: {event['delta']} - {pos_str}"
                    
                    self.event_listbox.insert(tk.END, f"[{i+1}] {event_details}")
                    # 마우스 이벤트는 배경색 설정
                    self.event_listbox.itemconfig(tk.END, {'bg': '#E0FFE0'})
        
        # 녹화 중이 아닐 때만 선택된 항목 복원
        if not self.recorder.recording:
            for idx in selected_indices:
                if idx < self.event_listbox.size():
                    self.event_listbox.selection_set(idx)
        
        # 이벤트 수 업데이트
        if self.recorder.recording:
            current_count = len(self.recorder.events)
            self.event_count_label.config(text=f"총 이벤트: {current_count} (녹화 중)")
        else:
            self.event_count_label.config(text=f"총 이벤트: {len(events)}")
        
        self.update_selection_info()
        
        # 녹화 중이면 주기적으로 업데이트
        if self.recorder.recording:
            self.update_timer = self.root.after(self.update_interval, self.update_event_list)
    
    # 매크로 녹화 관련 메소드
    def start_recording(self, event=None):
        """매크로 녹화 시작"""
        # 녹화 이미 진행 중이면 중복 실행 방지
        if self.recorder.recording:
            return
        
        # 녹화 시작
        self.recorder.start_recording()
        
        # UI 업데이트
        self.record_btn.config(state=tk.DISABLED)
        self.continue_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.save_btn.config(state=tk.DISABLED)
        self.record_status.config(text="녹화 중...", foreground="red")
        self.update_status("녹화 중...")
        
        # 이벤트 목록 초기화 및 실시간 업데이트 시작
        self.event_listbox.delete(0, tk.END)
        
        # 마우스 위치 실시간 업데이트 시작
        self.update_mouse_position()
        
        # 바로 첫 업데이트 실행
        self.update_event_list()
    
    def stop_recording(self, event=None):
        """매크로 녹화 중지"""
        # 녹화 중이 아니면 실행 방지
        if not self.recorder.recording:
            return
        
        events = self.recorder.stop_recording()
        
        # 타이머 중지
        if self.update_timer:
            self.root.after_cancel(self.update_timer)
            self.update_timer = None
        
        # 마우스 위치 업데이트 타이머 존재 여부 확인 및 중지는 필요 없음
        # (update_mouse_position 함수 내에서 녹화 상태를 확인하기 때문)
        
        # UI 업데이트
        self.record_btn.config(state=tk.NORMAL)
        self.continue_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.record_status.config(text="준비됨", foreground="black")
        
        if events:
            self.editor.current_events = events
            self.editor.modified = True
            self.update_event_list()
            self.update_status(f"녹화 완료 (총 {len(events)}개 이벤트)")
            self.save_btn.config(state=tk.NORMAL)  # 저장 버튼 활성화
        else:
            self.update_status("녹화된 이벤트 없음")
            self.save_btn.config(state=tk.DISABLED)  # 저장 버튼 비활성화
    
    def save_macro(self, event=None):
        """새 매크로로 저장"""
        if self.recorder.recording:
            messagebox.showwarning("경고", "녹화 중에는 저장할 수 없습니다. 녹화를 중지해주세요.")
            return
        
        if not self.editor.get_events():
            messagebox.showwarning("경고", "저장할 이벤트가 없습니다.")
            return
        
        name = simpledialog.askstring("매크로 저장", "매크로 이름을 입력하세요:")
        if name:
            if self.editor.save_edited_macro(name):
                self.update_macro_list()
                self.update_status(f"매크로 '{name}' 저장 완료")
            else:
                messagebox.showerror("오류", "매크로 저장에 실패했습니다.")
    
    # 매크로 불러오기 관련 메소드
    def load_macro(self):
        """선택한 매크로 불러오기"""
        selected = self.macro_listbox.curselection()
        if not selected:
            messagebox.showwarning("경고", "불러올 매크로를 선택하세요.")
            return
        
        macro_name = self.macro_list[selected[0]]
        if self.editor.load_macro_for_editing(macro_name):
            self.update_event_list()
            self.update_status(f"매크로 '{macro_name}' 로드 완료")
            self.notebook.select(1)  # 녹화/편집 탭으로 전환
        else:
            messagebox.showerror("오류", "매크로 불러오기에 실패했습니다.")
    
    def edit_macro(self):
        """선택한 매크로 편집"""
        selected = self.macro_listbox.curselection()
        if not selected:
            messagebox.showwarning("경고", "편집할 매크로를 선택하세요.")
            return
        
        # 선택한 매크로 이름 가져오기
        macro_name = self.macro_list[selected[0]]
        
        # 매크로 편집 모드로 로드
        if self.editor.load_macro_for_editing(macro_name):
            # 이벤트 목록 업데이트
            self.update_event_list()
            self.update_status(f"매크로 '{macro_name}' 편집 모드")
        else:
            messagebox.showerror("오류", f"매크로 '{macro_name}' 로드 실패")
    
    def delete_macro(self):
        """선택한 매크로 삭제"""
        selected = self.macro_listbox.curselection()
        if not selected:
            messagebox.showwarning("경고", "삭제할 매크로를 선택하세요.")
            return
        
        macro_name = self.macro_list[selected[0]]
        if messagebox.askyesno("확인", f"'{macro_name}' 매크로를 삭제하시겠습니까?"):
            if self.storage.delete_macro(macro_name):
                self.update_macro_list()
                self.update_status(f"매크로 '{macro_name}' 삭제 완료")
            else:
                messagebox.showerror("오류", "매크로 삭제에 실패했습니다.")
    
    # 이벤트 편집 관련 메소드
    def delete_selected_event(self):
        """선택한 이벤트 삭제"""
        # 녹화 중에는 편집 불가
        if self.recorder.recording:
            messagebox.showwarning("경고", "녹화 중에는 이벤트를 편집할 수 없습니다.")
            return
            
        selected = self.event_listbox.curselection()
        if not selected:
            messagebox.showwarning("경고", "삭제할 이벤트를 선택하세요.")
            return
        
        # 다중 선택 지원
        selected_indices = list(selected)
        
        # 하나의 이벤트만 선택한 경우 기존 방식 사용
        if len(selected_indices) == 1:
            if self.editor.delete_event(selected_indices[0]):
                self.update_event_list()
                self.update_status("이벤트 삭제 완료")
            else:
                messagebox.showerror("오류", "이벤트 삭제에 실패했습니다.")
        else:
            # 여러 이벤트 삭제
            if self.editor.delete_events(selected_indices):
                self.update_event_list()
                self.update_status(f"{len(selected_indices)}개 이벤트 삭제 완료")
            else:
                messagebox.showerror("오류", "이벤트 삭제에 실패했습니다.")
    
    def add_delay_to_event(self):
        """딜레이 이벤트 추가"""
        # 녹화 중이면 직접 딜레이 이벤트 추가
        if self.recorder.recording:
            delay = simpledialog.askfloat("딜레이 추가", "추가할 딜레이 시간(초):", minvalue=0.1, maxvalue=60)
            if delay is not None:
                if self.recorder.add_delay_event(delay):
                    self.update_status(f"{delay}초 딜레이 추가 완료")
                    # 이벤트 목록 업데이트
                    self.update_event_list()
                else:
                    messagebox.showerror("오류", "딜레이 추가에 실패했습니다.")
            return
        
        # 녹화 중이 아니면 선택된 이벤트 뒤에 딜레이 추가
        selected = self.event_listbox.curselection()
        if not selected:
            messagebox.showwarning("경고", "딜레이를 추가할 이벤트를 선택하세요.")
            return
        
        delay = simpledialog.askfloat("딜레이 추가", "추가할 딜레이 시간(초):", minvalue=0.1, maxvalue=60)
        if delay is not None:
            # 선택된 이벤트 위치에 딜레이 이벤트 추가
            if self.editor.add_delay_event(selected[0], delay):
                self.update_event_list()
                self.update_status(f"{delay}초 딜레이 추가 완료")
            else:
                messagebox.showerror("오류", "딜레이 추가에 실패했습니다.")
    
    def save_edited_macro(self, event=None):
        """편집된 매크로 저장"""
        if not self.editor.is_modified():
            messagebox.showinfo("알림", "변경 사항이 없습니다.")
            return
        
        current_name = self.storage.current_macro_name
        name = None
        
        if current_name:
            if messagebox.askyesno("확인", f"'{current_name}'에 덮어쓰시겠습니까?"):
                name = current_name
            else:
                name = simpledialog.askstring("매크로 저장", "새 매크로 이름을 입력하세요:")
        else:
            name = simpledialog.askstring("매크로 저장", "매크로 이름을 입력하세요:")
        
        if name:
            if self.editor.save_edited_macro(name):
                self.update_macro_list()
                self.update_status(f"매크로 '{name}' 저장 완료")
            else:
                messagebox.showerror("오류", "매크로 저장에 실패했습니다.")
    
    # 매크로 실행 관련 메소드
    def play_macro(self, event=None):
        """선택한 매크로 실행"""
        # 이미 실행 중이면 중복 실행 방지
        if self.player.is_playing():
            messagebox.showinfo("알림", "매크로가 이미 실행 중입니다.")
            return

        # 녹화 중에는 실행 불가
        if self.recorder.recording:
            messagebox.showwarning("경고", "녹화 중에는 매크로를 실행할 수 없습니다.")
            return
        
        # 매크로 목록 탭에서 실행하는 경우
        if self.notebook.index(self.notebook.select()) == 0:
            selected = self.macro_listbox.curselection()
            if not selected:
                messagebox.showwarning("경고", "실행할 매크로를 선택하세요.")
                return
            
            macro_name = self.macro_list[selected[0]]
            events = self.storage.load_macro(macro_name)
        else:
            # 편집 탭에서 실행하는 경우
            events = self.editor.get_events()
            
        if not events:
            messagebox.showwarning("경고", "실행할 매크로가 없습니다.")
            return
        
        # 무한 반복 체크인 경우
        if self.infinite_repeat.get():
            repeat_count = 0  # 0은 무한 반복 의미
        else:
            # 반복 횟수 가져오기
            try:
                repeat_count = int(self.repeat_count.get())
                if repeat_count < 1:
                    messagebox.showwarning("경고", "반복 횟수는 1 이상이어야 합니다.")
                    return
            except ValueError:
                messagebox.showwarning("경고", "올바른 반복 횟수를 입력하세요.")
                return
        
        self.player.play_macro(events, repeat_count)
        
        if repeat_count == 0:
            self.update_status("매크로 무한 반복 실행 중...")
        else:
            self.update_status(f"매크로 {repeat_count}회 실행 중...")
    
    def stop_macro(self, event=None):
        """매크로 실행 중지"""
        if self.player.stop_playing():
            self.update_status("매크로 실행 중지")
        else:
            self.update_status("실행 중인 매크로 없음")

    def select_all_events(self, event=None):
        """모든 이벤트 선택"""
        self.event_listbox.select_clear(0, tk.END)
        self.event_listbox.select_set(0, tk.END)

    def duplicate_selected_events(self):
        """선택한 이벤트 영역 복제"""
        # 녹화 중에는 복제 불가
        if self.recorder.recording:
            messagebox.showwarning("경고", "녹화 중에는 이벤트를 복제할 수 없습니다.")
            return
            
        selected = self.event_listbox.curselection()
        if not selected:
            messagebox.showwarning("경고", "복제할 이벤트를 선택하세요.")
            return
        
        # 선택한 이벤트 복제
        selected_indices = list(selected)
        selected_indices.sort()  # 인덱스 정렬
        
        # editor에서 이벤트 복제
        if self.editor.duplicate_events(selected_indices):
            self.update_event_list()
            self.update_status(f"{len(selected_indices)}개 이벤트 복제 완료")
        else:
            messagebox.showerror("오류", "이벤트 복제에 실패했습니다.")

    def configure_hotkeys(self):
        """단축키 설정"""
        # 단축키 목록 표시
        self.show_hotkeys()

    def show_hotkeys(self):
        """단축키 목록 표시"""
        hotkey_info = """
        단축키 목록:
        
        F5              - 매크로 실행 (매크로 목록에서)
        F6              - 매크로 실행 중지
        F9              - 현재 마우스 위치 가져오기
        F10             - 현재 마우스 위치 이벤트 추가
        Ctrl+R          - 녹화 시작/중지 토글
        Ctrl+E          - 녹화 이어서 시작
        Ctrl+S          - 매크로 저장
        Ctrl+A          - 전체 선택
        """
        
        messagebox.showinfo("단축키 목록", hotkey_info)

    def show_help(self):
        """도움말 표시"""
        # 구현 필요
        pass

    def show_about(self):
        """정보 표시"""
        # 구현 필요
        pass

    def update_record_settings(self):
        """녹화 설정 업데이트"""
        # 설정 변경사항을 recorder에 전달
        self.recorder.record_mouse_move = self.record_mouse_move.get()
        self.recorder.use_relative_coords = self.use_relative_coords.get()
        self.recorder.record_keyboard = self.record_keyboard.get()
        
        # 좌표 설정 동기화
        if self.use_relative_coords.get():
            self.coord_var.set("relative")
        else:
            self.coord_var.set("absolute")
        
        # 상태 메시지 업데이트
        settings = []
        if self.record_mouse_move.get():
            settings.append("마우스 이동")
        if self.record_keyboard.get():
            settings.append("키보드")
        
        coord_type = "상대" if self.use_relative_coords.get() else "절대"
        
        if settings:
            self.update_status(f"녹화 설정 변경: {', '.join(settings)} ({coord_type} 좌표)")
        else:
            self.update_status("경고: 녹화할 이벤트가 선택되지 않았습니다.")

    def update_mouse_position(self):
        """마우스 현재 위치 업데이트"""
        try:
            pos = mouse.get_position()
            self.mouse_pos_label.config(text=f"X: {pos[0]}, Y: {pos[1]}")
            
            # 녹화 중이면 지속적으로 업데이트
            if self.recorder.recording:
                self.root.after(100, self.update_mouse_position)
        except Exception as e:
            self.update_status(f"마우스 위치 가져오기 실패: {e}")

    def filter_events(self, event=None):
        """이벤트 필터링"""
        # 현재 필터 설정 가져오기
        filter_option = self.event_filter.get()
        search_text = self.search_var.get().lower()
        
        # 기존 이벤트 백업이 없으면 생성
        if not hasattr(self, '_all_events'):
            self._all_events = self.editor.get_events()
        
        # 원본 이벤트 목록
        original_events = self._all_events
        if not original_events:
            return
        
        # 리스트박스 초기화
        self.event_listbox.delete(0, tk.END)
        
        # 필터링된 이벤트만 표시
        filtered_count = 0
        displayed_index = 1
        
        for i, event in enumerate(original_events):
            event_type = event['type']
            
            # 이벤트 상세 정보 문자열 생성
            if event_type == 'delay':
                # 딜레이 이벤트는 독립적으로 표시
                delay_time = event['delay']
                event_details = f"⏱️ 딜레이: {delay_time:.2f}초"
            elif event_type == 'keyboard':
                key_event = event['event_type']
                key_symbol = "⌨️ "
                # 키보드 이벤트 아이콘 구분
                if key_event == 'down':
                    key_symbol = "⌨️⬇ "
                elif key_event == 'up':
                    key_symbol = "⌨️⬆ "
                
                event_details = f"{key_symbol}키보드 {event['event_type']} - {event['key']}"
            elif event_type == 'mouse':
                mouse_event_type = event['event_type']
                mouse_symbol = "🖱️ "
                
                # 마우스 이벤트별 아이콘 추가
                if mouse_event_type == 'move':
                    mouse_symbol = "🖱️➡️ "
                    pos_str = f"위치: {event['position']}"
                    # 상대 좌표인 경우 표시
                    if event.get('is_relative', False):
                        pos_str += " (상대)"
                    event_details = f"{mouse_symbol}마우스 이동 - {pos_str}"
                elif mouse_event_type == 'down':
                    mouse_symbol = "🖱️⬇ "
                    pos_str = f"위치: {event['position']}"
                    if event.get('is_relative', False):
                        pos_str += " (상대)"
                    event_details = f"{mouse_symbol}마우스 {mouse_event_type} - 버튼: {event['button']} - {pos_str}"
                elif mouse_event_type == 'up':
                    mouse_symbol = "🖱️⬆ "
                    pos_str = f"위치: {event['position']}"
                    if event.get('is_relative', False):
                        pos_str += " (상대)"
                    event_details = f"{mouse_symbol}마우스 {mouse_event_type} - 버튼: {event['button']} - {pos_str}"
                elif mouse_event_type == 'double':
                    mouse_symbol = "🖱️🔄 "
                    pos_str = f"위치: {event['position']}"
                    if event.get('is_relative', False):
                        pos_str += " (상대)"
                    event_details = f"{mouse_symbol}마우스 더블클릭 - 버튼: {event['button']} - {pos_str}"
                elif mouse_event_type == 'scroll':
                    mouse_symbol = "🖱️🔄 "
                    pos_str = f"위치: {event['position']}"
                    if event.get('is_relative', False):
                        pos_str += " (상대)"
                    event_details = f"{mouse_symbol}마우스 스크롤 - 델타: {event['delta']} - {pos_str}"
            
            # 필터 적용
            include = True
            
            # 이벤트 타입 필터링
            if filter_option == "키보드 이벤트" and event_type != 'keyboard':
                include = False
            elif filter_option == "마우스 이벤트" and event_type != 'mouse':
                include = False
            elif filter_option == "이동 이벤트" and (event_type != 'mouse' or event.get('event_type') != 'move'):
                include = False
            elif filter_option == "딜레이 이벤트" and event_type != 'delay':
                include = False
            
            # 검색어 필터링
            if search_text and search_text not in event_details.lower():
                include = False
            
            # 필터 통과한 이벤트만 표시
            if include:
                self.event_listbox.insert(tk.END, f"[{displayed_index}] {event_details}")
                
                # 이벤트 타입별 배경색 설정
                if event_type == 'delay':
                    self.event_listbox.itemconfig(tk.END, {'bg': '#FFE0E0'})
                elif event_type == 'keyboard':
                    self.event_listbox.itemconfig(tk.END, {'bg': '#E0FFFF'})
                elif event_type == 'mouse':
                    self.event_listbox.itemconfig(tk.END, {'bg': '#E0FFE0'})
                
                filtered_count += 1
                displayed_index += 1
        
        # 이벤트 수 업데이트
        self.event_count_label.config(text=f"총 이벤트: {len(original_events)} (표시: {filtered_count})")
        self.update_selection_info()

    def update_selection_info(self, event=None):
        """선택된 이벤트 정보 업데이트"""
        selected = self.event_listbox.curselection()
        self.selection_info_label.config(text=f"선택됨: {len(selected)}")

    def create_event_context_menu(self):
        """이벤트 목록의 컨텍스트 메뉴 생성"""
        self.event_context_menu = tk.Menu(self.event_listbox, tearoff=0)
        self.event_context_menu.add_command(label="이벤트 삭제", command=self.delete_selected_event)
        self.event_context_menu.add_command(label="딜레이 추가", command=self.add_delay_to_event)
        self.event_context_menu.add_command(label="이벤트 복제", command=self.duplicate_selected_events)
        self.event_context_menu.add_separator()
        self.event_context_menu.add_command(label="전체 선택", command=self.select_all_events)

        # 우클릭 이벤트에 메뉴 표시 연결
        self.event_listbox.bind("<Button-3>", self.show_event_context_menu)

    def show_event_context_menu(self, event):
        """우클릭 시 컨텍스트 메뉴 표시"""
        if self.event_listbox.size() > 0:
            self.event_context_menu.post(event.x_root, event.y_root)

    def on_event_select(self, event=None):
        """이벤트 선택 시 처리"""
        self.update_selection_info()

    def update_coord_settings(self):
        """좌표 설정 업데이트"""
        coord_mode = self.coord_var.get()
        
        # 상대/절대 좌표 설정
        self.use_relative_coords.set(coord_mode == "relative")
        
        # 설정 변경사항을 recorder에 전달
        self.recorder.use_relative_coords = self.use_relative_coords.get()
        
        # 상태 메시지 업데이트
        coord_type = "상대" if self.use_relative_coords.get() else "절대"
        self.update_status(f"좌표 모드 변경: {coord_type} 좌표")

    def toggle_repeat_entry(self):
        """무한 반복 선택 시 반복 횟수 입력 비활성화"""
        if self.infinite_repeat.get():
            self.repeat_count_entry.config(state=tk.DISABLED)
            self.repeat_count.set("∞")
        else:
            self.repeat_count_entry.config(state=tk.NORMAL)
            self.repeat_count.set("1")

    def setup_keyboard_shortcuts(self):
        """키보드 단축키 설정"""
        # F5 키: 매크로 실행
        self.root.bind("<F5>", lambda event: self.play_macro())
        
        # F6 키: 매크로 실행 중지
        self.root.bind("<F6>", lambda event: self.stop_macro())
        
        # Ctrl+R: 녹화 시작/중지 토글
        self.root.bind("<Control-r>", self.toggle_recording)
        
        # Ctrl+E: 녹화 이어서 시작
        self.root.bind("<Control-e>", lambda event: self.continue_recording())
        
        # Ctrl+S: 매크로 저장
        self.root.bind("<Control-s>", lambda event: self.save_macro())
        
        # Ctrl+A: 전체 선택
        self.root.bind("<Control-a>", lambda event: self.select_all_events())
        
        # F9: 현재 마우스 위치 가져오기
        self.root.bind("<F9>", lambda event: self.update_mouse_position())
        
        # F10: 현재 마우스 위치 이벤트 추가
        self.root.bind("<F10>", lambda event: self.add_current_position())

    def toggle_recording(self, event=None):
        """녹화 시작/중지 토글"""
        # 현재 녹화 중이면 중지, 아니면 시작
        if self.recorder.recording:
            self.stop_recording()
        else:
            self.start_recording()

    def continue_recording(self, event=None):
        """녹화 이어서 시작 - 기존 이벤트를 유지하고 녹화 시작"""
        # 이미 녹화 중이면 중복 실행 방지
        if self.recorder.recording:
            return
        
        # 에디터에 이벤트가 없으면 그냥 새로 녹화 시작
        if not self.editor.get_events():
            self.start_recording()
            return
        
        # 현재 이벤트를 레코더에 설정
        self.recorder.events = self.editor.get_events().copy()
        
        # 마지막 이벤트의 시간 찾기
        if self.recorder.events:
            last_time = max([event.get('time', 0) for event in self.recorder.events])
            # 시작 시간 조정 (마치 녹화를 중지했다가 다시 시작한 것처럼)
            self.recorder.start_time = time.time() - last_time
        
        # 녹화 시작
        self.recorder.recording = True
        
        # 키보드 이벤트 후크
        if self.recorder.record_keyboard:
            keyboard.hook(self.recorder._keyboard_callback)
        
        # 마우스 이벤트 후크
        mouse.hook(self.recorder._mouse_callback)
        
        # UI 업데이트
        self.record_btn.config(state=tk.DISABLED)
        self.continue_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.save_btn.config(state=tk.DISABLED)
        self.record_status.config(text="녹화 중...", foreground="red")
        self.update_status("녹화 이어서 진행 중...")
        
        # 바로 첫 업데이트 실행
        self.update_event_list()
        
        # 마우스 위치 실시간 업데이트 시작
        self.update_mouse_position()

    def add_current_position(self, event=None):
        """현재 마우스 위치를 이벤트로 추가"""
        # 마우스 현재 위치 가져오기
        pos = mouse.get_position()
        
        # 녹화 중이면 이벤트 직접 추가
        if self.recorder.recording:
            current_time = time.time() - self.recorder.start_time
            
            event_data = {
                'type': 'mouse',
                'event_type': 'move',
                'time': current_time,
                'position': pos,
                'is_relative': False
            }
            
            # 상대좌표 설정이면 변환
            if self.recorder.use_relative_coords:
                rel_x = pos[0] - self.recorder.base_x
                rel_y = pos[1] - self.recorder.base_y
                event_data['position'] = (rel_x, rel_y)
                event_data['is_relative'] = True
            
            self.recorder.events.append(event_data)
            self.recorder.last_event_time = current_time
            
            self.update_event_list()
            self.update_status(f"현재 마우스 위치 추가: {pos}")
        
        # 녹화 중이 아니면 편집모드로 추가 (에디터를 통해)
        else:
            if not hasattr(self.editor, 'current_events') or not self.editor.current_events:
                messagebox.showwarning("경고", "편집할 매크로가 없습니다. 먼저 녹화하거나 매크로를 로드하세요.")
                return
            
            # 현재 선택된 인덱스 가져오기 (없으면 마지막에 추가)
            selected = self.event_listbox.curselection()
            index = selected[0] if selected else len(self.editor.current_events)
            
            # 에디터에 새 이벤트 추가
            if index < len(self.editor.current_events):
                event_time = self.editor.current_events[index]['time']
            else:
                # 마지막에 추가하는 경우 가장 마지막 이벤트 시간 + 0.1초
                last_time = 0
                if self.editor.current_events:
                    last_time = max([e.get('time', 0) for e in self.editor.current_events])
                event_time = last_time + 0.1
            
            event_data = {
                'type': 'mouse',
                'event_type': 'move',
                'time': event_time,
                'position': pos,
                'is_relative': False
            }
            
            # 상대좌표 설정이면 변환 (현재 기준점이 없으므로 첫 이벤트 위치 기준)
            if self.use_relative_coords.get():
                # 기준점 찾기 (첫 마우스 이벤트의 위치)
                base_x, base_y = 0, 0
                for e in self.editor.current_events:
                    if e['type'] == 'mouse' and 'position' in e:
                        base_x, base_y = e['position']
                        break
                
                rel_x = pos[0] - base_x
                rel_y = pos[1] - base_y
                event_data['position'] = (rel_x, rel_y)
                event_data['is_relative'] = True
            
            self.editor.current_events.insert(index + 1, event_data)
            self.editor.modified = True
            
            self.update_event_list()
            self.update_status(f"위치 이벤트 추가됨: {pos}")

    def center_window(self):
        """창을 화면 중앙에 배치"""
        # 현재 창 크기 가져오기
        window_width = self.root.winfo_width()
        window_height = self.root.winfo_height()
        
        # 창이 완전히 생성되지 않았다면 지정된 크기 사용
        if window_width <= 1:
            # geometry에서 설정한 크기 파싱
            geometry = self.root.geometry()
            try:
                # "1200x800+x+y" 형식에서 너비와 높이 추출
                size_part = geometry.split('+')[0]
                width_height = size_part.split('x')
                window_width = int(width_height[0])
                window_height = int(width_height[1])
            except (IndexError, ValueError):
                # 파싱 실패 시 기본값 사용
                window_width = 1200
                window_height = 800
        
        # 화면 크기 가져오기
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # 창을 화면 중앙에 배치하기 위한 x, y 좌표 계산
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        # 창 위치 설정 (좌표는 양수여야 함)
        x = max(0, x)
        y = max(0, y)
        
        # 창 위치 적용
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # 창이 화면에 맞게 표시되도록 업데이트 호출
        self.root.update_idletasks() 