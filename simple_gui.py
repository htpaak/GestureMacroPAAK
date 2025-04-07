import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import time
import mouse
import keyboard

class SimpleGUI:
    def __init__(self, root, recorder, player, editor, storage):
        self.root = root
        self.recorder = recorder
        self.player = player
        self.editor = editor
        self.storage = storage
        
        # 윈도우 설정
        self.root.title("간단한 매크로 프로그램")
        
        # 창 크기 설정 (width x height)
        window_width = 800
        window_height = 600
        
        # 화면 크기 가져오기
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # 창을 화면 중앙에 배치하기 위한 x, y 좌표 계산
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        # 창 크기와 위치 설정
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # 최소 창 크기 설정
        self.root.minsize(800, 600)
        
        # 포커스 설정
        self.root.lift()
        self.root.focus_force()
        
        # 매크로 목록
        self.macro_list = []
        
        # GUI 구성요소
        self.macro_listbox = None
        self.event_listbox = None
        self.status_label = None
        
        # 실시간 업데이트 관련
        self.update_timer = None
        self.update_interval = 100  # 0.1초마다 업데이트
        
        # 녹화 설정
        self.record_mouse_move = tk.BooleanVar(value=False)
        self.use_relative_coords = tk.BooleanVar(value=False)
        self.record_keyboard = tk.BooleanVar(value=True)
        
        # 무한 반복 설정
        self.infinite_repeat = tk.BooleanVar(value=False)
        
        # 이벤트 선택 관련
        self.selected_events = []
        self.restore_selection = True  # 선택 복원 여부 제어 플래그
        
        # 단축키 설정
        self.setup_keyboard_shortcuts()
        
    def setup_ui(self):
        """간소화된 GUI 구성"""
        # 메인 프레임
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 상단 제어 프레임
        control_frame = ttk.LabelFrame(main_frame, text="매크로 제어", padding=10)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 제어 버튼 프레임
        button_frame = ttk.Frame(control_frame)
        button_frame.pack(fill=tk.X)
        
        # 녹화 버튼
        self.record_btn = ttk.Button(button_frame, text="녹화 시작 (Ctrl+R)", 
                                    command=self.start_recording)
        self.record_btn.pack(side=tk.LEFT, padx=5)
        
        # 녹화 중지 버튼
        self.stop_btn = ttk.Button(button_frame, text="녹화 중지 (Ctrl+R)", 
                                  command=self.stop_recording, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        
        # 저장 버튼
        self.save_btn = ttk.Button(button_frame, text="저장 (Ctrl+S)", 
                                  command=self.save_macro)
        self.save_btn.pack(side=tk.LEFT, padx=5)
        
        # 실행 및 중지 버튼
        ttk.Button(button_frame, text="실행 (F5)", 
                 command=self.play_macro).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="중지 (F6)", 
                 command=self.stop_macro).pack(side=tk.LEFT, padx=5)
        
        # 녹화 상태 표시
        self.record_status = ttk.Label(control_frame, text="준비", foreground="black")
        self.record_status.pack(anchor=tk.W, pady=(5, 0))
        
        # 메인 컨텐츠 영역 - 좌우 분할
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # 왼쪽 프레임 - 매크로 목록
        left_frame = ttk.LabelFrame(content_frame, text="매크로 목록", padding=10)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # 매크로 리스트박스 및 스크롤바
        list_scrollbar = ttk.Scrollbar(left_frame)
        list_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.macro_listbox = tk.Listbox(left_frame, font=('Consolas', 11))
        self.macro_listbox.pack(fill=tk.BOTH, expand=True)
        self.macro_listbox.config(yscrollcommand=list_scrollbar.set, 
                                 selectbackground='#4a6cd4', 
                                 selectforeground='white')
        list_scrollbar.config(command=self.macro_listbox.yview)
        
        # 매크로 목록 아래 버튼 프레임
        macro_btn_frame = ttk.Frame(left_frame)
        macro_btn_frame.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Button(macro_btn_frame, text="삭제", 
                  command=self.delete_macro).pack(side=tk.LEFT, padx=5)
        ttk.Button(macro_btn_frame, text="불러오기", 
                  command=self.load_macro).pack(side=tk.LEFT, padx=5)
        
        # 반복 횟수 설정
        repeat_frame = ttk.Frame(left_frame)
        repeat_frame.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Label(repeat_frame, text="반복 횟수:").pack(side=tk.LEFT, padx=5)
        
        self.repeat_count = tk.StringVar(value="1")
        self.repeat_count_entry = ttk.Entry(repeat_frame, textvariable=self.repeat_count, width=5)
        self.repeat_count_entry.pack(side=tk.LEFT, padx=5)
        
        # 무한 반복 체크박스 추가
        self.infinite_checkbox = ttk.Checkbutton(repeat_frame, text="무한 반복", 
                                                variable=self.infinite_repeat,
                                                command=self.toggle_infinite_repeat)
        self.infinite_checkbox.pack(side=tk.LEFT, padx=5)
        
        # 오른쪽 프레임 - 이벤트 목록
        right_frame = ttk.LabelFrame(content_frame, text="이벤트 목록", padding=10)
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        # 이벤트 리스트박스 및 스크롤바
        event_scrollbar = ttk.Scrollbar(right_frame)
        event_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # SINGLE 대신 EXTENDED 모드 사용 (다중 선택 가능)
        self.event_listbox = tk.Listbox(right_frame, font=('Consolas', 11), selectmode=tk.EXTENDED)
        self.event_listbox.pack(fill=tk.BOTH, expand=True)
        self.event_listbox.config(yscrollcommand=event_scrollbar.set, 
                                 selectbackground='#4a6cd4', 
                                 selectforeground='white')
        event_scrollbar.config(command=self.event_listbox.yview)
        
        # 선택 변경 이벤트 바인딩
        self.event_listbox.bind('<<ListboxSelect>>', self.on_event_select)
        
        # 이벤트 목록 아래 버튼 프레임
        event_btn_frame = ttk.Frame(right_frame)
        event_btn_frame.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Button(event_btn_frame, text="선택 삭제", 
                  command=self.delete_selected_event).pack(side=tk.LEFT, padx=5)
        ttk.Button(event_btn_frame, text="딜레이 추가", 
                  command=self.add_delay_to_event).pack(side=tk.LEFT, padx=5)
        ttk.Button(event_btn_frame, text="딜레이 수정", 
                  command=self.modify_delay_time).pack(side=tk.LEFT, padx=5)
        ttk.Button(event_btn_frame, text="전체 선택", 
                  command=self.select_all_events).pack(side=tk.LEFT, padx=5)
        
        # 이벤트 이동 버튼
        ttk.Button(event_btn_frame, text="↑", width=2,
                  command=self.move_event_up).pack(side=tk.RIGHT, padx=2)
        ttk.Button(event_btn_frame, text="↓", width=2,
                  command=self.move_event_down).pack(side=tk.RIGHT, padx=2)
        
        # 간단한 설정 프레임
        settings_frame = ttk.Frame(right_frame)
        settings_frame.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Checkbutton(settings_frame, text="마우스 이동 녹화", 
                       variable=self.record_mouse_move,
                       command=self.update_record_settings).pack(side=tk.LEFT, padx=5)
        ttk.Checkbutton(settings_frame, text="키보드 녹화", 
                       variable=self.record_keyboard,
                       command=self.update_record_settings).pack(side=tk.LEFT, padx=5)
        
        # 상태 표시줄
        self.status_label = ttk.Label(main_frame, text="준비", relief=tk.SUNKEN, anchor=tk.W)
        self.status_label.pack(fill=tk.X, pady=(10, 0))
        
        # 매크로 목록 업데이트
        self.update_macro_list()

    def update_status(self, message):
        """상태 메시지 업데이트"""
        self.status_label.config(text=message)
    
    def update_record_settings(self):
        """녹화 설정 업데이트"""
        self.recorder.record_mouse_movement = self.record_mouse_move.get()
        self.recorder.use_relative_coords = self.use_relative_coords.get()
        self.recorder.record_keyboard = self.record_keyboard.get()
        
        self.update_status("녹화 설정이 업데이트되었습니다.")
    
    def update_macro_list(self):
        """매크로 목록 업데이트"""
        self.macro_listbox.delete(0, tk.END)
        self.macro_list = self.storage.list_macros()
        
        for macro in self.macro_list:
            self.macro_listbox.insert(tk.END, macro)
    
    def update_event_list(self):
        """이벤트 목록 업데이트"""
        # 현재 선택된 항목 기억 (리스트박스에서 직접 선택한 경우만)
        if not self.selected_events:
            selected_indices = self.event_listbox.curselection()
            self.selected_events = []
            
            for idx in selected_indices:
                self.selected_events.append(idx)
        
        # 리스트박스 초기화 (녹화 중에는 목록을 보존)
        if not self.recorder.recording:
            self.event_listbox.delete(0, tk.END)
        
        # 이벤트 목록 가져오기
        if self.recorder.recording:
            events = self.recorder.events
            current_displayed = self.event_listbox.size()
            
            # 새로 추가된 이벤트만 업데이트
            for i in range(current_displayed, len(events)):
                event = events[i]
                self.display_event(event, i)
                # 새 이벤트가 추가될 때마다 항상 마지막 항목으로 스크롤
                self.event_listbox.see(tk.END)
        else:
            events = self.editor.get_events()
            
            if not events:
                return
            
            # 이벤트 표시
            for i, event in enumerate(events):
                self.display_event(event, i)
        
        # 녹화 중이 아닐 때만 선택된 항목 복원 (move_event_up/down에서 호출될 때는 복원하지 않음)
        # self.restore_selection 플래그를 사용하여 선택 복원 여부 제어
        if not self.recorder.recording and self.selected_events and getattr(self, 'restore_selection', True):
            # 먼저 모든 선택 해제
            self.event_listbox.selection_clear(0, tk.END)
            
            # 저장된 항목만 선택
            for idx in self.selected_events:
                if idx < self.event_listbox.size():
                    self.event_listbox.selection_set(idx)
        
        # 녹화 중이면 주기적으로 업데이트
        if self.recorder.recording:
            self.update_timer = self.root.after(self.update_interval, self.update_event_list)
    
    def display_event(self, event, index):
        """개별 이벤트 표시"""
        event_type = event['type']
        
        # 이벤트 유형에 따라 표시 방식 다르게 처리
        if event_type == 'delay':
            # 초 단위를 밀리초 단위로 변환하여 표시
            delay_time = event['delay']
            delay_time_ms = int(delay_time * 1000)
            event_details = f"⏱️ 딜레이: {delay_time_ms}ms"
            self.event_listbox.insert(tk.END, f"[{index+1}] {event_details}")
            self.event_listbox.itemconfig(tk.END, {'bg': '#FFE0E0'})
            
        elif event_type == 'keyboard':
            key_event = event['event_type']
            key_symbol = "⌨️ "
            if key_event == 'down':
                key_symbol = "⌨️⬇ "
            elif key_event == 'up':
                key_symbol = "⌨️⬆ "
            
            event_details = f"{key_symbol}키보드 {event['event_type']} - {event['key']}"
            self.event_listbox.insert(tk.END, f"[{index+1}] {event_details}")
            self.event_listbox.itemconfig(tk.END, {'bg': '#E0FFFF'})
            
        elif event_type == 'mouse':
            mouse_event_type = event['event_type']
            mouse_symbol = "🖱️ "
            
            if mouse_event_type == 'move':
                mouse_symbol = "🖱️➡️ "
                pos_str = f"위치: {event['position']}"
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
            
            self.event_listbox.insert(tk.END, f"[{index+1}] {event_details}")
            self.event_listbox.itemconfig(tk.END, {'bg': '#E0FFE0'})
            
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
        self.stop_btn.config(state=tk.NORMAL)
        self.save_btn.config(state=tk.DISABLED)
        self.record_status.config(text="녹화 중...", foreground="red")
        self.update_status("녹화 중...")
        
        # 이벤트 목록 초기화 및 실시간 업데이트 시작
        self.event_listbox.delete(0, tk.END)
        
        # 바로 첫 업데이트 실행
        self.update_event_list()
    
    def stop_recording(self, event=None):
        """매크로 녹화 중지"""
        # 녹화 중이 아니면 중복 실행 방지
        if not self.recorder.recording:
            return
        
        # 녹화 중지
        self.recorder.stop_recording()
        
        # UI 업데이트
        self.record_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.save_btn.config(state=tk.NORMAL)
        self.record_status.config(text="녹화 완료", foreground="black")
        self.update_status("녹화가 완료되었습니다.")
        
        # 타이머 중지
        if self.update_timer:
            self.root.after_cancel(self.update_timer)
            self.update_timer = None
        
        # 녹화된 이벤트를 에디터로 전송
        self.editor.current_events = self.recorder.events.copy()
        self.editor.modified = True
        
        # 이벤트 목록 업데이트
        self.update_event_list()
    
    def save_macro(self, event=None):
        """매크로 저장"""
        # 이벤트가 없으면 저장 불가
        if not self.editor.get_events():
            messagebox.showwarning("경고", "저장할 이벤트가 없습니다. 먼저 매크로를 녹화하세요.")
            return
        
        # 매크로 이름 입력 받기
        macro_name = simpledialog.askstring("매크로 저장", "매크로 이름을 입력하세요:")
        if not macro_name:
            return
        
        # 이미 존재하는 이름이면 덮어쓰기 확인
        if macro_name in self.storage.list_macros():
            if not messagebox.askyesno("덮어쓰기 확인", f"'{macro_name}' 매크로가 이미 존재합니다. 덮어쓰시겠습니까?"):
                return
        
        # 매크로 저장 - 인자 순서 수정 (이벤트를 먼저, 이름을 나중에)
        if self.storage.save_macro(self.editor.get_events(), macro_name):
            self.update_macro_list()
            self.update_status(f"매크로 '{macro_name}'이(가) 저장되었습니다.")
            self.editor.modified = False
        else:
            messagebox.showerror("오류", "매크로 저장에 실패했습니다.")
    
    def load_macro(self):
        """매크로 불러오기"""
        selected = self.macro_listbox.curselection()
        if not selected:
            messagebox.showwarning("경고", "불러올 매크로를 선택하세요.")
            return
        
        macro_name = self.macro_listbox.get(selected[0])
        
        # 편집 중인 매크로가 있고 변경사항이 있으면 확인
        if self.editor.modified and self.editor.get_events():
            if not messagebox.askyesno("변경사항 확인", "현재 편집 중인 매크로의 변경사항이 있습니다. 저장하지 않고 새 매크로를 불러오시겠습니까?"):
                return
        
        # 매크로 불러오기
        if self.editor.load_macro_for_editing(macro_name):
            self.update_event_list()
            self.update_status(f"매크로 '{macro_name}'을(를) 불러왔습니다.")
        else:
            messagebox.showerror("오류", f"매크로 '{macro_name}' 불러오기에 실패했습니다.")
    
    def play_macro(self, event=None):
        """매크로 실행"""
        # 선택된 매크로 또는 현재 편집 중인 매크로 실행
        events = None
        macro_name = "현재 편집 중인 매크로"
        
        # 매크로 목록에서 선택한 경우
        selected = self.macro_listbox.curselection()
        if selected:
            macro_name = self.macro_listbox.get(selected[0])
            events = self.storage.load_macro(macro_name)
        # 현재 편집 중인 매크로 사용
        else:
            events = self.editor.get_events()
        
        # 이벤트가 없으면 실행 불가
        if not events:
            messagebox.showwarning("경고", "실행할 이벤트가 없습니다.")
            return
        
        # 무한 반복 또는 반복 횟수 설정
        if self.infinite_repeat.get():
            repeat_count = 0  # player.py에서 0은 무한 반복을 의미
        else:
            # 반복 횟수 설정
            try:
                repeat_count = int(self.repeat_count.get())
                if repeat_count <= 0:
                    repeat_count = 1
            except ValueError:
                repeat_count = 1
                self.repeat_count.set("1")
        
        # 매크로 실행
        self.update_status(f"매크로 '{macro_name}' 실행 중...")
        self.player.play_macro(events, repeat_count=repeat_count)
    
    def stop_macro(self, event=None):
        """매크로 실행 중지"""
        self.player.stop_macro()
        self.update_status("매크로 실행이 중지되었습니다.")
    
    def delete_macro(self):
        """선택한 매크로 삭제"""
        selected = self.macro_listbox.curselection()
        if not selected:
            messagebox.showwarning("경고", "삭제할 매크로를 선택하세요.")
            return
        
        macro_name = self.macro_listbox.get(selected[0])
        
        # 삭제 확인
        if not messagebox.askyesno("삭제 확인", f"'{macro_name}' 매크로를 삭제하시겠습니까?"):
            return
        
        # 매크로 삭제
        if self.storage.delete_macro(macro_name):
            self.update_macro_list()
            self.update_status(f"매크로 '{macro_name}'이(가) 삭제되었습니다.")
        else:
            messagebox.showerror("오류", f"매크로 '{macro_name}' 삭제에 실패했습니다.")
    
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
        
        # 선택한 인덱스 목록
        selected_indices = list(selected)
        
        # 여러 이벤트 삭제
        if self.editor.delete_events(selected_indices):
            self.update_event_list()
            self.update_status(f"{len(selected_indices)}개 이벤트 삭제 완료")
        else:
            messagebox.showerror("오류", "이벤트 삭제에 실패했습니다.")
    
    def add_delay_to_event(self):
        """이벤트 사이에 딜레이 추가"""
        # 녹화 중에는 편집 불가
        if self.recorder.recording:
            messagebox.showwarning("경고", "녹화 중에는 이벤트를 편집할 수 없습니다.")
            return
        
        # 선택한 이벤트 인덱스
        selected = self.event_listbox.curselection()
        if not selected:
            messagebox.showwarning("경고", "딜레이를 추가할 위치를 선택하세요.")
            return
        
        # 딜레이 값 입력 받기 (밀리초 단위)
        delay_time_ms = simpledialog.askinteger("딜레이 추가", "추가할 딜레이 시간(ms):", 
                                              minvalue=10, maxvalue=60000)
        if not delay_time_ms:
            return
        
        # 밀리초를 초 단위로 변환
        delay_time = delay_time_ms / 1000
        
        # 딜레이 이벤트 생성
        delay_event = {
            'type': 'delay',
            'delay': delay_time,
            'time': 0
        }
        
        # 선택한 이벤트 아래에 추가하기 위해 인덱스 + 1 위치에 삽입
        index = selected[0] + 1
        
        # 에디터에 이벤트 추가
        if self.editor.insert_event(index, delay_event):
            # 선택 해제 및 저장
            self.restore_selection = False
            self.clear_selection()
            
            # 이벤트 목록 업데이트
            self.update_event_list()
            
            # 새로 추가된 딜레이 이벤트 선택
            self.set_single_selection(index)
            
            # 선택 복원 플래그 원복
            self.restore_selection = True
            
            self.update_status(f"{delay_time_ms}ms 딜레이가 추가되었습니다.")
        else:
            messagebox.showerror("오류", "딜레이 추가에 실패했습니다.")
            
    def modify_all_delays(self):
        """모든 딜레이 이벤트의 시간 수정"""
        # 녹화 중에는 편집 불가
        if self.recorder.recording:
            messagebox.showwarning("경고", "녹화 중에는 이벤트를 편집할 수 없습니다.")
            return
            
        if not self.editor.get_events():
            messagebox.showwarning("경고", "편집할 이벤트가 없습니다.")
            return
        
        # 배수 값 입력 받기
        multiplier = simpledialog.askfloat("딜레이 수정", "딜레이 시간 배수 (0.5=절반, 2=두배):", 
                                          minvalue=0.1, maxvalue=10.0)
        if not multiplier:
            return
        
        # 모든 딜레이 수정
        if self.editor.modify_all_delays(multiplier):
            self.update_event_list()
            self.update_status(f"딜레이 시간이 {multiplier}배로 수정되었습니다.")
        else:
            messagebox.showwarning("경고", "수정할 딜레이 이벤트가 없습니다.")
            
    def modify_delay_time(self):
        """선택한 딜레이 이벤트의 시간을 직접 수정"""
        # 녹화 중에는 편집 불가
        if self.recorder.recording:
            messagebox.showwarning("경고", "녹화 중에는 이벤트를 편집할 수 없습니다.")
            return
            
        # 현재 리스트박스에서 선택된 항목 가져오기
        selected = self.event_listbox.curselection()
        
        # 선택된 항목이 없으면 경고
        if not selected:
            messagebox.showwarning("경고", "수정할 딜레이 이벤트를 선택하세요.")
            return
            
        # 선택된 이벤트가 딜레이 이벤트인지 확인
        events = self.editor.get_events()
        delay_indices = []
        
        # 선택된 항목 중 딜레이 이벤트만 찾기
        for idx in selected:
            if idx < len(events) and events[idx]['type'] == 'delay':
                delay_indices.append(idx)
                
        if not delay_indices:
            messagebox.showwarning("경고", "선택한 항목 중 딜레이 이벤트가 없습니다.")
            return
        
        # 딜레이 시간 직접 입력 받기 (밀리초 단위)
        new_delay_time_ms = simpledialog.askinteger("딜레이 시간 설정", "새 딜레이 시간(ms):", 
                                                  minvalue=10, maxvalue=60000)
        if not new_delay_time_ms:
            return
            
        # 밀리초를 초 단위로 변환
        new_delay_time = new_delay_time_ms / 1000
        
        # 선택된 딜레이 이벤트 시간 수정
        if self.editor.set_selected_delays_time(delay_indices, new_delay_time):
            # 선택 저장
            self.selected_events = list(selected)
            
            # 이벤트 목록 업데이트
            self.update_event_list()
            
            msg = f"선택한 딜레이 이벤트({len(delay_indices)}개)의 시간이 {new_delay_time_ms}ms로 설정되었습니다."
            self.update_status(msg)
        else:
            messagebox.showerror("오류", "딜레이 시간 수정에 실패했습니다.")
    
    def select_all_events(self):
        """모든 이벤트 선택"""
        # 녹화 중에는 선택 불가
        if self.recorder.recording:
            return
            
        # 이벤트 목록 크기 가져오기
        event_count = self.event_listbox.size()
        if event_count == 0:
            return
        
        # 전체 선택이 작동하도록 내부 상태 설정
        self._skip_selection = True
        
        # 모든 이벤트를 리스트박스에서도 선택
        self.event_listbox.selection_clear(0, tk.END)
        for i in range(event_count):
            self.event_listbox.selection_set(i)
            
        # 전체 이벤트 내부적으로 선택 상태로 설정
        self.selected_events = list(range(event_count))
        
        # 전체 선택 시각적으로 표시
        if event_count > 0:
            self.event_listbox.see(0)  # 첫 번째 항목으로 스크롤
        
        self._skip_selection = False
        
        # 메시지 박스 표시 대신 상태바만 업데이트
        self.update_status(f"모든 이벤트({event_count}개)가 선택되었습니다.")
            
    def move_event_up(self):
        """선택한 이벤트를 위로 이동"""
        # 녹화 중에는 편집 불가
        if self.recorder.recording:
            messagebox.showwarning("경고", "녹화 중에는 이벤트를 편집할 수 없습니다.")
            return
            
        # 선택한 이벤트 인덱스
        selected = self.event_listbox.curselection()
        if not selected or len(selected) != 1:
            messagebox.showwarning("경고", "위로 이동할 이벤트를 하나만 선택하세요.")
            return
            
        current_index = selected[0]
            
        # 이벤트 위로 이동
        if self.editor.move_event_up(current_index):
            # 이벤트 목록 업데이트 시 선택 복원하지 않도록 플래그 설정
            self.restore_selection = False
            
            # 선택 해제
            self.clear_selection()
            
            # 이벤트 목록 업데이트
            self.update_event_list()
            
            # 이동된 새 위치 계산
            new_index = current_index - 1
            
            # 단일 항목 선택 설정
            self.set_single_selection(new_index)
            
            # 선택 복원 플래그 원복
            self.restore_selection = True
            
            self.update_status("이벤트가 위로 이동되었습니다.")
        else:
            messagebox.showwarning("경고", "이벤트를 더 위로 이동할 수 없습니다.")
            
    def move_event_down(self):
        """선택한 이벤트를 아래로 이동"""
        # 녹화 중에는 편집 불가
        if self.recorder.recording:
            messagebox.showwarning("경고", "녹화 중에는 이벤트를 편집할 수 없습니다.")
            return
            
        # 선택한 이벤트 인덱스
        selected = self.event_listbox.curselection()
        if not selected or len(selected) != 1:
            messagebox.showwarning("경고", "아래로 이동할 이벤트를 하나만 선택하세요.")
            return
            
        current_index = selected[0]
            
        # 이벤트 아래로 이동
        if self.editor.move_event_down(current_index):
            # 이벤트 목록 업데이트 시 선택 복원하지 않도록 플래그 설정
            self.restore_selection = False
            
            # 선택 해제
            self.clear_selection()
            
            # 이벤트 목록 업데이트
            self.update_event_list()
            
            # 이동된 새 위치 계산
            new_index = current_index + 1
            
            # 단일 항목 선택 설정
            self.set_single_selection(new_index)
            
            # 선택 복원 플래그 원복
            self.restore_selection = True
            
            self.update_status("이벤트가 아래로 이동되었습니다.")
        else:
            messagebox.showwarning("경고", "이벤트를 더 아래로 이동할 수 없습니다.")
    
    def on_event_select(self, event=None):
        """이벤트 리스트박스에서 항목 선택 시 호출되는 콜백"""
        # 전체 선택 처리중이면 무시
        if hasattr(self, '_skip_selection') and self._skip_selection:
            return
            
        # 리스트에서 선택된 항목들 가져오기
        selected = self.event_listbox.curselection()
        
        # 선택된 항목들을 self.selected_events에 저장
        self.selected_events = list(selected)
    
    def clear_selection(self):
        """이벤트 목록에서 모든 선택 해제"""
        self.event_listbox.selection_clear(0, tk.END)
        self.selected_events = []
        
    def set_single_selection(self, index):
        """단일 항목만 선택"""
        if index < 0 or index >= self.event_listbox.size():
            return False
            
        self._skip_selection = True
        self.event_listbox.selection_clear(0, tk.END)
        self.event_listbox.selection_set(index)
        self.event_listbox.see(index)
        self.selected_events = [index]
        self._skip_selection = False
        return True
    
    def setup_keyboard_shortcuts(self):
        """키보드 단축키 설정"""
        # F5 키: 매크로 실행
        self.root.bind("<F5>", lambda event: self.play_macro())
        
        # F6 키: 매크로 실행 중지
        self.root.bind("<F6>", lambda event: self.stop_macro())
        
        # Ctrl+R: 녹화 시작/중지 토글
        self.root.bind("<Control-r>", self.toggle_recording)
        
        # Ctrl+S: 매크로 저장
        self.root.bind("<Control-s>", lambda event: self.save_macro())
    
    def toggle_recording(self, event=None):
        """녹화 시작/중지 토글"""
        # 현재 녹화 중이면 중지, 아니면 시작
        if self.recorder.recording:
            self.stop_recording()
        else:
            self.start_recording() 
    
    def toggle_infinite_repeat(self):
        """무한 반복 토글 시 호출되는 함수"""
        if self.infinite_repeat.get():
            # 무한 반복이 체크되면 반복 횟수 입력란 비활성화
            self.repeat_count_entry.config(state=tk.DISABLED)
            self.repeat_count.set("∞")
        else:
            # 무한 반복이 해제되면 반복 횟수 입력란 활성화
            self.repeat_count_entry.config(state=tk.NORMAL)
            self.repeat_count.set("1") 