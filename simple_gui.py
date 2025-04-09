import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import time
import mouse
import keyboard
import os
import copy

class SimpleGUI:
    def __init__(self, root, recorder, player, editor, storage, gesture_manager=None):
        self.root = root
        self.recorder = recorder
        self.player = player
        self.editor = editor
        self.storage = storage
        self.gesture_manager = gesture_manager  # 제스처 매니저 추가
        
        # 제스처 인식 활성화 상태 변수 추가
        self.gesture_enabled = tk.BooleanVar(value=False)
        
        # 스타일 설정
        self.setup_styles()
        
        # 윈도우 설정
        self.root.title("제스처 매크로 프로그램")
        
        # 창 크기 설정 (width x height) - 더 작은 크기로 변경
        window_width = 1200  # 900에서 1000으로 변경
        window_height = 1200  # 900에서 1200으로 변경
        
        # 화면 크기 가져오기
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # 창을 화면 중앙에 배치하기 위한 x, y 좌표 계산
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        # 창 크기와 위치 설정
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # 최소 창 크기 설정
        self.root.minsize(1000, 800)
        
        # 포커스 설정
        self.root.lift()
        self.root.focus_force()
        
        # GUI 구성요소
        self.gesture_listbox = None
        self.event_listbox = None
        self.status_label = None
        
        # 현재 녹화 중인 제스처
        self.current_gesture = None
        
        # 현재 선택된 제스처 (포커스 유지를 위한 변수)
        self.selected_gesture_index = None
        self.selected_gesture_name = None
        
        # 실시간 업데이트 관련
        self.update_timer = None
        self.update_interval = 100  # 0.1초마다 업데이트
        
        # 녹화 설정
        self.record_mouse_move = tk.BooleanVar(value=False)
        self.record_delay = tk.BooleanVar(value=True)  # 딜레이 녹화 설정 기본값을 True로 변경
        self.use_relative_coords = tk.BooleanVar(value=False)  # 상대좌표 (기본값 False)
        self.use_absolute_coords = tk.BooleanVar(value=True)  # 절대좌표 변수 추가 (기본값 True)
        self.record_keyboard = tk.BooleanVar(value=True)
        
        # 무한 반복 설정
        self.infinite_repeat = tk.BooleanVar(value=False)
        
        # 이벤트 선택 관련
        self.selected_events = []
        self.restore_selection = True  # 선택 복원 여부 제어 플래그
        
        # 단축키 설정
        self.setup_keyboard_shortcuts()
        
        # 제스처 매니저 콜백 설정은 setup_ui에서 수행하므로 여기서 제거

    def setup_ui(self):
        """간소화된 GUI 구성"""
        # 메인 프레임
        main_frame = ttk.Frame(self.root, padding=20)  # 패딩 증가
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 윈도우 전체에 클릭 이벤트 바인딩 - 제스처 선택 유지
        self.root.bind('<Button-1>', lambda e: self.root.after(10, self.ensure_gesture_selection))
        
        # 최상단 제스처 인식 제어 프레임 (전체 UI 위에 배치)
        gesture_control_frame = ttk.Frame(main_frame)
        gesture_control_frame.pack(fill=tk.X, pady=(0, 15))
        
        # 제목 레이블 추가
        title_label = ttk.Label(gesture_control_frame, text="제스처 매크로", font=('Arial', 12, 'bold'))
        title_label.pack(side=tk.TOP, pady=(0, 10))
        
        # 제스처 인식 시작/중지 버튼을 큰 버튼으로 상단에 배치
        if self.gesture_manager:
            gesture_button_frame = ttk.Frame(gesture_control_frame)
            gesture_button_frame.pack(fill=tk.X)
            
            self.gesture_start_btn = ttk.Button(gesture_button_frame, text="시작", width=20,
                               command=self.start_gesture_recognition, style='Big.TButton')
            self.gesture_start_btn.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)
            
            self.gesture_stop_btn = ttk.Button(gesture_button_frame, text="중지", width=20,
                               command=self.stop_gesture_recognition, state=tk.DISABLED, style='Big.TButton')
            self.gesture_stop_btn.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)
        
        # 구분선 추가
        separator = ttk.Separator(main_frame, orient='horizontal')
        separator.pack(fill=tk.X, pady=10)
        
        # 상단 제어 프레임 (매크로 녹화 등)
        control_frame = ttk.LabelFrame(main_frame, text="매크로 제어", padding=15)
        control_frame.pack(fill=tk.X, pady=(0, 15))
        
        # 제어 버튼 프레임
        button_frame = ttk.Frame(control_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        # 제스처 녹화 버튼
        if self.gesture_manager:
            ttk.Button(button_frame, text="제스처 녹화", width=15,
                     command=self.start_gesture_recording).pack(side=tk.LEFT, padx=10)
        
        # 매크로 녹화 버튼 - 선택된 제스처에 매크로 녹화 수행
        self.record_btn = ttk.Button(button_frame, text="매크로 녹화 (F9)", 
                                    width=15,
                                    command=self.start_recording_for_selected_gesture)
        self.record_btn.pack(side=tk.LEFT, padx=10)
        
        # 녹화 중지 버튼
        self.stop_btn = ttk.Button(button_frame, text="녹화 완료 (F10)", 
                                  width=15,  # 버튼 너비 추가
                                  command=self.stop_recording, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=10)  # 패딩 증가
        
        # 저장 버튼 추가
        self.save_btn = ttk.Button(button_frame, text="저장", 
                                  width=15,  # 버튼 너비 추가
                                  command=self.save_macro, state=tk.NORMAL)  # 항상 활성화 상태로 변경
        self.save_btn.pack(side=tk.LEFT, padx=10)  # 패딩 증가
        
        # 녹화 상태 표시
        self.record_status = ttk.Label(control_frame, text="준비", foreground="black")
        self.record_status.pack(anchor=tk.W, pady=(5, 0))
        
        # 메인 컨텐츠 영역 - 좌우 분할
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # 왼쪽 프레임 - 제스처 목록 (가로 크기를 줄임)
        left_frame = ttk.Frame(content_frame, width=300)  # 프레임 자체에 width 설정
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=(0, 5))  # width 옵션 제거
        left_frame.pack_propagate(False)  # 크기 고정을 위해 pack_propagate를 False로 설정
        
        # 제스처 목록 프레임
        gesture_frame = ttk.LabelFrame(left_frame, text="제스처 목록", padding=10)
        gesture_frame.pack(fill=tk.BOTH, expand=True)
        
        # 제스처 리스트박스 및 스크롤바
        gesture_scrollbar = ttk.Scrollbar(gesture_frame)
        gesture_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.gesture_listbox = tk.Listbox(gesture_frame, font=('Consolas', 11), height=15, 
                                         selectmode=tk.EXTENDED,  # 다중 선택 모드로 변경
                                         exportselection=False)  # exportselection=False로 설정하여 포커스가 빠져도 선택 유지
        self.gesture_listbox.pack(fill=tk.BOTH, expand=True)
        self.gesture_listbox.config(yscrollcommand=gesture_scrollbar.set, 
                                   selectbackground='#4a6cd4', 
                                   selectforeground='white')
        gesture_scrollbar.config(command=self.gesture_listbox.yview)
        
        # 제스처 선택 이벤트 바인딩 - 이벤트 목록 업데이트
        self.gesture_listbox.bind('<<ListboxSelect>>', self.on_gesture_select)
        # 포커스 이벤트 바인딩 - 포커스가 사라져도 선택 유지
        self.gesture_listbox.bind('<FocusOut>', self.maintain_gesture_selection)
        
        # 제스처 목록 아래 버튼 프레임
        gesture_btn_frame = ttk.Frame(gesture_frame)
        gesture_btn_frame.pack(fill=tk.X, pady=(10, 0))  # 상단 패딩 증가
        
        ttk.Button(gesture_btn_frame, text="수정", width=10,  # 수정 버튼 추가
                  command=self.edit_gesture).pack(side=tk.LEFT, padx=5)
        ttk.Button(gesture_btn_frame, text="삭제", width=10,  # 버튼 너비 추가
                  command=self.delete_gesture).pack(side=tk.LEFT, padx=5)
        
        # 제스처 이동 버튼은 삭제 (repeat_frame으로 이동)
        
        # 반복 횟수 설정
        repeat_frame = ttk.Frame(gesture_frame)
        repeat_frame.pack(fill=tk.X, pady=(5, 0))

        ttk.Label(repeat_frame, text="반복 횟수:").pack(side=tk.LEFT, padx=5)

        self.repeat_count = tk.StringVar(value="1")
        self.repeat_count_entry = ttk.Entry(repeat_frame, textvariable=self.repeat_count, width=5)
        self.repeat_count_entry.pack(side=tk.LEFT, padx=5)

        # 제스처 이동 버튼을 반복 횟수 오른쪽으로 이동
        ttk.Button(repeat_frame, text="↑", width=2,
                  command=self.move_gesture_up).pack(side=tk.RIGHT, padx=2)
        ttk.Button(repeat_frame, text="↓", width=2,
                  command=self.move_gesture_down).pack(side=tk.RIGHT, padx=2)
        
        # 무한 반복 체크박스를 별도 프레임으로 이동
        infinite_frame = ttk.Frame(gesture_frame)
        infinite_frame.pack(fill=tk.X, pady=(5, 0))

        self.infinite_checkbox = ttk.Checkbutton(infinite_frame, text="무한 반복", 
                                                variable=self.infinite_repeat,
                                                command=self.toggle_infinite_repeat)
        self.infinite_checkbox.pack(side=tk.LEFT, padx=5)
        
        # 오른쪽 프레임 - 이벤트 목록
        right_frame = ttk.LabelFrame(content_frame, text="이벤트 목록", padding=10)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        # 이벤트 리스트박스 및 스크롤바
        event_scrollbar = ttk.Scrollbar(right_frame)
        event_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # SINGLE 대신 EXTENDED 모드 사용 (다중 선택 가능)
        self.event_listbox = tk.Listbox(right_frame, font=('Consolas', 11), selectmode=tk.EXTENDED, 
                                       activestyle='dotbox', highlightthickness=2)
        self.event_listbox.pack(fill=tk.BOTH, expand=True)
        self.event_listbox.config(yscrollcommand=event_scrollbar.set, 
                                 selectbackground='#4a6cd4', 
                                 selectforeground='white')
        event_scrollbar.config(command=self.event_listbox.yview)
        
        # 선택 변경 이벤트 바인딩
        self.event_listbox.bind('<<ListboxSelect>>', self.on_event_select)
        # 더블 클릭 이벤트 바인딩 추가
        self.event_listbox.bind('<Double-1>', self.on_event_double_click)
        
        # 이벤트 목록 아래 버튼 프레임 - 새 버튼 줄 추가
        event_btn_frame = ttk.Frame(right_frame)
        event_btn_frame.pack(fill=tk.X, pady=(5, 0))

        ttk.Button(event_btn_frame, text="전체 선택", 
                  command=self.select_all_events).pack(side=tk.LEFT, padx=5)

        ttk.Button(event_btn_frame, text="선택 삭제", 
                  command=self.delete_selected_event).pack(side=tk.LEFT, padx=5)

        ttk.Button(event_btn_frame, text="딜레이 추가", 
                  command=self.add_delay_to_event).pack(side=tk.LEFT, padx=5)

        ttk.Button(event_btn_frame, text="딜레이 삭제", 
                  command=self.delete_delay_events).pack(side=tk.LEFT, padx=5)

        ttk.Button(event_btn_frame, text="딜레이 수정", 
                  command=self.modify_delay_time).pack(side=tk.LEFT, padx=5)

        # 이벤트 이동 버튼
        ttk.Button(event_btn_frame, text="↑", width=2,
                  command=self.move_event_up).pack(side=tk.RIGHT, padx=2)
        ttk.Button(event_btn_frame, text="↓", width=2,
                  command=self.move_event_down).pack(side=tk.RIGHT, padx=2)

        # 랜덤 딜레이 버튼 프레임 추가
        random_delay_frame = ttk.Frame(right_frame)
        random_delay_frame.pack(fill=tk.X, pady=(5, 0))

        ttk.Button(random_delay_frame, text="랜덤 좌표 추가", 
                  command=self.add_random_position).pack(side=tk.LEFT, padx=5)

        ttk.Button(random_delay_frame, text="랜덤 딜레이 추가", 
                  command=self.add_random_delay).pack(side=tk.LEFT, padx=5)

        # 간단한 설정 프레임
        settings_frame = ttk.Frame(right_frame)
        settings_frame.pack(fill=tk.X, pady=(5, 0))
        
        # 명시적으로 변수 재설정 (초기화 문제 해결)
        self.use_absolute_coords.set(True)
        self.use_relative_coords.set(False)
        
        # 딜레이 녹화 체크박스를 마우스 이동 녹화 체크박스 왼쪽에 추가
        ttk.Checkbutton(settings_frame, text="딜레이 녹화", 
                      variable=self.record_delay,
                      command=self.update_record_settings).pack(side=tk.LEFT, padx=5)
        
        # 키보드 녹화와 마우스 이동 녹화 체크박스의 위치 변경
        ttk.Checkbutton(settings_frame, text="키보드 녹화", 
                       variable=self.record_keyboard,
                       command=self.update_record_settings).pack(side=tk.LEFT, padx=5)
                       
        ttk.Checkbutton(settings_frame, text="마우스 이동 녹화", 
                       variable=self.record_mouse_move,
                       command=self.update_record_settings).pack(side=tk.LEFT, padx=5)
        
        # 절대좌표와 상대좌표 체크박스 추가
        ttk.Checkbutton(settings_frame, text="절대좌표 녹화", 
                       variable=self.use_absolute_coords,
                       command=lambda: self.toggle_absolute_coords()).pack(side=tk.LEFT, padx=5)
                       
        ttk.Checkbutton(settings_frame, text="상대좌표 녹화", 
                       variable=self.use_relative_coords,
                       command=lambda: self.toggle_relative_coords()).pack(side=tk.LEFT, padx=5)
        
        # 상태 표시줄
        self.status_label = ttk.Label(main_frame, text="준비", relief=tk.SUNKEN, anchor=tk.W)
        self.status_label.pack(fill=tk.X, pady=(10, 0))
        
        # 제스처 목록 업데이트
        if self.gesture_manager:
            self.update_gesture_list()
            
        # 제스처 매니저 콜백 설정
        if self.gesture_manager:
            print("제스처 매니저 콜백 설정 시작")  # 디버깅 로그 추가
            
            # 녹화기 설정
            self.gesture_manager.recorder = self.recorder
            
            # 제스처 목록 업데이트 콜백 설정
            self.gesture_manager.set_update_gesture_list_callback(self.update_gesture_list)
            print("제스처 목록 업데이트 콜백 설정 완료")  # 디버깅 로그 추가
            
            # 매크로 녹화 요청 콜백 설정
            self.gesture_manager.set_macro_record_callback(self.start_macro_for_gesture)
            print("매크로 녹화 요청 콜백 설정 완료")  # 디버깅 로그 추가
            
            # GUI 참조 설정
            self.gesture_manager.set_gui_callback(self)
            print("GUI 참조 설정 완료")  # 디버깅 로그 추가

        # 초기 설정 업데이트 - 레코더의 설정 초기화
        print("초기 레코더 설정 업데이트")  # 디버깅 로그 추가
        self.update_record_settings()

    def setup_styles(self):
        """버튼 스타일 설정"""
        style = ttk.Style()
        # 큰 버튼 스타일 추가
        style.configure('Big.TButton', font=('Arial', 11, 'bold'), padding=10)

    def update_status(self, message):
        """상태 메시지 업데이트"""
        self.status_label.config(text=message)
    
    def update_record_settings(self):
        """녹화 설정 업데이트"""
        print(f"update_record_settings 호출됨: 절대좌표={self.use_absolute_coords.get()}, 상대좌표={self.use_relative_coords.get()}")  # 디버깅 로그 추가
        
        # 좌표 타입 충돌 해결
        if self.use_absolute_coords.get() and self.use_relative_coords.get():
            print("좌표 타입 충돌 감지 - 절대좌표 우선 사용")
            self.use_relative_coords.set(False)
        elif not self.use_absolute_coords.get() and not self.use_relative_coords.get():
            print("좌표 타입 미설정 감지 - 절대좌표 기본값으로 설정")
            self.use_absolute_coords.set(True)
        
        self.recorder.record_mouse_movement = self.record_mouse_move.get()
        self.recorder.use_relative_coords = self.use_relative_coords.get()
        self.recorder.record_keyboard = self.record_keyboard.get()
        self.recorder.record_delay = self.record_delay.get()  # 딜레이 녹화 설정 추가
        
        # 녹화 설정 메시지 준비
        settings = []
        if self.record_delay.get():
            settings.append("딜레이")
        if self.record_mouse_move.get():
            coords_type = "상대좌표" if self.use_relative_coords.get() else "절대좌표"
            settings.append(f"마우스 이동 ({coords_type})")
        if self.record_keyboard.get():
            settings.append("키보드")
            
        if settings:
            self.update_status(f"녹화 설정이 업데이트되었습니다: {', '.join(settings)}")
        else:
            self.update_status("경고: 모든 녹화 설정이 비활성화되었습니다.")
    
    def start_gesture_recording(self):
        """새 제스처 녹화 시작"""
        if not self.gesture_manager:
            return
            
        # 제스처 인식기가 활성화되어 있는지 확인
        if not self.gesture_enabled.get():
            if messagebox.askyesno("제스처 인식 활성화", 
                                 "제스처 녹화를 위해 제스처 인식을 활성화해야 합니다.\n활성화하시겠습니까?"):
                self.gesture_enabled.set(True)
                self.toggle_gesture_recognition()
            else:
                return
        
        # 제스처 녹화 시작
        self.gesture_manager.start_gesture_recording()
        
        # 상태 업데이트
        self.update_status("제스처 녹화 중...")
    
    def start_macro_for_gesture(self, gesture):
        """특정 제스처에 대한 매크로 녹화 시작"""
        print(f"start_macro_for_gesture 호출됨 - 제스처: {gesture}")  # 디버깅 로그 추가
        
        # 현재 제스처 저장
        self.current_gesture = gesture
        
        # 매크로 녹화 시작
        self.start_recording()
        
        # 상태 업데이트
        self.update_status(f"제스처 '{gesture}'에 대한 매크로 녹화 중...")
    
    def start_recording(self):
        """매크로 녹화 시작"""
        print("매크로 녹화 시작 함수 호출됨")  # 디버깅 로그 추가
        if self.recorder.recording:
            print("이미 녹화 중")  # 디버깅 로그 추가
            return
        
        # 녹화 시작
        self.recorder.start_recording()
        print("recorder.start_recording() 호출 완료")  # 디버깅 로그 추가
        
        # 버튼 상태 변경
        self.record_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        # self.save_btn.config(state=tk.DISABLED) 라인 제거 - 저장 버튼은 항상 활성화 상태 유지
        
        # 녹화 상태 표시
        self.record_status.config(text="녹화 중", foreground="red")
        
        # 이벤트 목록 초기화
        self.event_listbox.delete(0, tk.END)
        
        # 이벤트 목록 실시간 업데이트 시작
        self.start_event_list_updates()
        
        # 상태 업데이트 (이미 제스처 녹화 중인 경우 메시지를 변경하지 않음)
        if not self.current_gesture:
            self.update_status("매크로 녹화 중...")
    
    def start_event_list_updates(self):
        """이벤트 목록 실시간 업데이트 시작"""
        print("이벤트 목록 업데이트 시작")  # 디버깅 로그 추가
        # 기존 타이머가 있으면 중지
        if self.update_timer:
            self.root.after_cancel(self.update_timer)
            self.update_timer = None
        
        # 첫 번째 업데이트 즉시 시작
        self.update_event_list()
    
    def stop_event_list_updates(self):
        """이벤트 목록 실시간 업데이트 중지"""
        print("이벤트 목록 업데이트 중지")  # 디버깅 로그 추가
        if self.update_timer:
            self.root.after_cancel(self.update_timer)
            self.update_timer = None
    
    def stop_recording(self):
        """매크로 녹화 중지"""
        if not self.recorder.recording:
            return
        
        # 녹화 중지
        self.recorder.stop_recording()
        
        # 버튼 상태 변경
        self.record_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        
        # 녹화 상태 표시
        self.record_status.config(text="준비", foreground="black")
        
        # 이벤트 목록 실시간 업데이트 중지
        self.stop_event_list_updates()
        
        # 제스처에 대한 매크로 녹화인 경우 자동 저장
        if self.current_gesture:
            self.save_gesture_macro()
            # self.save_btn.config(state=tk.DISABLED) 라인 제거 - 저장 버튼은 항상 활성화 상태 유지
        else:
            # 일반 매크로 녹화인 경우 저장 준비
            # self.save_btn.config(state=tk.NORMAL) 라인 제거 - 저장 버튼은 항상 활성화 상태 유지
            self.update_status("녹화 완료. 저장하려면 '저장' 버튼을 클릭하세요.")
    
    def save_gesture_macro(self):
        """제스처에 대한 매크로 저장"""
        if not self.gesture_manager or not self.current_gesture:
            return
            
        # 녹화된 매크로 이벤트 가져오기
        events = self.recorder.events
        
        # 이벤트가 없으면 빈 배열로 초기화 (빈 이벤트 저장 허용)
        if not events:
            print("녹화된 이벤트가 없어 빈 배열로 초기화")  # 디버깅 로그 추가
            events = []
            # 사용자에게 빈 이벤트 저장 확인
            if not messagebox.askyesno("빈 이벤트 저장", 
                                     f"제스처 '{self.current_gesture}'에 빈 이벤트 목록을 저장하시겠습니까?"):
                self.update_status("저장이 취소되었습니다.")
                self.current_gesture = None
                return
        
        # 제스처에 매크로 저장
        success = self.gesture_manager.save_macro_for_gesture(self.current_gesture, events)
        
        if success:
            # 이벤트 개수에 따라 메시지 다르게 표시
            if len(events) == 0:
                messagebox.showinfo("저장 완료", 
                                  f"제스처 '{self.current_gesture}'에 빈 매크로가 저장되었습니다.")
                self.update_status(f"제스처 '{self.current_gesture}'에 빈 매크로가 저장되었습니다.")
            else:
                messagebox.showinfo("저장 완료", 
                                  f"제스처 '{self.current_gesture}'에 매크로({len(events)}개 이벤트)가 저장되었습니다.")
                self.update_status(f"제스처 '{self.current_gesture}'에 매크로가 저장되었습니다.")
        else:
            messagebox.showerror("저장 오류", "매크로 저장 중 오류가 발생했습니다.")
            self.update_status("매크로 저장 중 오류가 발생했습니다.")
        
        # 현재 제스처 초기화
        self.current_gesture = None
    
    def save_macro(self):
        """매크로 저장 - 선택된 제스처에 이벤트 직접 저장"""
        # 현재 이벤트 목록 가져오기
        events = None
        if self.recorder.recording:
            events = self.recorder.events
        elif hasattr(self.editor, 'get_events') and callable(self.editor.get_events):
            events = self.editor.get_events()
        elif hasattr(self.editor, 'events'):
            events = self.editor.events
        
        # 이벤트가 없으면 빈 배열로 초기화 (빈 이벤트 저장 허용)
        if not events:
            print("이벤트가 없어 빈 배열로 초기화")  # 디버깅 로그 추가
            events = []
        
        # 현재 UI에서 선택된 제스처 확인 - 리스트박스에서 선택 확인
        selected_gesture = None
        if self.gesture_listbox and self.gesture_listbox.curselection():
            selected_index = self.gesture_listbox.curselection()[0]
            selected_gesture = self.gesture_listbox.get(selected_index)
            # 내부 변수 업데이트
            self.selected_gesture_index = selected_index
            self.selected_gesture_name = selected_gesture
        # 리스트박스에 선택이 없는 경우 내부 변수 사용
        elif self.selected_gesture_name:
            selected_gesture = self.selected_gesture_name
        
        # 선택된 제스처가 있으면 해당 제스처에 매크로 저장
        if selected_gesture and self.gesture_manager:
            # 이벤트 배열이 비어있는지 확인
            if len(events) == 0:
                # 사용자에게 빈 이벤트 저장 확인
                if not messagebox.askyesno("빈 이벤트 저장", f"제스처 '{selected_gesture}'에 빈 이벤트 목록을 저장하시겠습니까?"):
                    self.update_status("저장이 취소되었습니다.")
                    return
            
            # 매크로 이름 생성 (제스처 기반) - 파일명으로 사용할 수 있게 가공
            safe_gesture = selected_gesture.replace('→', '_RIGHT_').replace('↓', '_DOWN_').replace('←', '_LEFT_').replace('↑', '_UP_')
            macro_name = f"gesture_{safe_gesture}.json"
            
            # 에디터에 현재 매크로 이름 설정
            if hasattr(self.editor, 'set_current_macro') and callable(self.editor.set_current_macro):
                self.editor.set_current_macro(macro_name)
                print(f"저장 시 에디터의 현재 편집 중인 매크로 이름 설정: {macro_name}")  # 디버깅 로그
            
            success = self.gesture_manager.save_macro_for_gesture(selected_gesture, events)
            
            if success:
                # 이벤트 개수에 따라 메시지 다르게 표시
                if len(events) == 0:
                    messagebox.showinfo("저장 완료", f"제스처 '{selected_gesture}'에 빈 매크로가 저장되었습니다.")
                    self.update_status(f"제스처 '{selected_gesture}'에 빈 매크로가 저장되었습니다.")
                else:
                    messagebox.showinfo("저장 완료", f"제스처 '{selected_gesture}'에 매크로({len(events)}개 이벤트)가 저장되었습니다.")
                    self.update_status(f"제스처 '{selected_gesture}'에 매크로가 저장되었습니다.")
            else:
                messagebox.showerror("저장 오류", "매크로 저장 중 오류가 발생했습니다.")
                self.update_status("매크로 저장 중 오류가 발생했습니다.")
        else:
            # 선택된 제스처가 없을 경우 경고
            messagebox.showwarning("선택 오류", "저장할 제스처를 먼저 선택하세요.")
            self.update_status("저장할 제스처를 먼저 선택하세요.")
    
    def update_gesture_list(self):
        """제스처 목록 업데이트"""
        print("update_gesture_list 함수 호출됨")  # 디버깅 로그 추가
        # 제스처 매니저가 없으면 무시
        if not self.gesture_manager:
            print("제스처 매니저 없음")  # 디버깅 로그 추가
            return
        
        # 현재 선택된 제스처 저장
        selected_gesture_name = self.selected_gesture_name
        
        # 리스트박스 초기화
        self.gesture_listbox.delete(0, tk.END)
        
        # 제스처 목록 가져오기
        gesture_mappings = self.gesture_manager.get_mappings()
        gestures = list(gesture_mappings.keys())
        
        # 제스처 목록 표시
        for gesture in gestures:
            # 오래된 모디파이어 표기를 현대화된 표기로 변환
            display_gesture = gesture
            # A 또는 AT -> Alt로 변환
            display_gesture = display_gesture.replace("A-", "Alt-").replace("AT", "Alt")
            # CT -> Ctrl로 변환
            display_gesture = display_gesture.replace("CT", "Ctrl")
            
            self.gesture_listbox.insert(tk.END, display_gesture)
        
        # 이전에 선택된 제스처 다시 선택
        if selected_gesture_name in gestures:
            idx = gestures.index(selected_gesture_name)
            self.gesture_listbox.selection_clear(0, tk.END)  # 모든 선택 해제
            self.gesture_listbox.selection_set(idx)
            self.gesture_listbox.see(idx)  # 해당 위치로 스크롤
            self.selected_gesture_index = idx
            self.selected_gesture_name = selected_gesture_name
            print(f"제스처 선택 복원: {selected_gesture_name}")  # 디버깅 로그 추가
            
            # 선택된 제스처의 이벤트 목록 업데이트
            self.update_event_list_for_gesture(selected_gesture_name)
        else:
            # 선택된 제스처가 없는 경우 선택 정보 초기화
            self.selected_gesture_index = None
            self.selected_gesture_name = None
            
        # 제스처 개수 업데이트
        print(f"제스처 목록 업데이트 완료: {len(gestures)}개")  # 디버깅 로그 추가
    
    def delete_gesture(self):
        """선택된 제스처 삭제"""
        # 선택된 모든 항목의 인덱스 가져오기 (역순으로 정렬)
        selected_indices = list(self.gesture_listbox.curselection())
        selected_indices.sort(reverse=True)  # 역순으로 정렬하여 삭제 시 인덱스 변화 방지
        
        if not selected_indices:
            messagebox.showwarning("경고", "삭제할 제스처를 선택해주세요.")
            return
            
        # 선택된 모든 제스처 삭제
        deleted_count = 0
        for index in selected_indices:
            gesture_name = self.gesture_listbox.get(index)
            if gesture_name in self.gesture_manager.gesture_mappings:
                self.gesture_manager.remove_mapping(gesture_name)
                deleted_count += 1
        
        # 선택 초기화
        self.selected_gesture_index = None
        self.selected_gesture_name = None
        
        # 이벤트 목록 초기화
        self.event_listbox.delete(0, tk.END)
        
        # 제스처 목록 전체 새로고침
        self.update_gesture_list()
        
        # 삭제 결과 메시지
        self.update_status(f"{deleted_count}개의 제스처가 삭제되었습니다.")
    
    def play_gesture_macro(self):
        """선택된 제스처의 매크로 실행"""
        if not self.gesture_manager:
            return
            
        # 선택된 제스처 확인
        selected = self.gesture_listbox.curselection()
        if not selected:
            messagebox.showwarning("선택 오류", "실행할 제스처를 선택하세요.")
            return
            
        # 제스처 이름 가져오기
        gesture = self.gesture_listbox.get(selected[0])
        
        # 제스처에 연결된 매크로 실행
        repeat_count = 1  # 기본값
        
        # 반복 횟수 설정
        if self.infinite_repeat.get():
            repeat_count = -1  # 무한 반복
        else:
            try:
                repeat_count = int(self.repeat_count.get())
                if repeat_count < 1:
                    repeat_count = 1
            except ValueError:
                repeat_count = 1
        
        # 매크로 실행
        self.gesture_manager.execute_gesture_action(gesture)
        self.update_status(f"제스처 '{gesture}'의 매크로를 실행 중...")
    
    def toggle_gesture_recognition(self):
        """제스처 인식 켜기/끄기"""
        if not self.gesture_manager:
            return
            
        if self.gesture_enabled.get():
            self.stop_gesture_recognition()
        else:
            self.start_gesture_recognition()
    
    # 기존 매크로 관련 함수들 유지
    def play_macro(self):
        """매크로 실행"""
        # ... 기존 코드 ...
    
    def stop_macro(self):
        """매크로 실행 중지"""
        # ... 기존 코드 ...
    
    # 나머지 기존 함수들 유지
    def update_event_list(self):
        """이벤트 목록 업데이트"""
        print("update_event_list 함수 호출됨")  # 디버깅 로그 추가
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
            events = None
            # editor.get_events() 메서드 확인
            if hasattr(self.editor, 'get_events') and callable(self.editor.get_events):
                try:
                    events = self.editor.get_events()
                    print(f"에디터에서 이벤트 {len(events)}개 로드함")  # 디버깅 로그 추가
                except Exception as e:
                    print(f"get_events 호출 중 오류: {e}")  # 디버깅 로그 추가
                    events = []
            # events 속성 직접 접근
            elif hasattr(self.editor, 'events'):
                try:
                    events = self.editor.events
                    print(f"에디터 events 속성에서 {len(events)}개 로드함")  # 디버깅 로그 추가
                except Exception as e:
                    print(f"events 속성 접근 중 오류: {e}")  # 디버깅 로그 추가
                    events = []
            else:
                print("에디터에서 이벤트를 가져올 수 없음")  # 디버깅 로그 추가
                events = []
            
            # 선택된 제스처가 있고 events가 비어있는 경우 제스처의 매크로 로드 시도
            # 'skip_auto_reload' 플래그가 True면 자동 로드를 건너뛴다
            if not events and hasattr(self, 'gesture_listbox') and not getattr(self, 'skip_auto_reload', False):
                print("에디터에 이벤트가 없어 제스처의 매크로 로드 시도")  # 디버깅 로그 추가
                selected_gesture = self.gesture_listbox.curselection()
                if selected_gesture:
                    gesture = self.gesture_listbox.get(selected_gesture[0])
                    print(f"선택된 제스처: {gesture}")  # 디버깅 로그 추가
                    
                    # 제스처에 대한 매크로 로드 시도
                    if self.gesture_manager and gesture in self.gesture_manager.gesture_mappings:
                        macro_name = self.gesture_manager.gesture_mappings[gesture]
                        full_path = os.path.join("macros", macro_name)
                        
                        try:
                            # 파일이 없으면 대체 경로 시도
                            if not os.path.exists(full_path):
                                safe_gesture = gesture.replace('→', '_RIGHT_').replace('↓', '_DOWN_').replace('←', '_LEFT_').replace('↑', '_UP_')
                                alternative_path = os.path.join("macros", f"gesture_{safe_gesture}.json")
                                
                                if os.path.exists(alternative_path):
                                    full_path = alternative_path
                            
                            # 파일이 존재하면 읽기
                            if os.path.exists(full_path):
                                print(f"매크로 파일 로드: {full_path}")  # 디버깅 로그 추가
                                with open(full_path, 'r') as f:
                                    import json
                                    macro_data = json.load(f)
                                
                                print(f"매크로 데이터 로드됨: {len(macro_data)}개 이벤트")  # 디버깅 로그 추가
                                
                                # 에디터에 이벤트 설정
                                if hasattr(self.editor, 'load_events'):
                                    print("editor.load_events 호출")  # 디버깅 로그 추가
                                    self.editor.load_events(macro_data)
                                elif hasattr(self.editor, 'events'):
                                    print("editor.events에 직접 할당")  # 디버깅 로그 추가
                                    import copy
                                    self.editor.events = copy.deepcopy(macro_data)
                                
                                # events 변수 업데이트
                                events = macro_data
                            else:
                                print(f"매크로 파일을 찾을 수 없음: {full_path}")  # 디버깅 로그 추가
                        except Exception as e:
                            print(f"매크로 로드 중 오류: {e}")  # 디버깅 로그 추가
                            import traceback
                            traceback.print_exc()
            
            if not events:
                print("표시할 이벤트 없음")  # 디버깅 로그 추가
                return
            
            # 이벤트 표시
            for i, event in enumerate(events):
                self.display_event(event, i)
            
            print(f"{len(events)}개 이벤트 표시됨")  # 디버깅 로그 추가
        
        # 'skip_auto_reload' 플래그를 사용 후 리셋
        if hasattr(self, 'skip_auto_reload'):
            self.skip_auto_reload = False
        
        # 녹화 중이 아닐 때만 선택된 항목 복원 (move_event_up/down에서 호출될 때는 복원하지 않음)
        # self.restore_selection 플래그를 사용하여 선택 복원 여부 제어
        if not self.recorder.recording and self.selected_events and getattr(self, 'restore_selection', True):
            # 선택하기 전 영역 확인 - 범위를 벗어나면 선택 안함
            max_index = self.event_listbox.size() - 1
            valid_selections = [idx for idx in self.selected_events if idx <= max_index]
            
            if valid_selections:
                # 먼저 모든 선택 해제
                self.event_listbox.selection_clear(0, tk.END)
                
                # 저장된 항목만 선택
                for idx in valid_selections:
                    if idx < self.event_listbox.size():
                        self.event_listbox.selection_set(idx)
                        print(f"이벤트 {idx}번 선택 복원됨")  # 디버깅 로그 추가
            else:
                # 모든 선택 항목이 범위를 벗어나면 선택 목록 초기화
                self.selected_events = []
        
        # 녹화 중이면 주기적으로 업데이트
        if self.recorder.recording:
            self.update_timer = self.root.after(self.update_interval, self.update_event_list)
    
    def display_event(self, event, index):
        """이벤트를 리스트박스에 표시"""
        event_type = event.get('type', 'unknown')
        
        # 이벤트 타입에 따라 표시 방식 결정
        if event_type == 'keyboard':
            key = event.get('key', '')
            event_type_str = 'down' if event.get('event_type') == 'down' else 'up'
            display_str = f"{index+1:3d} {event.get('time', 0):.3f} K-{event_type_str.ljust(4)} {key}"
        elif event_type == 'mouse':
            button = event.get('button', '')
            event_type_str = event.get('event_type', '')
            pos_x, pos_y = event.get('position', (0, 0))
            
            # 랜덤 좌표 범위가 설정된 경우
            if 'position_range' in event:
                range_px = event.get('position_range', 0)
                display_str = f"{index+1:3d} {event.get('time', 0):.3f} M-{event_type_str.ljust(6)} {button} ({pos_x}, {pos_y}) ±{range_px}px"
            else:
                display_str = f"{index+1:3d} {event.get('time', 0):.3f} M-{event_type_str.ljust(6)} {button} ({pos_x}, {pos_y})"
        elif event_type == 'delay':
            delay_ms = int(event.get('delay', 0) * 1000)
            
            # 랜덤 범위가 설정된 경우
            if 'random_range' in event:
                range_ms = int(event.get('random_range', 0) * 1000)
                display_str = f"{index+1:3d} {event.get('time', 0):.3f} D 딜레이: {delay_ms}ms ±{range_ms}ms"
            else:
                display_str = f"{index+1:3d} {event.get('time', 0):.3f} D 딜레이: {delay_ms}ms"
        else:
            display_str = f"{index+1:3d} {event.get('time', 0):.3f} ? 알 수 없는 이벤트 타입: {event_type}"
        
        # 리스트박스에 추가
        self.event_listbox.insert(tk.END, display_str)
        
        # 특별한 이벤트에 색상 적용
        if event_type == 'delay':
            if 'random_range' in event:
                self.event_listbox.itemconfig(tk.END, {'bg': '#E6F9E6'})  # 랜덤 딜레이는 연한 녹색
            else:
                self.event_listbox.itemconfig(tk.END, {'bg': '#E6E6FF'})  # 일반 딜레이는 연한 파란색
        elif event_type == 'mouse':
            if 'position_range' in event:
                self.event_listbox.itemconfig(tk.END, {'bg': '#F9E6E6'})  # 랜덤 좌표는 연한 빨간색
    
    def delete_selected_event(self):
        """선택한 이벤트 삭제"""
        print("delete_selected_event 함수 호출됨")  # 디버깅 로그 추가
        # 녹화 중에는 편집 불가
        if self.recorder.recording:
            print("녹화 중 - 이벤트 삭제 불가")  # 디버깅 로그 추가
            messagebox.showwarning("경고", "녹화 중에는 이벤트를 편집할 수 없습니다.")
            return
            
        # 선택된 이벤트 확인 - 내부 변수 사용
        if not self.selected_events:
            # 리스트박스에서 직접 선택 확인
            selected = self.event_listbox.curselection()
            if not selected:
                messagebox.showwarning("경고", "삭제할 이벤트를 선택하세요.")
                return
            self.selected_events = list(selected)
            
        print(f"삭제할 이벤트: {self.selected_events}")  # 디버깅 로그 추가
        
        # 선택한 인덱스 목록
        selected_indices = self.selected_events
        print(f"삭제할 인덱스: {selected_indices}")  # 디버깅 로그 추가
        
        # 인덱스 유효성 확인
        events = []
        try:
            if hasattr(self.editor, 'get_events') and callable(self.editor.get_events):
                events = self.editor.get_events()
            elif hasattr(self.editor, 'events'):
                events = self.editor.events
        except Exception as e:
            print(f"이벤트 목록 가져오기 오류: {e}")
            events = []
            
        print(f"현재 이벤트 개수: {len(events)}")  # 디버깅 로그 추가
            
        # 유효하지 않은 인덱스 필터링 (삭제 대신)
        valid_indices = []
        for idx in selected_indices:
            if 0 <= idx < len(events):
                valid_indices.append(idx)
            else:
                print(f"유효하지 않은 인덱스 무시: {idx}")  # 디버깅 로그 추가
        
        if not valid_indices:
            print("유효한 인덱스가 없음")  # 디버깅 로그 추가
            messagebox.showwarning("경고", "선택한 이벤트 중 유효한 항목이 없습니다.")
            # 선택 초기화
            self.selected_events = []
            self.clear_selection()
            return
        
        # 여러 이벤트 삭제
        delete_result = False
        try:
            # delete_events 메서드가 있으면 사용
            if hasattr(self.editor, 'delete_events') and callable(self.editor.delete_events):
                print("editor.delete_events 메소드 사용")  # 디버깅 로그 추가
                delete_result = self.editor.delete_events(valid_indices)
            # events 속성 직접 접근 (대안 방법)
            elif hasattr(self.editor, 'events'):
                print("events 속성 직접 접근하여 삭제")  # 디버깅 로그 추가
                # 내림차순으로 정렬하여 인덱스 변화 방지
                sorted_indices = sorted(valid_indices, reverse=True)
                for idx in sorted_indices:
                    if 0 <= idx < len(self.editor.events):
                        print(f"이벤트 {idx} 삭제됨")  # 디버깅 로그 추가
                        del self.editor.events[idx]
                delete_result = True
            else:
                print("삭제 방법 없음")  # 디버깅 로그 추가
                messagebox.showerror("오류", "에디터가 이벤트 삭제를 지원하지 않습니다.")
                return
        except Exception as e:
            print(f"삭제 중 예외 발생: {e}")  # 디버깅 로그 추가
            import traceback
            traceback.print_exc()
            messagebox.showerror("오류", f"이벤트 삭제 중 오류가 발생했습니다: {e}")
            return
        
        if delete_result:
            print("이벤트 삭제 성공")  # 디버깅 로그 추가
            # 선택 해제
            self.clear_selection()
            
            # 이벤트 삭제 후 자동 로드를 방지하는 플래그 설정
            self.skip_auto_reload = True
            
            # 이벤트 목록 업데이트
            self.update_event_list()
            
            self.update_status(f"{len(valid_indices)}개 이벤트 삭제 완료")
        else:
            print("이벤트 삭제 실패")  # 디버깅 로그 추가
            messagebox.showerror("오류", "이벤트 삭제에 실패했습니다.")
    
    def add_delay_to_event(self):
        """이벤트 사이에 딜레이 추가"""
        print("add_delay_to_event 함수 호출됨")  # 디버깅 로그 추가
        # 녹화 중에는 편집 불가
        if self.recorder.recording:
            print("녹화 중 - 딜레이 추가 불가")  # 디버깅 로그 추가
            messagebox.showwarning("경고", "녹화 중에는 이벤트를 편집할 수 없습니다.")
            return
        
        # 선택한 이벤트 인덱스
        selected = self.event_listbox.curselection()
        print(f"선택된 이벤트: {selected}")  # 디버깅 로그 추가
        if not selected:
            messagebox.showwarning("경고", "딜레이를 추가할 위치를 선택하세요.")
            return
        
        # 이벤트 목록 가져오기
        events = []
        try:
            if hasattr(self.editor, 'get_events') and callable(self.editor.get_events):
                events = self.editor.get_events()
            elif hasattr(self.editor, 'events'):
                events = self.editor.events
        except Exception as e:
            print(f"이벤트 목록 가져오기 오류: {e}")
            events = []
            
        print(f"현재 이벤트 개수: {len(events)}")  # 디버깅 로그 추가
        
        # 전체 선택인지 확인
        is_all_selected = len(selected) > 1 and len(selected) == len(events)
        
        # 딜레이 값 입력 받기 (밀리초 단위)
        if is_all_selected:
            delay_time_ms = simpledialog.askinteger("모든 이벤트 사이에 딜레이 추가", 
                                                "추가할 딜레이 시간(ms):", 
                                                minvalue=10, maxvalue=60000)
        else:
            delay_time_ms = simpledialog.askinteger("딜레이 추가", 
                                                "추가할 딜레이 시간(ms):", 
                                                minvalue=10, maxvalue=60000)
                                                
        if not delay_time_ms:
            print("딜레이 시간 입력 취소")  # 디버깅 로그 추가
            return
            
        print(f"추가할 딜레이: {delay_time_ms}ms")  # 디버깅 로그 추가
        
        # 밀리초를 초 단위로 변환
        delay_time = delay_time_ms / 1000
        
        # 전체 선택인 경우, 모든 이벤트 사이에 딜레이 추가
        if is_all_selected:
            print("전체 선택 감지됨 - 모든 이벤트 사이에 딜레이 추가")  # 디버깅 로그 추가
            return self.add_delay_between_all_events(delay_time, delay_time_ms)
        
        # 인덱스 유효성 검사
        if selected[0] >= len(events):
            print(f"유효하지 않은 인덱스: {selected[0]}")  # 디버깅 로그 추가
            messagebox.showerror("오류", "선택한 위치가 유효하지 않습니다.")
            return
        
        # 일반적인 단일 위치에 딜레이 추가 처리
        # 선택한 이벤트 아래에 추가하기 위해 인덱스 + 1 위치에 삽입
        index = selected[0] + 1
        print(f"삽입 위치: {index}")  # 디버깅 로그 추가
        
        # 딜레이 이벤트 생성
        delay_event = {
            'type': 'delay',
            'delay': delay_time,
            'time': 0  # 시간은 나중에 설정됨
        }
        
        # 에디터에 이벤트 추가
        insert_result = False
        try:
            # insert_event 메서드가 있으면 사용
            if hasattr(self.editor, 'insert_event') and callable(self.editor.insert_event):
                print("editor.insert_event 메소드 사용")  # 디버깅 로그 추가
                insert_result = self.editor.insert_event(index, delay_event)
            # events 속성 직접 접근 (대안 방법)
            elif hasattr(self.editor, 'events'):
                print("events 속성 직접 접근하여 삽입")  # 디버깅 로그 추가
                # 이전 이벤트 시간 가져오기 (있다면)
                if index > 0 and index <= len(self.editor.events):
                    # 시간 정보가 있다면 설정
                    if 'time' in self.editor.events[index-1]:
                        delay_event['time'] = self.editor.events[index-1]['time'] + 0.001
                    
                # 삽입
                if index <= len(self.editor.events):
                    self.editor.events.insert(index, delay_event)
                    insert_result = True
                else:
                    print(f"삽입 위치 범위 초과: {index} (총 {len(self.editor.events)}개)")
            else:
                print("삽입 방법 없음")  # 디버깅 로그 추가
                messagebox.showerror("오류", "에디터가 이벤트 삽입을 지원하지 않습니다.")
                return
        except Exception as e:
            print(f"삽입 중 예외 발생: {e}")  # 디버깅 로그 추가
            import traceback
            traceback.print_exc()
            messagebox.showerror("오류", f"딜레이 추가 중 오류가 발생했습니다: {e}")
            return
        
        if insert_result:
            print("딜레이 이벤트 추가 성공")  # 디버깅 로그 추가
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
            print("딜레이 이벤트 추가 실패")  # 디버깅 로그 추가
            messagebox.showerror("오류", "딜레이 추가에 실패했습니다.")
            
    def add_delay_between_all_events(self, delay_time, delay_time_ms):
        """모든 이벤트 사이에 딜레이 추가"""
        print("add_delay_between_all_events 함수 호출됨")  # 디버깅 로그 추가
        
        # 이벤트 목록 가져오기
        events = []
        if hasattr(self.editor, 'get_events') and callable(self.editor.get_events):
            events = self.editor.get_events()
        elif hasattr(self.editor, 'events'):
            events = self.editor.events
            
        # 이미 존재하는 딜레이 이벤트를 제외한 위치 찾기
        insert_positions = []
        event_count = len(events)
        
        if event_count < 2:
            print("이벤트가 1개 이하라 딜레이를 추가할 위치가 없음")  # 디버깅 로그 추가
            messagebox.showinfo("알림", "딜레이를 추가할 이벤트 사이가 없습니다.")
            return False
        
        # 뒤에서부터 앞으로 처리 (인덱스 변화 방지)
        # 우선 추가할 위치를 모두 파악
        for i in range(event_count - 1, 0, -1):
            # 현재 위치에 딜레이 이벤트가 없는 경우만 추가
            if events[i-1]['type'] != 'delay' and events[i]['type'] != 'delay':
                insert_positions.append(i)
        
        print(f"딜레이 추가할 위치: {insert_positions}")  # 디버깅 로그 추가
        if not insert_positions:
            messagebox.showinfo("알림", "모든 이벤트 사이에 이미 딜레이가 있습니다.")
            return False
        
        # 딜레이 이벤트 템플릿
        delay_event_template = {
            'type': 'delay',
            'delay': delay_time,
            'time': 0
        }
        
        # 삽입 성공 여부
        insert_success = True
        inserted_count = 0
        
        # 직접 이벤트 삽입
        try:
            if hasattr(self.editor, 'events'):
                # 위치를 역순으로 정렬 (인덱스 변화 방지)
                for i in sorted(insert_positions, reverse=True):
                    # 딜레이 이벤트 복제
                    delay_event = delay_event_template.copy()
                    
                    # 이전 이벤트 시간이 있다면 설정
                    if 'time' in events[i-1]:
                        delay_event['time'] = events[i-1]['time'] + 0.001
                    
                    # 이벤트 삽입
                    self.editor.events.insert(i, delay_event)
                    inserted_count += 1
                
                insert_success = True
            else:
                # insert_event 메서드가 있는 경우
                for i in sorted(insert_positions, reverse=True):
                    delay_event = delay_event_template.copy()
                    if hasattr(self.editor, 'insert_event') and callable(self.editor.insert_event):
                        self.editor.insert_event(i, delay_event)
                        inserted_count += 1
                
                insert_success = True
        except Exception as e:
            print(f"일괄 딜레이 추가 중 오류 발생: {e}")  # 디버깅 로그 추가
            import traceback
            traceback.print_exc()
            messagebox.showerror("오류", f"이벤트 사이 딜레이 추가 중 오류가 발생했습니다: {e}")
            return False
        
        if insert_success:
            print(f"모든 이벤트 사이에 딜레이 추가 성공: {inserted_count}개")  # 디버깅 로그 추가
            # 선택 해제 및 저장
            self.restore_selection = False
            self.clear_selection()
            
            # 이벤트 목록 업데이트
            self.update_event_list()
            
            # 선택 복원 플래그 원복
            self.restore_selection = True
            
            self.update_status(f"모든 이벤트 사이에 {delay_time_ms}ms 딜레이 {inserted_count}개가 추가되었습니다.")
            return True
        else:
            print("이벤트 사이 딜레이 추가 실패")  # 디버깅 로그 추가
            messagebox.showerror("오류", "이벤트 사이 딜레이 추가에 실패했습니다.")
            return False
    
    def modify_delay_time(self):
        """선택한 딜레이 이벤트의 시간을 직접 수정"""
        print("modify_delay_time 함수 호출됨")  # 디버깅 로그 추가
        # 녹화 중에는 편집 불가
        if self.recorder.recording:
            print("녹화 중 - 딜레이 수정 불가")  # 디버깅 로그 추가
            messagebox.showwarning("경고", "녹화 중에는 이벤트를 편집할 수 없습니다.")
            return
            
        # 현재 리스트박스에서 선택된 항목 가져오기
        selected = self.event_listbox.curselection()
        print(f"선택된 이벤트: {selected}")  # 디버깅 로그 추가
        
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
                
        print(f"딜레이 이벤트 인덱스: {delay_indices}")  # 디버깅 로그 추가
        if not delay_indices:
            messagebox.showwarning("경고", "선택한 항목 중 딜레이 이벤트가 없습니다.")
            return
        
        # 딜레이 시간 직접 입력 받기 (밀리초 단위)
        new_delay_time_ms = simpledialog.askinteger("딜레이 시간 설정", "새 딜레이 시간(ms):", 
                                                  minvalue=10, maxvalue=60000)
        if not new_delay_time_ms:
            print("딜레이 시간 입력 취소")  # 디버깅 로그 추가
            return
            
        print(f"새 딜레이 시간: {new_delay_time_ms}ms")  # 디버깅 로그 추가
        # 밀리초를 초 단위로 변환
        new_delay_time = new_delay_time_ms / 1000
        
        # 선택된 딜레이 이벤트 시간 수정
        if self.editor.set_selected_delays_time(delay_indices, new_delay_time):
            print("딜레이 시간 수정 성공")  # 디버깅 로그 추가
            # 선택 저장
            self.selected_events = list(selected)
            
            # 이벤트 목록 업데이트
            self.update_event_list()
            
            msg = f"선택한 딜레이 이벤트({len(delay_indices)}개)의 시간이 {new_delay_time_ms}ms로 설정되었습니다."
            self.update_status(msg)
        else:
            print("딜레이 시간 수정 실패")  # 디버깅 로그 추가
            messagebox.showerror("오류", "딜레이 시간 수정에 실패했습니다.")
    
    def select_all_events(self):
        """모든 이벤트 선택"""
        print("select_all_events 함수 호출됨")  # 디버깅 로그 추가
        # 녹화 중에는 선택 불가
        if self.recorder.recording:
            print("녹화 중 - 전체 선택 불가")  # 디버깅 로그 추가
            return
            
        # 이벤트 목록 크기 가져오기
        event_count = self.event_listbox.size()
        print(f"이벤트 개수: {event_count}")  # 디버깅 로그 추가
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
        print(f"전체 선택 완료: {len(self.selected_events)}개")  # 디버깅 로그 추가
        
        # 메시지 박스 표시 대신 상태바만 업데이트
        self.update_status(f"모든 이벤트({event_count}개)가 선택되었습니다.")
            
    def move_event_up(self):
        """선택한 이벤트를 위로 이동"""
        print("move_event_up 함수 호출됨")  # 디버깅 로그 추가
        # 녹화 중에는 편집 불가
        if self.recorder.recording:
            print("녹화 중 - 이벤트 이동 불가")  # 디버깅 로그 추가
            messagebox.showwarning("경고", "녹화 중에는 이벤트를 편집할 수 없습니다.")
            return
            
        # 선택한 이벤트 인덱스
        selected = self.event_listbox.curselection()
        print(f"선택된 이벤트: {selected}")  # 디버깅 로그 추가
        if not selected or len(selected) != 1:
            messagebox.showwarning("경고", "위로 이동할 이벤트를 하나만 선택하세요.")
            return
            
        current_index = selected[0]
        print(f"현재 인덱스: {current_index}")  # 디버깅 로그 추가
            
        # 0번 인덱스는 더 이상 위로 이동할 수 없음
        if current_index <= 0:
            print("첫 번째 이벤트는 더 이상 위로 이동할 수 없음")  # 디버깅 로그 추가
            messagebox.showwarning("경고", "첫 번째 이벤트는 더 위로 이동할 수 없습니다.")
            return
            
        # 이벤트 개수 확인
        events = []
        if hasattr(self.editor, 'get_events') and callable(self.editor.get_events):
            events = self.editor.get_events()
        elif hasattr(self.editor, 'events'):
            events = self.editor.events
            
        print(f"현재 이벤트 개수: {len(events)}")  # 디버깅 로그 추가
        
        # 인덱스 유효성 검사
        if current_index >= len(events):
            print(f"유효하지 않은 인덱스: {current_index}")  # 디버깅 로그 추가
            messagebox.showerror("오류", "선택한 이벤트가 유효하지 않습니다.")
            return
            
        # 이벤트 위로 이동
        move_result = False
        try:
            # 메서드가 있으면 사용
            if hasattr(self.editor, 'move_event_up') and callable(self.editor.move_event_up):
                print("editor.move_event_up 메소드 사용")  # 디버깅 로그 추가
                move_result = self.editor.move_event_up(current_index)
            # events 속성 직접 접근 (대안 방법)
            elif hasattr(self.editor, 'events'):
                print("events 속성 직접 접근하여 이벤트 이동")  # 디버깅 로그 추가
                # 인덱스 유효성 확인
                if 0 < current_index < len(self.editor.events):
                    # 이벤트 교환
                    self.editor.events[current_index], self.editor.events[current_index-1] = (
                        self.editor.events[current_index-1], self.editor.events[current_index]
                    )
                    move_result = True
            else:
                print("이벤트 이동 방법 없음")  # 디버깅 로그 추가
                messagebox.showerror("오류", "에디터가 이벤트 이동을 지원하지 않습니다.")
                return
        except Exception as e:
            print(f"이동 중 예외 발생: {e}")  # 디버깅 로그 추가
            import traceback
            traceback.print_exc()
            messagebox.showerror("오류", f"이벤트 이동 중 오류가 발생했습니다: {e}")
            return
        
        if move_result:
            print(f"이벤트 위로 이동 성공: {current_index} -> {current_index-1}")  # 디버깅 로그 추가
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
            print("이벤트 위로 이동 실패")  # 디버깅 로그 추가
            messagebox.showwarning("경고", "이벤트를 더 위로 이동할 수 없습니다.")
            
    def move_event_down(self):
        """선택한 이벤트를 아래로 이동"""
        print("move_event_down 함수 호출됨")  # 디버깅 로그 추가
        # 녹화 중에는 편집 불가
        if self.recorder.recording:
            print("녹화 중 - 이벤트 이동 불가")  # 디버깅 로그 추가
            messagebox.showwarning("경고", "녹화 중에는 이벤트를 편집할 수 없습니다.")
            return
            
        # 선택한 이벤트 인덱스
        selected = self.event_listbox.curselection()
        print(f"선택된 이벤트: {selected}")  # 디버깅 로그 추가
        if not selected or len(selected) != 1:
            messagebox.showwarning("경고", "아래로 이동할 이벤트를 하나만 선택하세요.")
            return
            
        current_index = selected[0]
        print(f"현재 인덱스: {current_index}")  # 디버깅 로그 추가
            
        # 이벤트 개수 확인
        events = []
        if hasattr(self.editor, 'get_events') and callable(self.editor.get_events):
            events = self.editor.get_events()
        elif hasattr(self.editor, 'events'):
            events = self.editor.events
            
        print(f"현재 이벤트 개수: {len(events)}")  # 디버깅 로그 추가
        
        # 인덱스 유효성 검사
        if current_index >= len(events) - 1:
            print(f"마지막 이벤트는 더 이상 아래로 이동할 수 없음: {current_index}")  # 디버깅 로그 추가
            messagebox.showwarning("경고", "마지막 이벤트는 더 아래로 이동할 수 없습니다.")
            return
        
        # 이벤트 아래로 이동
        move_result = False
        try:
            # 메서드가 있으면 사용
            if hasattr(self.editor, 'move_event_down') and callable(self.editor.move_event_down):
                print("editor.move_event_down 메소드 사용")  # 디버깅 로그 추가
                move_result = self.editor.move_event_down(current_index)
            # events 속성 직접 접근 (대안 방법)
            elif hasattr(self.editor, 'events'):
                print("events 속성 직접 접근하여 이벤트 이동")  # 디버깅 로그 추가
                # 인덱스 유효성 확인
                if 0 <= current_index < len(self.editor.events) - 1:
                    # 이벤트 교환
                    self.editor.events[current_index], self.editor.events[current_index+1] = (
                        self.editor.events[current_index+1], self.editor.events[current_index]
                    )
                    move_result = True
            else:
                print("이벤트 이동 방법 없음")  # 디버깅 로그 추가
                messagebox.showerror("오류", "에디터가 이벤트 이동을 지원하지 않습니다.")
                return
        except Exception as e:
            print(f"이동 중 예외 발생: {e}")  # 디버깅 로그 추가
            import traceback
            traceback.print_exc()
            messagebox.showerror("오류", f"이벤트 이동 중 오류가 발생했습니다: {e}")
            return
        
        if move_result:
            print(f"이벤트 아래로 이동 성공: {current_index} -> {current_index+1}")  # 디버깅 로그 추가
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
            print("이벤트 아래로 이동 실패")  # 디버깅 로그 추가
            messagebox.showwarning("경고", "이벤트를 더 아래로 이동할 수 없습니다.")
    
    def on_event_select(self, event=None):
        """이벤트 리스트박스에서 항목 선택 시 호출되는 콜백"""
        # 전체 선택 처리중이면 무시
        if hasattr(self, '_skip_selection') and self._skip_selection:
            return
            
        # 녹화 중이면 무시
        if self.recorder.recording:
            return
            
        # 리스트에서 선택된 항목들 가져오기
        selected = self.event_listbox.curselection()
        if not selected:
            return
            
        print(f"이벤트 선택됨: {selected}")  # 디버깅 로그 추가
            
        # 선택된 항목들을 self.selected_events에 저장
        self.selected_events = list(selected)
        
        # 상태표시줄 업데이트
        if len(selected) == 1:
            idx = selected[0]
            # editor.get_events() 메서드를 사용하여 이벤트 리스트 가져오기
            events = self.editor.get_events()
            if events and idx < len(events):
                event_type = events[idx]['type']
                self.update_status(f"이벤트 #{idx+1} 선택됨 (유형: {event_type})")
            else:
                self.update_status(f"이벤트 #{idx+1} 선택됨")
        else:
            self.update_status(f"{len(selected)}개 이벤트 선택됨")
    
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
        
        # F9 키: 매크로 녹화 시작
        self.root.bind("<F9>", lambda event: self.start_recording_for_selected_gesture())
        
        # F10 키: 매크로 녹화 중지
        self.root.bind("<F10>", lambda event: self.stop_recording())
        
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
    
    def start_recording_for_selected_gesture(self):
        """선택된 제스처에 대해 매크로 녹화 시작"""
        # 선택된 제스처 확인
        selected = self.gesture_listbox.curselection()
        if not selected:
            messagebox.showwarning("선택 오류", "매크로를 녹화할 제스처를 선택하세요.")
            return
            
        # 제스처 이름 가져오기
        gesture = self.gesture_listbox.get(selected[0])
        
        # 현재 제스처 설정 (매크로 녹화 완료 후 저장에 사용)
        self.current_gesture = gesture
        
        # 매크로 녹화 시작
        self.start_recording()
        
        # 상태 업데이트
        self.update_status("제스처 녹화 중...")

    def on_gesture_select(self, event=None):
        """제스처 선택 시 이벤트 처리"""
        print("on_gesture_select 함수 호출됨")  # 디버깅 로그 추가
        
        # 선택 처리 스킵 플래그 확인
        if hasattr(self, '_skip_selection') and self._skip_selection:
            print("선택 처리 스킵됨 (_skip_selection 플래그)")  # 디버깅 로그 추가
            return
            
        # 현재 선택된 항목
        selected = self.gesture_listbox.curselection()
        print(f"선택된 항목: {selected}")  # 디버깅 로그 추가
        
        if not selected:
            print("선택된 항목 없음")  # 디버깅 로그 추가
            self.selected_gesture_index = None
            self.selected_gesture_name = None
            return
            
        # 선택된 첫 번째 항목의 인덱스와 텍스트
        selected_index = selected[0]
        selected_text = self.gesture_listbox.get(selected_index)
        
        print(f"선택된 항목: {selected_index}, 텍스트: {selected_text}")  # 디버깅 로그 추가
        
        # 이전에 선택했던 제스처 확인
        previous_selected_gesture = self.selected_gesture_name
        
        # 모디파이어 변환 고려 - UI에 표시된 이름과 실제 매핑 이름 일치시키기
        # 여기서는 매핑에서 실제 제스처 이름 찾기
        actual_gesture_name = None
        
        # 매핑 목록에서 찾기 (표시 이름과 실제 이름이 다를 수 있음)
        for gesture in self.gesture_manager.get_mappings().keys():
            # UI에 표시될 이름 생성
            display_name = gesture
            display_name = display_name.replace("A-", "Alt-").replace("AT", "Alt")
            display_name = display_name.replace("CT", "Ctrl")
            
            if display_name == selected_text:
                actual_gesture_name = gesture
                break
        
        # 찾지 못한 경우 UI에 표시된 이름 그대로 사용
        if not actual_gesture_name:
            actual_gesture_name = selected_text
        
        # 이전 선택과 현재 선택이 같은 경우 중복 처리 방지
        if previous_selected_gesture == actual_gesture_name:
            print(f"같은 제스처({actual_gesture_name})가 다시 선택됨 - 처리 스킵")  # 디버깅 로그 추가
            return
        
        # 상태 저장
        self.selected_gesture_index = selected_index
        self.selected_gesture_name = actual_gesture_name
        
        print(f"선택된 제스처: {self.selected_gesture_name}")  # 디버깅 로그 추가
        
        # 선택된 이벤트 초기화 (제스처 변경 시 이전 선택된 이벤트 인덱스가 유효하지 않을 수 있음)
        self.selected_events = []
        self.clear_selection()
        
        # editor의 이벤트 초기화 (이전 제스처의 이벤트가 남아있는 것 방지)
        if hasattr(self.editor, 'events'):
            self.editor.events = []
        
        # 선택된 제스처의 이벤트 목록 업데이트
        self.update_event_list_for_gesture(self.selected_gesture_name)

    def maintain_gesture_selection(self, event):
        """포커스가 사라져도 선택 유지"""
        print("maintain_gesture_selection 함수 호출됨")  # 디버깅 로그 추가
        # 현재 선택 저장
        current_selection = self.gesture_listbox.curselection()
        
        # 선택 제거 방지
        if current_selection:
            try:
                # 현재 선택 정보 저장
                selection_indices = list(current_selection)
                
                # 선택 유지를 위해 먼저 모든 선택 해제
                self.gesture_listbox.selection_clear(0, tk.END)
                
                # 저장된 선택 복원
                for idx in selection_indices:
                    self.gesture_listbox.selection_set(idx)
                    
                print(f"선택 유지: {selection_indices}")  # 디버깅 로그 추가
            except Exception as e:
                print(f"선택 유지 중 오류: {e}")  # 디버깅 로그 추가
        # 선택이 없지만 내부 변수에 선택 정보가 있는 경우
        elif self.selected_gesture_index is not None:
            try:
                self.gesture_listbox.selection_set(self.selected_gesture_index)
                print(f"선택 복원: {self.selected_gesture_index}")  # 디버깅 로그 추가
            except Exception as e:
                print(f"선택 복원 중 오류: {e}")  # 디버깅 로그 추가
    
    def ensure_gesture_selection(self):
        """제스처 선택이 유지되도록 함"""
        # 현재 선택 확인
        current_selection = self.gesture_listbox.curselection()
        
        # 선택된 항목이 없고 내부 변수에 선택 정보가 있는 경우
        if not current_selection and self.selected_gesture_index is not None:
            try:
                # 이전 선택 복원
                if self.selected_gesture_index < self.gesture_listbox.size():
                    self.gesture_listbox.selection_clear(0, tk.END)
                    self.gesture_listbox.selection_set(self.selected_gesture_index)
                    print(f"선택 복원: {self.selected_gesture_index}")  # 디버깅 로그 추가
            except Exception as e:
                print(f"선택 보장 중 오류: {e}")  # 디버깅 로그 추가
        # 선택된 항목이 있고 내부 변수와 다른 경우 내부 변수 업데이트
        elif current_selection and (not self.selected_gesture_index or current_selection[0] != self.selected_gesture_index):
            try:
                # 첫 번째 선택 항목으로 내부 변수 업데이트
                self.selected_gesture_index = current_selection[0]
                self.selected_gesture_name = self.gesture_listbox.get(current_selection[0])
                print(f"선택 정보 업데이트: {self.selected_gesture_name}")  # 디버깅 로그 추가
            except Exception as e:
                print(f"선택 정보 업데이트 중 오류: {e}")  # 디버깅 로그 추가

    def move_gesture_up(self):
        """선택한 제스처를 위로 이동"""
        print("move_gesture_up 함수 호출됨")  # 디버깅 로그 추가
        # 제스처 매니저가 없으면 무시
        if not self.gesture_manager:
            print("제스처 매니저 없음")  # 디버깅 로그 추가
            return
            
        # 선택한 제스처 인덱스
        selected = self.gesture_listbox.curselection()
        print(f"선택된 제스처: {selected}")  # 디버깅 로그 추가
        if not selected:
            messagebox.showwarning("경고", "위로 이동할 제스처를 선택하세요.")
            return
            
        current_index = selected[0]
        print(f"현재 인덱스: {current_index}")  # 디버깅 로그 추가
            
        # 0번 인덱스는 더 이상 위로 이동할 수 없음
        if current_index <= 0:
            print("첫 번째 제스처는 더 이상 위로 이동할 수 없음")  # 디버깅 로그 추가
            messagebox.showwarning("경고", "첫 번째 제스처는 더 위로 이동할 수 없습니다.")
            return
            
        # 제스처 목록 가져오기
        gestures = list(self.gesture_manager.gesture_mappings.keys())
        
        # 인덱스 유효성 검사
        if current_index >= len(gestures):
            print(f"유효하지 않은 인덱스: {current_index}")  # 디버깅 로그 추가
            messagebox.showerror("오류", "선택한 제스처가 유효하지 않습니다.")
            return
            
        # 현재 제스처와 이전 제스처 가져오기
        current_gesture = gestures[current_index]
        prev_gesture = gestures[current_index - 1]
        
        try:
            # 제스처 매핑에서 직접 순서 변경
            # 원래 목록에서 제스처 제거
            gestures.pop(current_index)
            # 이전 위치에 삽입
            gestures.insert(current_index - 1, current_gesture)
            
            # 새로운 매핑 생성
            new_mappings = {}
            for gesture in gestures:
                new_mappings[gesture] = self.gesture_manager.gesture_mappings[gesture]
            
            # 새 매핑으로 교체
            self.gesture_manager.gesture_mappings = new_mappings
            
            # 제스처 매핑 저장
            self.gesture_manager.save_mappings()
            
            print(f"제스처 위치 변경됨: {current_gesture}를 위로 이동")  # 디버깅 로그 추가
            
            # 선택된 제스처 이름 저장
            self.selected_gesture_name = current_gesture
            
            # 제스처 목록 업데이트
            self.update_gesture_list()
            
            # 이동된 제스처 선택 (새 위치)
            new_index = current_index - 1
            self.gesture_listbox.selection_clear(0, tk.END)  # 모든 선택 해제
            self.gesture_listbox.selection_set(new_index)  # 새 위치 선택
            self.gesture_listbox.see(new_index)  # 해당 위치로 스크롤
            self.selected_gesture_index = new_index
            
            # 선택된 이벤트 초기화 (제스처 변경 시 이전 선택된 이벤트 인덱스가 유효하지 않을 수 있음)
            self.selected_events = []
            self.clear_selection()
            
            # 이벤트 목록 갱신 추가
            self.update_event_list_for_gesture(current_gesture)
            
            self.update_status(f"제스처 '{current_gesture}'가 위로 이동되었습니다.")
        except Exception as e:
            print(f"제스처 이동 중 오류 발생: {e}")  # 디버깅 로그 추가
            messagebox.showerror("오류", f"제스처 이동 중 오류가 발생했습니다: {e}")
    
    def move_gesture_down(self):
        """선택한 제스처를 아래로 이동"""
        print("move_gesture_down 함수 호출됨")  # 디버깅 로그 추가
        # 제스처 매니저가 없으면 무시
        if not self.gesture_manager:
            print("제스처 매니저 없음")  # 디버깅 로그 추가
            return
            
        # 선택한 제스처 인덱스
        selected = self.gesture_listbox.curselection()
        print(f"선택된 제스처: {selected}")  # 디버깅 로그 추가
        if not selected:
            messagebox.showwarning("경고", "아래로 이동할 제스처를 선택하세요.")
            return
            
        current_index = selected[0]
        print(f"현재 인덱스: {current_index}")  # 디버깅 로그 추가
            
        # 제스처 목록 가져오기
        gestures = list(self.gesture_manager.gesture_mappings.keys())
        
        # 마지막 항목은 더 이상 아래로 이동할 수 없음
        if current_index >= len(gestures) - 1:
            print("마지막 제스처는 더 이상 아래로 이동할 수 없음")  # 디버깅 로그 추가
            messagebox.showwarning("경고", "마지막 제스처는 더 아래로 이동할 수 없습니다.")
            return
            
        # 인덱스 유효성 검사
        if current_index >= len(gestures):
            print(f"유효하지 않은 인덱스: {current_index}")  # 디버깅 로그 추가
            messagebox.showerror("오류", "선택한 제스처가 유효하지 않습니다.")
            return
            
        # 현재 제스처와 다음 제스처 가져오기
        current_gesture = gestures[current_index]
        next_gesture = gestures[current_index + 1]
        
        try:
            # 제스처 매핑에서 직접 순서 변경
            # 원래 목록에서 제스처 제거
            gestures.pop(current_index)
            # 다음 위치에 삽입
            gestures.insert(current_index + 1, current_gesture)
            
            # 새로운 매핑 생성
            new_mappings = {}
            for gesture in gestures:
                new_mappings[gesture] = self.gesture_manager.gesture_mappings[gesture]
            
            # 새 매핑으로 교체
            self.gesture_manager.gesture_mappings = new_mappings
            
            # 제스처 매핑 저장
            self.gesture_manager.save_mappings()
            
            print(f"제스처 위치 변경됨: {current_gesture}를 아래로 이동")  # 디버깅 로그 추가
            
            # 선택된 제스처 이름 저장
            self.selected_gesture_name = current_gesture
            
            # 제스처 목록 업데이트
            self.update_gesture_list()
            
            # 이동된 제스처 선택 (새 위치)
            new_index = current_index + 1
            self.gesture_listbox.selection_clear(0, tk.END)  # 모든 선택 해제
            self.gesture_listbox.selection_set(new_index)  # 새 위치 선택
            self.gesture_listbox.see(new_index)  # 해당 위치로 스크롤
            self.selected_gesture_index = new_index
            
            # 선택된 이벤트 초기화 (제스처 변경 시 이전 선택된 이벤트 인덱스가 유효하지 않을 수 있음)
            self.selected_events = []
            self.clear_selection()
            
            # 이벤트 목록 갱신 추가
            self.update_event_list_for_gesture(current_gesture)
            
            self.update_status(f"제스처 '{current_gesture}'가 아래로 이동되었습니다.")
        except Exception as e:
            print(f"제스처 이동 중 오류 발생: {e}")  # 디버깅 로그 추가
            messagebox.showerror("오류", f"제스처 이동 중 오류가 발생했습니다: {e}")

    def update_event_list_for_gesture(self, gesture_name):
        """선택된 제스처에 대한 이벤트 목록 업데이트"""
        print(f"update_event_list_for_gesture 함수 호출: {gesture_name}")  # 디버깅 로그 추가
        
        if not self.gesture_manager or not gesture_name:
            return
            
        # 제스처에 대한 매크로 파일 경로 가져오기
        if gesture_name in self.gesture_manager.gesture_mappings:
            macro_name = self.gesture_manager.gesture_mappings[gesture_name]
            full_path = os.path.join("macros", macro_name)
            print(f"매크로 파일 경로 시도: {full_path}")  # 디버깅 로그 추가
            
            # 파일이 존재하는지 확인
            if not os.path.exists(full_path):
                print(f"파일이 존재하지 않음, 대체 경로 시도")  # 디버깅 로그 추가
                # 대체 경로 시도
                safe_gesture = gesture_name.replace('→', '_RIGHT_').replace('↓', '_DOWN_').replace('←', '_LEFT_').replace('↑', '_UP_')
                alternative_path = os.path.join("macros", f"gesture_{safe_gesture}.json")
                print(f"대체 경로: {alternative_path}")  # 디버깅 로그 추가
                
                if os.path.exists(alternative_path):
                    full_path = alternative_path
                    macro_name = f"gesture_{safe_gesture}.json"  # 매크로 이름 업데이트
                    print(f"대체 경로 파일 존재함: {full_path}")  # 디버깅 로그 추가
                else:
                    print(f"매크로 파일을 찾을 수 없음: {macro_name} / {alternative_path}")  # 디버깅 로그 추가
                    
                    # 매크로 매핑이 존재하지만 파일이 없는 경우, 경고 표시
                    warning_message = f"제스처 '{gesture_name}'의 매크로 파일을 찾을 수 없습니다."
                    self.update_status(warning_message)
                    
                    # 이벤트 목록 초기화
                    self.event_listbox.delete(0, tk.END)
                    self.event_listbox.insert(tk.END, "♦ 매크로 파일이 없습니다. '저장' 버튼으로 새 매크로를 저장하세요.")
                    self.event_listbox.itemconfig(tk.END, {'bg': '#FFE0E0'})
                    
                    # editor의 현재 편집 중인 매크로 이름 업데이트
                    if hasattr(self.editor, 'set_current_macro') and callable(self.editor.set_current_macro):
                        self.editor.set_current_macro(macro_name)
                    
                    return
            else:
                print(f"원래 경로 파일 존재함: {full_path}")  # 디버깅 로그 추가
            
            try:
                # 매크로 파일 읽기 - UTF-8 인코딩 사용
                with open(full_path, 'r', encoding='utf-8') as f:
                    import json
                    events = json.load(f)
                
                print(f"매크로 파일 내용 로드됨: {len(events)}개 이벤트")  # 디버깅 로그 추가
                
                # 임시 파일이고 이벤트가 없는 경우 특별 처리
                if "_temp.json" in macro_name and len(events) == 0:
                    print("임시 파일이고 이벤트가 없음 - 특별 메시지 표시")
                    
                    # 이벤트 목록 업데이트
                    self.event_listbox.delete(0, tk.END)  # 기존 이벤트 목록 초기화
                    self.event_listbox.insert(tk.END, "♦ 이 제스처에는 아직 이벤트가 없습니다.")
                    self.event_listbox.insert(tk.END, "♦ 매크로를 녹화하려면 '매크로 녹화 시작' 버튼을 클릭하고,")
                    self.event_listbox.insert(tk.END, "♦ 녹화 후 '녹화 중지' 버튼을 클릭하세요.")
                    
                    for i in range(3):
                        self.event_listbox.itemconfig(i, {'bg': '#FFFFD0'})
                        
                    # 상태 업데이트
                    self.update_status(f"제스처 '{gesture_name}'에 연결된 매크로가 비어있습니다. 새 매크로를 녹화하세요.")
                    
                    # 에디터에 빈 이벤트 목록 설정
                    if hasattr(self.editor, 'events'):
                        self.editor.events = []
                    
                    # editor의 현재 편집 중인 매크로 이름 업데이트
                    if hasattr(self.editor, 'set_current_macro') and callable(self.editor.set_current_macro):
                        self.editor.set_current_macro(macro_name)
                    
                    return
                
                # 에디터에 이벤트 설정
                if hasattr(self.editor, 'events'):
                    print("editor.events에 직접 할당")  # 디버깅 로그 추가
                    import copy
                    self.editor.events = copy.deepcopy(events)
                else:
                    print("에디터에 이벤트를 설정할 방법이 없음")  # 디버깅 로그 추가
                    self.update_status(f"에디터에 이벤트를 로드할 수 없습니다.")
                    return
                
                # editor의 현재 편집 중인 매크로 이름 업데이트
                if hasattr(self.editor, 'set_current_macro') and callable(self.editor.set_current_macro):
                    self.editor.set_current_macro(macro_name)
                    print(f"editor의 현재 편집 중인 매크로 이름 업데이트: {macro_name}")  # 디버깅 로그 추가
                
                # 이벤트 목록 업데이트
                self.event_listbox.delete(0, tk.END)  # 기존 이벤트 목록 초기화
                
                # 이벤트 표시
                for i, event in enumerate(events):
                    self.display_event(event, i)
                
                # 이벤트가 있으면 첫 번째 항목으로 스크롤
                if len(events) > 0:
                    self.event_listbox.see(0)
                
                print(f"제스처 '{gesture_name}'의 이벤트 {len(events)}개 로드됨")  # 디버깅 로그 추가
                
                # 상태 업데이트
                if len(events) == 0:
                    self.update_status(f"제스처 '{gesture_name}'에 연결된 매크로가 비어있습니다.")
                else:
                    self.update_status(f"제스처 '{gesture_name}'의 이벤트 {len(events)}개 로드됨")
            except Exception as e:
                print(f"제스처 이벤트 로드 중 오류: {e}")  # 디버깅 로그 추가
                import traceback
                traceback.print_exc()
                self.update_status(f"매크로 로드 중 오류가 발생했습니다: {e}")
                
                # 오류 발생 시 이벤트 목록에 오류 메시지 표시
                self.event_listbox.delete(0, tk.END)
                self.event_listbox.insert(tk.END, f"♦ 매크로 파일 로드 중 오류 발생: {e}")
                self.event_listbox.itemconfig(tk.END, {'bg': '#FFD0D0'})
        else:
            print(f"제스처 '{gesture_name}'에 대한 매핑이 없음")  # 디버깅 로그 추가
            self.update_status(f"제스처 '{gesture_name}'에 대한 매크로 매핑이 없습니다.")

    def delete_delay_events(self):
        """선택된 이벤트 중 딜레이 이벤트만 삭제"""
        print("delete_delay_events 함수 호출됨")  # 디버깅 로그 추가
        # 녹화 중에는 편집 불가
        if self.recorder.recording:
            print("녹화 중 - 딜레이 삭제 불가")  # 디버깅 로그 추가
            messagebox.showwarning("경고", "녹화 중에는 이벤트를 편집할 수 없습니다.")
            return
            
        # 선택한 이벤트 인덱스
        selected = self.event_listbox.curselection()
        print(f"선택된 이벤트: {selected}")  # 디버깅 로그 추가
        if not selected:
            messagebox.showwarning("경고", "삭제할 이벤트를 선택하세요.")
            return
            
        # 이벤트 목록 가져오기
        events = []
        if hasattr(self.editor, 'get_events') and callable(self.editor.get_events):
            events = self.editor.get_events()
        elif hasattr(self.editor, 'events'):
            events = self.editor.events
        else:
            print("이벤트를 가져올 수 없음")  # 디버깅 로그 추가
            messagebox.showerror("오류", "이벤트 목록을 가져올 수 없습니다.")
            return
            
        # 선택된 이벤트 중 딜레이 이벤트의 인덱스만 추출
        delay_indices = []
        for idx in selected:
            if idx < len(events) and events[idx]['type'] == 'delay':
                delay_indices.append(idx)
                
        print(f"삭제할 딜레이 이벤트 인덱스: {delay_indices}")  # 디버깅 로그 추가
        
        if not delay_indices:
            messagebox.showinfo("알림", "선택한 항목 중 딜레이 이벤트가 없습니다.")
            return
            
        # 확인 메시지
        confirm = messagebox.askyesno("딜레이 삭제 확인", 
                                    f"선택한 항목 중 딜레이 이벤트 {len(delay_indices)}개를 삭제하시겠습니까?")
        if not confirm:
            return
            
        # 삭제 실행
        delete_result = False
        try:
            # 내림차순으로 정렬하여 인덱스 변화 방지
            sorted_indices = sorted(delay_indices, reverse=True)
            
            # delete_events 메서드가 있으면 사용
            if hasattr(self.editor, 'delete_events') and callable(self.editor.delete_events):
                print("editor.delete_events 메소드 사용")  # 디버깅 로그 추가
                delete_result = self.editor.delete_events(sorted_indices)
            # events 속성 직접 접근 (대안 방법)
            elif hasattr(self.editor, 'events'):
                print("events 속성 직접 접근하여 삭제")  # 디버깅 로그 추가
                for idx in sorted_indices:
                    if 0 <= idx < len(self.editor.events):
                        del self.editor.events[idx]
                delete_result = True
            else:
                print("삭제 방법 없음")  # 디버깅 로그 추가
                messagebox.showerror("오류", "에디터가 이벤트 삭제를 지원하지 않습니다.")
                return
        except Exception as e:
            print(f"딜레이 삭제 중 예외 발생: {e}")  # 디버깅 로그 추가
            import traceback
            traceback.print_exc()
            messagebox.showerror("오류", f"딜레이 이벤트 삭제 중 오류가 발생했습니다: {e}")
            return
            
        if delete_result:
            print("딜레이 이벤트 삭제 성공")  # 디버깅 로그 추가
            # 선택 해제
            self.clear_selection()
            
            # 이벤트 삭제 후 자동 로드를 방지하는 플래그 설정
            self.skip_auto_reload = True
            
            # 이벤트 목록 업데이트
            self.update_event_list()
            
            self.update_status(f"딜레이 이벤트 {len(delay_indices)}개가 삭제되었습니다.")
        else:
            print("딜레이 이벤트 삭제 실패")  # 디버깅 로그 추가
            messagebox.showerror("오류", "딜레이 이벤트 삭제에 실패했습니다.")

    def on_event_double_click(self, event):
        """이벤트 항목 더블 클릭 시 처리"""
        print("더블 클릭 이벤트 발생")  # 디버깅 로그 추가
        # 녹화 중에는 무시
        if self.recorder.recording:
            return
            
        # 선택된 항목 가져오기
        selected = self.event_listbox.curselection()
        if not selected:
            return
            
        # 단일 항목만 처리
        if len(selected) == 1:
            index = selected[0]
            events = self.editor.get_events()
            if events and index < len(events):
                event_type = events[index]['type']
                
                if event_type == 'delay':
                    # 딜레이 이벤트면 수정 다이얼로그 표시
                    print(f"딜레이 이벤트 더블 클릭: {index}")  # 디버깅 로그 추가
                    self.modify_delay_time()
                else:
                    print(f"일반 이벤트 더블 클릭: {index}")  # 디버깅 로그 추가
                    # 일반 이벤트에 대한 정보 표시
                    messagebox.showinfo("이벤트 정보", f"이벤트 #{index+1}\n유형: {event_type}")

    def add_random_delay(self):
        """선택한 딜레이 이벤트에 랜덤 범위 추가"""
        print("add_random_delay 함수 호출됨")  # 디버깅 로그 추가
        # 녹화 중에는 편집 불가
        if self.recorder.recording:
            print("녹화 중 - 랜덤 딜레이 추가 불가")  # 디버깅 로그 추가
            messagebox.showwarning("경고", "녹화 중에는 이벤트를 편집할 수 없습니다.")
            return
        
        # 현재 리스트박스에서 선택된 항목 가져오기
        selected = self.event_listbox.curselection()
        print(f"선택된 이벤트: {selected}")  # 디버깅 로그 추가
        
        # 선택된 항목이 없으면 경고
        if not selected:
            messagebox.showwarning("경고", "랜덤 딜레이를 추가할 딜레이 이벤트를 선택하세요.")
            return
        
        # 선택된 이벤트가 딜레이 이벤트인지 확인
        events = self.editor.get_events()
        delay_indices = []
        
        # 선택된 항목 중 딜레이 이벤트만 찾기
        for idx in selected:
            if idx < len(events) and events[idx]['type'] == 'delay':
                delay_indices.append(idx)
        
        print(f"딜레이 이벤트 인덱스: {delay_indices}")  # 디버깅 로그 추가
        if not delay_indices:
            messagebox.showwarning("경고", "선택한 항목 중 딜레이 이벤트가 없습니다.")
            return
        
        # 랜덤 범위 값 입력 받기 (밀리초 단위)
        random_range_ms = simpledialog.askinteger("랜덤 딜레이 범위 설정", 
                                                "랜덤 범위 ±(ms):", 
                                                minvalue=10, maxvalue=10000)
        if not random_range_ms:
            print("랜덤 범위 입력 취소")  # 디버깅 로그 추가
            return
        
        print(f"랜덤 범위: ±{random_range_ms}ms")  # 디버깅 로그 추가
        
        # 성공 여부
        update_success = True
        
        try:
            # 선택된 딜레이 이벤트에 랜덤 범위 추가
            for idx in delay_indices:
                # 기존 딜레이 값 가져오기
                event = events[idx]
                base_delay = event['delay']
                
                # 랜덤 범위 추가
                event['random_range'] = random_range_ms / 1000  # 초 단위로 변환
                
                # 이벤트 업데이트
                if hasattr(self.editor, 'events'):
                    self.editor.events[idx] = event
                
                print(f"딜레이 이벤트 {idx}에 랜덤 범위 ±{random_range_ms}ms 추가됨")  # 디버깅 로그 추가
        except Exception as e:
            print(f"랜덤 딜레이 추가 중 오류 발생: {e}")  # 디버깅 로그 추가
            import traceback
            traceback.print_exc()
            messagebox.showerror("오류", f"랜덤 딜레이 추가 중 오류가 발생했습니다: {e}")
            update_success = False
        
        if update_success:
            # 선택 저장
            self.selected_events = list(selected)
            
            # 이벤트 목록 업데이트
            self.update_event_list()
            
            msg = f"선택한 딜레이 이벤트({len(delay_indices)}개)에 랜덤 범위 ±{random_range_ms}ms가 추가되었습니다."
            self.update_status(msg)
        else:
            print("랜덤 딜레이 추가 실패")  # 디버깅 로그 추가
            messagebox.showerror("오류", "랜덤 딜레이 추가에 실패했습니다.")

    def add_random_position(self):
        """선택한 마우스 이벤트에 랜덤 좌표 범위 추가"""
        print("add_random_position 함수 호출됨")  # 디버깅 로그 추가
        # 녹화 중에는 편집 불가
        if self.recorder.recording:
            print("녹화 중 - 랜덤 좌표 추가 불가")  # 디버깅 로그 추가
            messagebox.showwarning("경고", "녹화 중에는 이벤트를 편집할 수 없습니다.")
            return
        
        # 현재 리스트박스에서 선택된 항목 가져오기
        selected = self.event_listbox.curselection()
        print(f"선택된 이벤트: {selected}")  # 디버깅 로그 추가
        
        # 선택된 항목이 없으면 경고
        if not selected:
            messagebox.showwarning("경고", "랜덤 좌표를 추가할 마우스 이벤트를 선택하세요.")
            return
        
        # 선택된 이벤트가 마우스 이벤트인지 확인
        events = self.editor.get_events()
        mouse_indices = []
        
        # 선택된 항목 중 마우스 이벤트만 찾기
        for idx in selected:
            if idx < len(events) and events[idx]['type'] == 'mouse':
                mouse_indices.append(idx)
        
        print(f"마우스 이벤트 인덱스: {mouse_indices}")  # 디버깅 로그 추가
        if not mouse_indices:
            messagebox.showwarning("경고", "선택한 항목 중 마우스 이벤트가 없습니다.")
            return
        
        # 랜덤 범위 값 입력 받기 (픽셀 단위)
        random_range_px = simpledialog.askinteger("랜덤 좌표 범위 설정", 
                                                "랜덤 범위 ±(px):", 
                                                minvalue=1, maxvalue=100)
        if not random_range_px:
            print("랜덤 범위 입력 취소")  # 디버깅 로그 추가
            return
        
        print(f"랜덤 범위: ±{random_range_px}px")  # 디버깅 로그 추가
        
        # 성공 여부
        update_success = True
        
        try:
            # 선택된 마우스 이벤트에 랜덤 범위 추가
            for idx in mouse_indices:
                # 기존 마우스 이벤트 가져오기
                event = events[idx]
                
                # 랜덤 범위 추가
                event['position_range'] = random_range_px
                
                # 이벤트 업데이트
                if hasattr(self.editor, 'events'):
                    self.editor.events[idx] = event
                
                print(f"마우스 이벤트 {idx}에 랜덤 좌표 범위 ±{random_range_px}px 추가됨")  # 디버깅 로그 추가
        except Exception as e:
            print(f"랜덤 좌표 추가 중 오류 발생: {e}")  # 디버깅 로그 추가
            import traceback
            traceback.print_exc()
            messagebox.showerror("오류", f"랜덤 좌표 추가 중 오류가 발생했습니다: {e}")
            update_success = False
        
        if update_success:
            # 선택 저장
            self.selected_events = list(selected)
            
            # 이벤트 목록 업데이트
            self.update_event_list()
            
            msg = f"선택한 마우스 이벤트({len(mouse_indices)}개)에 랜덤 좌표 범위 ±{random_range_px}px가 추가되었습니다."
            self.update_status(msg)
        else:
            print("랜덤 좌표 추가 실패")  # 디버깅 로그 추가
            messagebox.showerror("오류", "랜덤 좌표 추가에 실패했습니다.")

    def start_gesture_recognition(self):
        """제스처 인식 시작"""
        if not self.gesture_manager:
            return
            
        self.gesture_enabled.set(True)
        self.gesture_manager.start()
        self.update_status("제스처 인식이 활성화되었습니다.")
        
        # 버튼 상태 업데이트
        self.gesture_start_btn.config(state=tk.DISABLED)
        self.gesture_stop_btn.config(state=tk.NORMAL)

    def stop_gesture_recognition(self):
        """제스처 인식 중지"""
        if not self.gesture_manager:
            return
            
        self.gesture_enabled.set(False)
        self.gesture_manager.stop()
        self.update_status("제스처 인식이 비활성화되었습니다.")
        
        # 버튼 상태 업데이트
        self.gesture_start_btn.config(state=tk.NORMAL)
        self.gesture_stop_btn.config(state=tk.DISABLED)

    def delete_selected_gesture(self):
        """선택된 제스처 삭제"""
        # 선택된 모든 항목의 인덱스 가져오기 (역순으로 정렬)
        selected_indices = list(self.gesture_listbox.curselection())
        selected_indices.sort(reverse=True)  # 역순으로 정렬하여 삭제 시 인덱스 변화 방지
        
        if not selected_indices:
            messagebox.showwarning("경고", "삭제할 제스처를 선택해주세요.")
            return
            
        # 선택된 모든 제스처 삭제
        deleted_count = 0
        for index in selected_indices:
            gesture_name = self.gesture_listbox.get(index)
            if gesture_name in self.gesture_manager.gesture_mappings:
                self.gesture_manager.remove_mapping(gesture_name)
                deleted_count += 1
        
        # 선택 초기화
        self.selected_gesture_index = None
        self.selected_gesture_name = None
        
        # 이벤트 목록 초기화
        self.event_listbox.delete(0, tk.END)
        
        # 제스처 목록 전체 새로고침
        self.update_gesture_list()
        
        # 삭제 결과 메시지
        self.update_status(f"{deleted_count}개의 제스처가 삭제되었습니다.")

    def toggle_absolute_coords(self):
        """절대좌표 체크박스 토글 시 호출"""
        print(f"toggle_absolute_coords 호출됨: 절대좌표={self.use_absolute_coords.get()}")
        if self.use_absolute_coords.get():
            # 절대좌표가 선택되면 상대좌표 해제
            self.use_relative_coords.set(False)
        else:
            # 절대좌표가 해제되면 상대좌표 선택
            self.use_relative_coords.set(True)
        
        # 레코더 설정 업데이트
        self.recorder.use_relative_coords = self.use_relative_coords.get()
        
        # 상태 메시지 업데이트
        coords_type = "상대좌표" if self.use_relative_coords.get() else "절대좌표"
        print(f"최종 좌표 타입 설정: {coords_type}")
        self.update_status(f"좌표 타입이 {coords_type}로 설정되었습니다.")

    def toggle_relative_coords(self):
        """상대좌표 체크박스 토글 시 호출"""
        print(f"toggle_relative_coords 호출됨: 상대좌표={self.use_relative_coords.get()}")
        if self.use_relative_coords.get():
            # 상대좌표가 선택되면 절대좌표 해제
            self.use_absolute_coords.set(False)
        else:
            # 상대좌표가 해제되면 절대좌표 선택
            self.use_absolute_coords.set(True)
        
        # 레코더 설정 업데이트
        self.recorder.use_relative_coords = self.use_relative_coords.get()
        
        # 상태 메시지 업데이트
        coords_type = "상대좌표" if self.use_relative_coords.get() else "절대좌표"
        print(f"최종 좌표 타입 설정: {coords_type}")
        self.update_status(f"좌표 타입이 {coords_type}로 설정되었습니다.")

    def edit_gesture(self):
        """선택된 제스처 수정"""
        # 선택된 항목의 인덱스 가져오기
        selected_indices = list(self.gesture_listbox.curselection())
        
        if not selected_indices or len(selected_indices) > 1:
            messagebox.showwarning("경고", "수정할 제스처를 하나만 선택해주세요.")
            return
            
        # 선택된 제스처 이름과 매크로 정보 저장
        gesture_index = selected_indices[0]
        gesture_name = self.gesture_listbox.get(gesture_index)
        
        # 제스처가 매핑에 있는지 확인
        if not self.gesture_manager or gesture_name not in self.gesture_manager.gesture_mappings:
            messagebox.showerror("오류", "선택한 제스처를 찾을 수 없습니다.")
            return
            
        # 기존 매크로 파일 이름 저장
        macro_name = self.gesture_manager.gesture_mappings[gesture_name]
        
        # 확인 메시지
        if not messagebox.askyesno("제스처 수정", f"'{gesture_name}' 제스처를 새로 녹화하시겠습니까?\n매크로는 유지됩니다."):
            return
            
        # 임시 저장을 위한 정보
        self.edit_gesture_info = {
            "old_gesture": gesture_name,
            "macro_name": macro_name
        }
        
        # 제스처 녹화 시작
        if self.gesture_manager:
            # 제스처 인식이 비활성화된 경우 활성화
            if not self.gesture_enabled.get():
                if messagebox.askyesno("제스처 인식 활성화", 
                                     "제스처 녹화를 위해 제스처 인식을 활성화해야 합니다.\n활성화하시겠습니까?"):
                    self.gesture_enabled.set(True)
                    self.toggle_gesture_recognition()
                else:
                    return
            
            # 기존 제스처 제거 (매크로 파일은 유지)
            self.gesture_manager.gesture_mappings.pop(gesture_name, None)
            
            # 제스처 녹화 모드로 전환
            self.gesture_manager.recording_mode = True
            
            # 수정 모드 설정
            self.editing_gesture = True
            
            # 제스처 시각화 창 생성
            self.gesture_manager.create_gesture_canvas()
            
            # 상태 업데이트
            self.update_status(f"'{gesture_name}' 제스처 수정 중... 새 제스처를 그려주세요.")
    
    # GestureManager의 on_gesture_ended 메서드에서 호출할 콜백 메서드 추가
    def on_gesture_edit_complete(self, new_gesture):
        """제스처 수정 완료 콜백"""
        if hasattr(self, 'editing_gesture') and self.editing_gesture and hasattr(self, 'edit_gesture_info'):
            # 새 제스처에 기존 매크로 연결
            old_gesture = self.edit_gesture_info["old_gesture"]
            macro_name = self.edit_gesture_info["macro_name"]
            
            # 새 제스처가 이미 존재하는지 확인
            if new_gesture in self.gesture_manager.gesture_mappings:
                messagebox.showwarning("중복된 제스처", 
                                     f"제스처 '{new_gesture}'가 이미 존재합니다. 수정이 취소되었습니다.")
                
                # 기존 제스처 복원
                self.gesture_manager.gesture_mappings[old_gesture] = macro_name
                self.gesture_manager.save_mappings()
                self.update_gesture_list()
                return
            
            # 새 제스처에 기존 매크로 할당
            self.gesture_manager.gesture_mappings[new_gesture] = macro_name
            
            # 매핑 저장
            self.gesture_manager.save_mappings()
            
            # 제스처 목록 업데이트
            self.update_gesture_list()
            
            # 상태 업데이트
            self.update_status(f"제스처가 '{old_gesture}'에서 '{new_gesture}'로 변경되었습니다.")
            
            # 편집 모드 종료
            self.editing_gesture = False
            delattr(self, 'edit_gesture_info')
            
            # 결과 메시지
            messagebox.showinfo("제스처 수정 완료", 
                              f"제스처가 '{old_gesture}'에서 '{new_gesture}'로 변경되었습니다.")