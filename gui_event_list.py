    # gui_event_list.py
import tkinter as tk
from tkinter import ttk, messagebox
import sys  # For platform check
import monitor_utils # 모니터 유틸리티 임포트
import time    # 시간 측정
import logging # 로깅 임포트 주석 제거


class GuiEventListMixin:
    """GUI의 이벤트 목록(오른쪽 프레임) UI 요소 및 관련 설정 생성을 담당하는 믹스인 클래스"""

    def _create_event_list_widgets(self, parent_frame):
        """이벤트 목록 관련 위젯 생성 - 구조 수정 및 1366x768 최적화"""
        # 불필요한 내부 LabelFrame 생성 제거
        # event_list_frame = ttk.LabelFrame(...) # 제거

        # 이벤트 리스트박스 및 스크롤바 (parent_frame에 직접 배치)
        event_scrollbar = ttk.Scrollbar(parent_frame)
        event_scrollbar.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 5), pady=(5, 2)) # 하단 pady 줄임 5 -> 2

        self.event_listbox = tk.Listbox(parent_frame, font=('Consolas', 10), selectmode=tk.EXTENDED,
                                        activestyle='dotbox', highlightthickness=2, exportselection=False)
        self.event_listbox.pack(fill=tk.BOTH, expand=True, padx=(5, 0), pady=(5, 2)) # 하단 pady 줄임 5 -> 2
        self.event_listbox.config(yscrollcommand=event_scrollbar.set,
                                      selectbackground='#4a6cd4',
                                      selectforeground='white')
        event_scrollbar.config(command=self.event_listbox.yview)

        # 이벤트 바인딩 (콜백 함수는 GuiEventListMixin 또는 GuiEventEditorMixin 등에 있어야 함)
        on_select_cmd = getattr(self, 'on_event_select',
                                lambda e: print("on_event_select not found"))
        on_double_click_cmd = getattr(self, 'on_event_double_click', lambda e: print(
            "on_event_double_click not found"))
        self.event_listbox.bind('<<ListboxSelect>>', on_select_cmd)
        self.event_listbox.bind('<Double-1>', on_double_click_cmd)
        
        # 추가 이벤트 바인딩 설정
        if hasattr(self, 'setup_event_listbox_bindings') and callable(self.setup_event_listbox_bindings):
            self.setup_event_listbox_bindings()
        
        # --- 버튼 프레임 및 옵션 프레임을 parent_frame에 직접 배치 ---

        # 첫 번째 줄 버튼 프레임 (pady 최소화)
        event_btn_frame = ttk.Frame(parent_frame)
        event_btn_frame.pack(fill=tk.X, pady=(2, 1)) # pady (2, 0) -> (2, 1)

        # 버튼 콜백 가져오기 (존재하지 않으면 경고 출력) - 순서 유지
        delete_selected_cmd = getattr(self, 'delete_selected_event', lambda: print(
            "delete_selected_event not found"))
        add_delay_cmd = getattr(self, 'add_delay_to_event', lambda: print(
            "add_delay_to_event not found"))
        delete_delay_cmd = getattr(
            self, 'delete_delay_event', lambda: print("delete_delay_event not found"))
        modify_delay_cmd = getattr(
            self, 'modify_delay_time', lambda: print("modify_delay_time not found"))
        
        # 버튼 크기 및 패딩 축소
        btn_width = 14 # 18 -> 14
        btn_padx = 1   # 2 -> 1
        btn_font_size = 8 # 9 -> 8

        # --- 첫 번째 줄 버튼들 pack --- 
        tk.Button(event_btn_frame, text="Delete",
                 font=('Arial', btn_font_size), # 폰트 적용
                 bg='#e8e8e8',
                 relief=tk.RAISED,
                 borderwidth=2,
                 highlightthickness=0,
                 width=btn_width, # 너비 설정
                 command=delete_selected_cmd).pack(side=tk.LEFT, padx=btn_padx)

        tk.Button(event_btn_frame, text="Add Delay",
                 font=('Arial', btn_font_size),
                 bg='#e8e8e8',
                 relief=tk.RAISED,
                 borderwidth=2,
                 highlightthickness=0,
                 width=btn_width, # 너비 설정
                 command=add_delay_cmd).pack(side=tk.LEFT, padx=btn_padx)

        tk.Button(event_btn_frame, text="Delete Delay",
                 font=('Arial', btn_font_size),
                 bg='#e8e8e8',
                 relief=tk.RAISED,
                 borderwidth=2,
                 highlightthickness=0,
                 width=btn_width, # 너비 설정
                 command=delete_delay_cmd).pack(side=tk.LEFT, padx=btn_padx)

        tk.Button(event_btn_frame, text="Modify Delay",
                 font=('Arial', btn_font_size),
                 bg='#e8e8e8',
                 relief=tk.RAISED,
                 borderwidth=2,
                 highlightthickness=0,
                 width=btn_width, # 너비 설정
                 command=modify_delay_cmd).pack(side=tk.LEFT, padx=btn_padx)

        # 두 번째 줄 버튼 프레임 (pady 최소화)
        event_btn_frame2 = ttk.Frame(parent_frame) # parent_frame으로 변경
        event_btn_frame2.pack(fill=tk.X, pady=(1, 1)) # pady (5, 0) -> (1, 1)

        # 버튼 콜백 가져오기 (두 번째 줄 - 랜덤/마우스 이동)
        add_random_pos_cmd = getattr(self, 'add_random_position', lambda: print("add_random_position not found"))
        add_random_delay_cmd = getattr(self, 'add_random_delay', lambda: print("add_random_delay not found"))
        add_mouse_move_cmd = getattr(self, 'add_mouse_move_event', lambda: print("add_mouse_move_event not found"))
        move_up_cmd = getattr(self, 'move_event_up',
                              lambda: print("move_event_up not found"))
        move_down_cmd = getattr(self, 'move_event_down',
                                lambda: print("move_event_down not found"))
        
        # --- 두 번째 줄 버튼들 pack --- 
        tk.Button(event_btn_frame2, text="Random Position",
                 font=('Arial', btn_font_size),
                 bg='#e8e8e8',
                 relief=tk.RAISED,
                 borderwidth=2,
                 highlightthickness=0,
                 width=btn_width, # 너비 설정
                 command=add_random_pos_cmd).pack(side=tk.LEFT, padx=btn_padx)

        tk.Button(event_btn_frame2, text="Random Delay",
                 font=('Arial', btn_font_size),
                 bg='#e8e8e8',
                 relief=tk.RAISED,
                 borderwidth=2,
                 highlightthickness=0,
                 width=btn_width, # 너비 설정
                 command=add_random_delay_cmd).pack(side=tk.LEFT, padx=btn_padx)

        tk.Button(event_btn_frame2, text="Add Mouse Move",
                 font=('Arial', btn_font_size),
                 bg='#e8e8e8',
                 relief=tk.RAISED,
                 borderwidth=2,
                 highlightthickness=0,
                 width=btn_width, # 너비 설정
                 command=add_mouse_move_cmd).pack(side=tk.LEFT, padx=btn_padx)

        # --- 위/아래 이동 버튼을 두 번째 프레임 오른쪽에 추가 --- 
        # ↓ 버튼 먼저 pack (오른쪽 끝에 위치)
        tk.Button(event_btn_frame2, text="↓",
                 font=('Arial', btn_font_size), # 폰트 적용
                 bg='#e8e8e8',
                 relief=tk.RAISED,
                 borderwidth=2,
                 highlightthickness=0,
                 width=3, # 화살표 버튼 너비
                 command=move_down_cmd).pack(side=tk.RIGHT, padx=btn_padx)

        # ↑ 버튼 다음에 pack (↓ 버튼 왼쪽에 위치)
        tk.Button(event_btn_frame2, text="↑",
                 font=('Arial', btn_font_size), # 폰트 적용
                 bg='#e8e8e8',
                 relief=tk.RAISED,
                 borderwidth=2,
                 highlightthickness=0,
                 width=3, # 화살표 버튼 너비
                 command=move_up_cmd).pack(side=tk.RIGHT, padx=btn_padx)

        # 녹화 옵션 프레임 (pady 최소화)
        options_frame = ttk.LabelFrame(parent_frame, text="Recording Options", padding=(5, 2))
        options_frame.pack(fill=tk.X, pady=(1, 2)) # pady (3, 0) -> (1, 2)

        # 옵션 체크박스들을 담을 내부 프레임 (기존 코드 유지)
        options_inner_frame = ttk.Frame(options_frame)
        options_inner_frame.pack(fill=tk.X, padx=0, pady=0) # padx/pady 추가

        # 각 옵션을 위한 프레임 생성 (내부 패딩 최소화)
        move_frame = ttk.Frame(options_inner_frame)
        move_frame.pack(side=tk.LEFT, padx=3, pady=0) # padx 5->3, pady 1->0
        # ttk.Checkbutton(move_frame, text="Record Mouse Move", variable=getattr(self, 'record_mouse_move', tk.BooleanVar(value=False))).pack(anchor=tk.W)

        delay_frame = ttk.Frame(options_inner_frame)
        delay_frame.pack(side=tk.LEFT, padx=3, pady=0) # padx 5->3, pady 1->0
        ttk.Checkbutton(delay_frame, text="Record Delay", variable=getattr(self, 'record_delay', tk.BooleanVar(value=True))).pack(anchor=tk.W)

        keyboard_frame = ttk.Frame(options_inner_frame)
        keyboard_frame.pack(side=tk.LEFT, padx=3, pady=0) # padx 5->3, pady 1->0
        ttk.Checkbutton(keyboard_frame, text="Record Keyboard", variable=getattr(self, 'record_keyboard', tk.BooleanVar(value=True))).pack(anchor=tk.W)

        # 좌표 옵션 프레임 (내부 패딩 조정)
        coord_frame = ttk.Frame(options_inner_frame)
        coord_frame.pack(side=tk.LEFT, padx=3, pady=0) # padx 5->3, pady 1->0

        # 라디오 버튼 선택 시 recorder의 recording_coord_mode 업데이트하는 콜백
        def update_recorder_coord_mode():
            selected_mode = self.coord_mode_var.get() # 수정: coord_selection_var -> coord_mode_var 사용

            # Recorder 설정 업데이트
            if hasattr(self, 'recorder') and self.recorder:
                # recorder 객체에 새로운 속성 설정
                self.recorder.recording_coord_mode = selected_mode 
                print(f"Recorder coord mode set to: {selected_mode}") # 디버깅 로그
                
                # --- 기존 BooleanVar 업데이트 로직 제거 ---
                # is_relative = (selected_mode != "absolute")
                # self.use_absolute_coords.set(not is_relative) 
                # self.use_relative_coords.set(is_relative) # 기존 변수 업데이트 중지
                # self.recorder.use_relative_coords = is_relative # 기존 속성 업데이트 중지
            else:
                print("Warning: Recorder object not found to update settings.")

        # GuiBase의 coord_mode_var 사용 (StringVar)
        ttk.Radiobutton(coord_frame, text="Absolute Coordinate",
                        variable=self.coord_mode_var, value="absolute",
                        command=update_recorder_coord_mode).pack(anchor=tk.W)
        ttk.Radiobutton(coord_frame, text="Mouse Relative Coordinate",
                        variable=self.coord_mode_var, value="playback_relative",
                        command=update_recorder_coord_mode).pack(anchor=tk.W)
        ttk.Radiobutton(coord_frame, text="Gesture Relative Coordinate",
                        variable=self.coord_mode_var, value="gesture_relative",
                        command=update_recorder_coord_mode).pack(anchor=tk.W)

    def update_event_list(self):
        """이벤트 목록 업데이트. 녹화 중이면 recorder에서, 아니면 editor에서 이벤트를 가져와 표시합니다."""
        # <<< 디버그 로그 제거 1 >>>
        # logging.debug("[GUI DEBUG] update_event_list started.")

        if not hasattr(self, 'event_listbox'):
            logging.error("Error: event_listbox not found in update_event_list.")
            return

        events = []
        source = None
        is_recording = False

        if hasattr(self, 'recorder') and self.recorder and getattr(self.recorder, 'recording', False):
            try:
                if hasattr(self.recorder, 'events'):
                    events = self.recorder.events or []
                    source = "recorder"
                    is_recording = True
                    # <<< 디버그 로그 제거 >>>
                    # logging.debug(f"[GUI DEBUG] Getting events from recorder. Recording: {is_recording}")
                else:
                    logging.warning("Warning: recorder found but has no 'events' attribute.")
            except Exception as e:
                logging.error(f"Error getting events from recorder: {e}", exc_info=True)
        elif hasattr(self, 'editor') and self.editor:
             try:
                 if hasattr(self.editor, 'get_events') and callable(self.editor.get_events):
                     events = self.editor.get_events() or []
                     source = "editor (get_events)"
                     # <<< 디버그 로그 제거 >>>
                     # logging.debug(f"[GUI DEBUG] Getting events from editor (get_events). Recording: {is_recording}")
                 elif hasattr(self.editor, 'events'): # Fallback
                     events = self.editor.events or []
                     source = "editor (events)"
                     # logging.debug(f"[GUI DEBUG] Getting events from editor (events attribute). Recording: {is_recording}")
                 else:
                      logging.warning("Warning: editor found but has no way to get events.")
             except Exception as e:
                 logging.error(f"Error getting events from editor: {e}", exc_info=True)
                 events = []

        # <<< 디버그 로그 제거 2 >>>
        # logging.debug(f"[GUI DEBUG] Fetched {len(events)} events from {source}.")

        # 2. 목록 초기화
        try:
            # 현재 선택 상태 저장 (업데이트 후 복원 위함)
            # selected_indices = self.event_listbox.curselection()
            # 현재 보이는 첫번째 줄 인덱스 저장 (스크롤 위치 유지 위함)
            # top_index = self.event_listbox.nearest(0)

            self.event_listbox.delete(0, tk.END)
        except tk.TclError:
             logging.error("Error clearing event_listbox (likely destroyed).")
             return # 리스트박스 오류 시 더 이상 진행 불가
        except Exception as e:
             logging.error(f"Unexpected error clearing listbox: {e}", exc_info=True)
             return

        # 3. 이벤트 표시
        if not events:
            # <<< 디버그 로그 제거 >>>
            # logging.debug("[GUI DEBUG] No events to display.")
            pass
        else:
            for i, event in enumerate(events):
                try:
                    # <<< 디버그 로그 제거 3 >>>
                    # logging.debug(f"[GUI DEBUG] Processing event {i}: {event}")
                    # if event.get('type') == 'mouse' and event.get('event_type') == 'wheel':
                    #      logging.debug(f"[GUI DEBUG] >>> Calling display_event for WHEEL event {i}")
                    self.display_event(event, i)
                except Exception as e:
                    logging.error(f"Error displaying event {i} in update_event_list: {e}", exc_info=True)
                    # 에러 발생 시 리스트박스에 에러 메시지 표시 시도
                    try:
                        self.event_listbox.insert(
                            tk.END, f"{i+1:<4} ! Error: {e}")
                        self.event_listbox.itemconfig(tk.END, {'fg': 'red'})
                    except:
                        pass # 리스트박스도 문제 있으면 무시

        # 4. 스크롤 및 선택 복원 (선택 사항)
        if is_recording:
            # 녹화 중에는 항상 맨 아래로 스크롤
             try:
                 self.event_listbox.see(tk.END)
             except tk.TclError: pass # 위젯 파괴 시 무시
             except Exception as e: logging.error(f"Error scrolling to end: {e}", exc_info=True)
        # else:
        #     # 녹화 중 아닐 때 스크롤 위치와 선택 복원 시도
        #     try:
        #         # 스크롤 위치 복원
        #         if top_index is not None and top_index < self.event_listbox.size():
        #              self.event_listbox.yview_moveto(top_index / self.event_listbox.size()) # 비율로 이동
        #             # self.event_listbox.see(top_index) # 특정 인덱스로 이동 (덜 정확할 수 있음)
        #
        #         # 선택 복원 (필요 시, 하지만 상태 변경 유발 가능성 있음)
        #         # for idx in selected_indices:
        #         #     if 0 <= idx < self.event_listbox.size():
        #         #         self.event_listbox.selection_set(idx)
        #     except tk.TclError: pass # 위젯 파괴 시 무시
        #     except Exception as e: print(f"Error restoring scroll/selection: {e}")

        # <<< Tkinter 업데이트 요청 추가 >>>
        if hasattr(self, 'root') and self.root and self.root.winfo_exists():
             self.root.update_idletasks()

        # <<< 디버그 로그 제거 >>>
        # logging.debug("[GUI DEBUG] update_event_list finished.")

    def display_event(self, event, index):
        """이벤트 목록 표시 형식 변경: 키/버튼 값 우선, 시간 정보 제거"""
        # <<< 디버그 로그 제거 4 >>>
        # logging.debug(f"[GUI DEBUG] display_event started for index {index}, event: {event}")

        if not hasattr(self, 'event_listbox'):
            logging.error("Error: event_listbox not found in display_event.")
            return

        event_type = event.get('type', 'unknown')
        display_str = f"{index+1:<4} "  # 인덱스 (왼쪽 정렬, 4칸)

        try:
            # 이벤트 유형별 포맷
            if event_type == 'keyboard':
                key = event.get('key', '')
                event_type_str = 'down' if event.get('event_type') == 'down' else 'up'
                # 키 값 부분을 특정 길이로 맞추고 UP/DOWN 정렬
                key_part = f"Key: {key}"
                display_str += f"{key_part.ljust(20)} {event_type_str.upper()}"
            elif event_type == 'mouse':
                # <<< 디버그 로그 제거 5 >>>
                # logging.debug(f"[GUI DEBUG] Processing mouse event in display_event: {event}")
                event_type_str = event.get('event_type', 'unknown')
                coord_mode = event.get('coord_mode', 'absolute') # <-- 좌표 모드 가져오기
                pos_x, pos_y = event.get('position', (0, 0))

                # 좌표 모드 접두사 설정
                mode_prefix = "Abs:" # 기본값
                if coord_mode == 'playback_relative':
                    mode_prefix = "MRel:"
                elif coord_mode == 'gesture_relative':
                    mode_prefix = "GRel:"

                # 좌표 문자열 생성 (기존 로직 활용하되, is_relative 대신 coord_mode 사용)
                pos_str = ""
                if coord_mode == 'absolute':
                    monitor = monitor_utils.get_monitor_from_point(pos_x, pos_y)
                    if monitor:
                        rel_x, rel_y = monitor_utils.absolute_to_relative(pos_x, pos_y, monitor)
                        monitor_index = monitor_utils.get_monitors().index(monitor)
                        # mode_prefix는 이미 "Abs:" 이므로 여기서는 M 번호만 추가
                        pos_str = f"M{monitor_index}:({rel_x:>4}, {rel_y:>4})"
                    else:
                        pos_str = f"M?:({pos_x:>4}, {pos_y:>4})" # 모니터 못 찾으면 M?
                else: # playback_relative 또는 gesture_relative
                    # mode_prefix는 위에서 설정됨 (MRel: 또는 GRel:)
                    pos_str = f"({pos_x:>4}, {pos_y:>4})"

                # 최종 좌표 표시 문자열 (접두사 + 좌표)
                coord_display = f"{mode_prefix}{pos_str}"

                if event_type_str == 'move':
                    # is_relative = event.get('is_relative', False) # 더 이상 사용 안 함
                    # 기존 pos_str 생성 로직 제거
                    display_str += f"Move     {coord_display}" # coord_display 사용
                    if 'random_range' in event:
                        range_px = event.get('random_range', 0)
                        display_str += f" +/-{range_px:<3}px"
                elif event_type_str in ['up', 'down', 'double']:
                    button = event.get('button', '')
                    # is_relative = event.get('is_relative', False) # 더 이상 사용 안 함
                    # 기존 pos_str 생성 로직 제거
                    # 버튼 값 부분을 특정 길이로 맞추고 UP/DOWN 정렬
                    button_part = f"Mouse: {button}"
                    action_str = f"{event_type_str.upper()}"
                    display_str += f"{button_part.ljust(20)} {action_str.ljust(6)} {coord_display}" # coord_display 사용
                    if 'random_range' in event:
                        range_px = event.get('random_range', 0)
                        display_str += f" +/-{range_px:<3}px"
                elif event_type_str == 'wheel':
                     # <<< 디버그 로그 제거 6 >>>
                     # logging.debug(f"[GUI DEBUG] >>> Handling 'wheel' event type string in display_event")
                     # 휠 이벤트는 좌표 표시 로직 변경 없음 (필요 시 coord_display 추가 가능)
                     delta = event.get('delta', 0)
                     direction_str = "up" if delta > 0 else "down" if delta < 0 else ""
                     wheel_part = "Mouse: wheel"
                     display_str += f"{wheel_part.ljust(20)} {direction_str.ljust(6)} {delta}"
                else:
                     # 알 수 없는 마우스 액션 (wheel은 이제 처리됨)
                     display_str += f"Mouse Action: {event_type_str}" # 맨 앞 '?' 제거
            elif event_type == 'delay':
                delay_sec = event.get('delay', 0)
                delay_ms = int(delay_sec * 1000)
                # 딜레이 시간 표시 형식 변경 (ms 값이 콜론 바로 뒤에 오도록)
                # delay_part = "Delay:"
                # display_str += f"{delay_part.ljust(20)} {delay_ms:>6} ms"
                display_str += f"Delay: {delay_ms} ms"
                if 'random_range' in event:
                    range_sec = event.get('random_range', 0)
                    range_ms = int(range_sec * 1000)
                    # display_str += f" +/-{range_ms:<5}ms"
                    display_str += f" +/-{range_ms}ms"
            else:
                # 시간 정보 제거
                display_str += f"? Unknown event type: {event_type}"

            # <<< 디버그 로그 제거 7 >>>
            # logging.debug(f"[GUI DEBUG] Final display_str for index {index}: '{display_str}'")

            # 리스트박스에 추가
            self.event_listbox.insert(tk.END, display_str)

            # Apply background color based on event type
            bg_color = None
            if event_type == 'keyboard':
                # bg_color = '#FFFFE0' # Light Yellow
                bg_color = '#E6F0FF' # Light Blue (Swapped)
            elif event_type == 'mouse' or event_type == 'click' or event_type == 'drag':
                bg_color = '#FFE6E6' # Light Red
            elif event_type == 'delay': # 딜레이 배경색 추가
                 bg_color = '#FFFFE0' # Light Yellow
            # else: # Unknown type, no specific background
            #     pass

            if bg_color:
                try:
                    self.event_listbox.itemconfig(tk.END, {'bg': bg_color})
                except tk.TclError: # Handle cases where the widget might be destroyed
                    pass

        except tk.TclError:
            logging.error("Error adding item to event_listbox (likely destroyed).")
        except Exception as e:
            logging.error(f"Error formatting/displaying event {index}: {e}", exc_info=True)
            try:
                # Add error message to listbox if possible
                self.event_listbox.insert(
                    tk.END, f"{index+1:<4} ! Error displaying event: {e}")
                self.event_listbox.itemconfig(tk.END, {'fg': 'red'})
            except:
                pass  # Ignore if listbox is also broken

    def clear_selection(self):
        """이벤트 목록 선택 해제"""
        if hasattr(self, 'event_listbox'):
            self.event_listbox.selection_clear(0, tk.END)
        self.selected_events = []  # 내부 변수도 초기화

    def select_all_events(self):
        """모든 이벤트 선택 (추출된 코드)"""
        print("select_all_events 함수 호출됨")
        # 녹화 중에는 선택 불가
        if hasattr(self, 'recorder') and self.recorder.recording:
            print("녹화 중 - 전체 선택 불가")
            return

        # 이벤트 리스트박스 확인
        if not hasattr(self, 'event_listbox'):
            print("Error: event_listbox not found.")
            return

        # 이벤트 목록 크기 가져오기
        try:
            event_count = self.event_listbox.size()
        except tk.TclError:
            print("Error accessing event_listbox size (likely destroyed).")
            return  # 위젯이 없으면 진행 불가

        print(f"Number of events: {event_count}")
        if event_count == 0:
            return

        # 내부 변수 초기화
        if not hasattr(self, 'selected_events'):
            self.selected_events = []

        # 모든 이벤트를 리스트박스에서 선택
        try:
            self.event_listbox.selection_clear(0, tk.END)
            self.event_listbox.selection_set(0, tk.END)
        except tk.TclError:
            print("Error selecting items in event_listbox (likely destroyed).")
            return

        # 내부 선택 목록 업데이트
        self.selected_events = list(range(event_count))

        # 시각적 피드백 (스크롤)
        if event_count > 0:
            try:
                self.event_listbox.see(0)
            except tk.TclError:
                pass  # 위젯 파괴 시 무시

        print(f"Selected all {len(self.selected_events)} events.")

        # 상태 업데이트
        if hasattr(self, 'update_status') and callable(self.update_status):
            self.update_status(f"All {event_count} events selected.")

    def on_event_select(self, event=None):
        # ... (existing code) ...
        pass  # 임시로 pass 추가
