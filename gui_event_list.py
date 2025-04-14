    # gui_event_list.py
import tkinter as tk
from tkinter import ttk, messagebox
import sys  # For platform check


class GuiEventListMixin:
    """GUI의 이벤트 목록(오른쪽 프레임) UI 요소 및 관련 설정 생성을 담당하는 믹스인 클래스"""

    def _create_event_list_widgets(self, parent_frame):
        """이벤트 목록 관련 위젯 생성 (추출된 코드)"""
        # 오른쪽 프레임을 LabelFrame으로 변경
        event_list_frame = ttk.LabelFrame(
            parent_frame, text="Event List", padding=10)
        event_list_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # 이벤트 리스트박스 및 스크롤바
        event_scrollbar = ttk.Scrollbar(event_list_frame)
        event_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.event_listbox = tk.Listbox(event_list_frame, font=('Consolas', 11), selectmode=tk.EXTENDED,
                                        activestyle='dotbox', highlightthickness=2, exportselection=False)
        self.event_listbox.pack(fill=tk.BOTH, expand=True)
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

        # 이벤트 목록 아래 버튼 프레임
        event_btn_frame = ttk.Frame(event_list_frame)
        event_btn_frame.pack(fill=tk.X, pady=(5, 0))

        # 버튼 콜백 가져오기 (존재하지 않으면 경고 출력)
        select_all_cmd = getattr(
            self, 'select_all_events', lambda: print("select_all_events not found"))
        delete_selected_cmd = getattr(self, 'delete_selected_event', lambda: print(
            "delete_selected_event not found"))
        add_delay_cmd = getattr(self, 'add_delay_to_event', lambda: print(
            "add_delay_to_event not found"))
        delete_delay_cmd = getattr(
            self, 'delete_delay_events', lambda: print("delete_delay_events not found"))
        modify_delay_cmd = getattr(
            self, 'modify_delay_time', lambda: print("modify_delay_time not found"))
        move_up_cmd = getattr(self, 'move_event_up',
                              lambda: print("move_event_up not found"))
        move_down_cmd = getattr(self, 'move_event_down',
                                lambda: print("move_event_down not found"))

        ttk.Button(event_btn_frame, text="Select All",
                   command=select_all_cmd).pack(side=tk.LEFT, padx=5)
        ttk.Button(event_btn_frame, text="Delete Selected",
                   command=delete_selected_cmd).pack(side=tk.LEFT, padx=5)
        ttk.Button(event_btn_frame, text="Add Delay",
                   command=add_delay_cmd).pack(side=tk.LEFT, padx=5)
        ttk.Button(event_btn_frame, text="Delete Delay",
                   command=delete_delay_cmd).pack(side=tk.LEFT, padx=5)
        ttk.Button(event_btn_frame, text="Modify Delay",
                   command=modify_delay_cmd).pack(side=tk.LEFT, padx=5)
        ttk.Button(event_btn_frame, text="↑", width=2,
                   command=move_up_cmd).pack(side=tk.RIGHT, padx=2)
        ttk.Button(event_btn_frame, text="↓", width=2,
                   command=move_down_cmd).pack(side=tk.RIGHT, padx=2)

        # 랜덤 기능 버튼 프레임
        random_btn_frame = ttk.Frame(event_list_frame)
        random_btn_frame.pack(fill=tk.X, pady=(5, 0))

        add_random_pos_cmd = getattr(
            self, 'add_random_position', lambda: print("add_random_position not found"))
        add_random_delay_cmd = getattr(
            self, 'add_random_delay', lambda: print("add_random_delay not found"))

        ttk.Button(random_btn_frame, text="Add Random Position",
                   command=add_random_pos_cmd).pack(side=tk.LEFT, padx=5)
        ttk.Button(random_btn_frame, text="Add Random Delay",
                   command=add_random_delay_cmd).pack(side=tk.LEFT, padx=5)

        # 설정 관련 위젯은 여기서 생성하지 않음 (다른 믹스인으로 이동 고려)

    def update_event_list(self):
        """이벤트 목록 업데이트. 녹화 중이면 recorder에서, 아니면 editor에서 이벤트를 가져와 표시합니다."""
        if not hasattr(self, 'event_listbox'):
            print("Error: event_listbox not found in update_event_list.")
            return

        events = []
        source = None # 이벤트 소스 추적 (디버깅용)
        is_recording = False

        # 1. 이벤트 소스 확인
        if hasattr(self, 'recorder') and self.recorder and getattr(self.recorder, 'recording', False):
            # 녹화 중이면 recorder에서 가져옴
            try:
                if hasattr(self.recorder, 'events'):
                    events = self.recorder.events or []
                    source = "recorder"
                    is_recording = True
                else:
                    print("Warning: recorder found but has no 'events' attribute.")
            except Exception as e:
                print(f"Error getting events from recorder: {e}")
                # 오류 발생 시 빈 목록으로 처리하거나 다른 로직 추가 가능

        elif hasattr(self, 'editor') and self.editor:
             # 녹화 중이 아니면 editor에서 가져옴
             try:
                 if hasattr(self.editor, 'get_events') and callable(self.editor.get_events):
                     events = self.editor.get_events() or []
                     source = "editor (get_events)"
                 elif hasattr(self.editor, 'events'): # Fallback
                     events = self.editor.events or []
                     source = "editor (events)"
                 else:
                      print("Warning: editor found but has no way to get events.")
             except Exception as e:
                 print(f"Error getting events from editor: {e}")
                 events = [] # 오류 시 빈 목록

        # 2. 목록 초기화
        try:
            # 현재 선택 상태 저장 (업데이트 후 복원 위함)
            # selected_indices = self.event_listbox.curselection()
            # 현재 보이는 첫번째 줄 인덱스 저장 (스크롤 위치 유지 위함)
            # top_index = self.event_listbox.nearest(0)

            self.event_listbox.delete(0, tk.END)
        except tk.TclError:
             print("Error clearing event_listbox (likely destroyed).")
             return # 리스트박스 오류 시 더 이상 진행 불가
        except Exception as e:
             print(f"Unexpected error clearing listbox: {e}")
             return

        # 3. 이벤트 표시
        if not events:
            # print(f"update_event_list: No events found from {source if source else 'any source'}.")
            pass # 빈 목록이면 아무것도 안 함
        else:
            # print(f"update_event_list: Displaying {len(events)} events from {source}.")
            for i, event in enumerate(events):
                try:
                    self.display_event(event, i)
                except Exception as e:
                    print(f"Error displaying event {i} in update_event_list: {e}")
                    # 에러 발생 시 리스트박스에 에러 메시지 표시 시도
                    try:
                        self.event_listbox.insert(tk.END, f"{i+1:<4} ! Error: {e}")
                        self.event_listbox.itemconfig(tk.END, {'fg': 'red'})
                    except:
                        pass # 리스트박스도 문제 있으면 무시

        # 4. 스크롤 및 선택 복원 (선택 사항)
        if is_recording:
            # 녹화 중에는 항상 맨 아래로 스크롤
             try:
                 self.event_listbox.see(tk.END)
             except tk.TclError: pass # 위젯 파괴 시 무시
             except Exception as e: print(f"Error scrolling to end: {e}")
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

    def display_event(self, event, index):
        """Format and display a single event in the listbox (extracted code)."""
        if not hasattr(self, 'event_listbox'):
            print("Error: event_listbox not found in display_event.")
            return

        event_type = event.get('type', 'unknown')
        display_str = f"{index+1:<4} "  # Index (left-aligned, 4 spaces)

        try:
            # Format based on event type
            if event_type == 'keyboard':
                key = event.get('key', '')
                event_type_str = 'down' if event.get(
                    'event_type') == 'down' else 'up'
                # Timestamp (right-aligned, 8 spaces)
                timestamp = f"{event.get('time', 0):>8.3f}s"
                # Type (left-aligned, 4 spaces)
                display_str += f"{timestamp} K-{event_type_str:<4} {key}"
            elif event_type == 'mouse_move':
                pos_x, pos_y = event.get('position', (0, 0))
                timestamp = f"{event.get('time', 0):>8.3f}s"
                # Coordinates (right-aligned)
                pos_str = f"({pos_x:>4}, {pos_y:>4})"
                display_str += f"{timestamp} M-Move   {pos_str}"
                if 'random_range' in event:
                    range_px = event.get('random_range', 0)
                    display_str += f" +/-{range_px:<3}px"
            elif event_type == 'click' or event_type == 'drag':  # Assuming 'drag' also has button and pos
                button = event.get('button', '')
                event_type_str = event.get(
                    'event_type', 'click')  # 'press' or 'release'
                pos_x, pos_y = event.get('position', (0, 0))
                timestamp = f"{event.get('time', 0):>8.3f}s"
                pos_str = f"({pos_x:>4}, {pos_y:>4})"
                # Event type (left, 6), Button (left, 5)
                display_str += f"{timestamp} M-{event_type_str:<6} {button:<5} {pos_str}"
                if 'random_range' in event:
                    range_px = event.get('random_range', 0)
                    display_str += f" +/-{range_px:<3}px"
            elif event_type == 'delay':
                delay_sec = event.get('delay', 0)
                delay_ms = int(delay_sec * 1000)
                timestamp = f"{event.get('time', 0):>8.3f}s"
                display_str += f"{timestamp} Delay    {delay_ms:>6} ms"
                if 'random_range' in event:
                    range_sec = event.get('random_range', 0)
                    range_ms = int(range_sec * 1000)
                    display_str += f" +/-{range_ms:<5}ms"
            else:
                timestamp = f"{event.get('time', 0):>8.3f}s"
                display_str += f"{timestamp} ? Unknown event type: {event_type}"

            # Add to listbox
            self.event_listbox.insert(tk.END, display_str)

            # Apply background color for specific events
            bg_color = None
            if event_type == 'delay':
                # Light green for random, light blue for normal
                bg_color = '#E6F9E6' if 'random_range' in event else '#E6E6FF'
            elif event_type in ['mouse_move', 'click', 'drag'] and 'random_range' in event:
                bg_color = '#F9E6E6'  # Light red for random position

            if bg_color:
                self.event_listbox.itemconfig(tk.END, {'bg': bg_color})

        except tk.TclError:
            print("Error adding item to event_listbox (likely destroyed).")
        except Exception as e:
            print(f"Error formatting/displaying event {index}: {e}")
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

    def delete_selected_event(self):
        """선택한 이벤트 삭제 (추출된 코드)"""
        print("delete_selected_event 함수 호출됨")
        # 녹화 중에는 편집 불가
        if hasattr(self, 'recorder') and self.recorder.recording:
            print("녹화 중 - 이벤트 삭제 불가")
            messagebox.showwarning(
                "Warning", "Cannot edit events while recording.")
            return

        # 이벤트 리스트박스 확인
        if not hasattr(self, 'event_listbox'):
            print("Error: event_listbox not found.")
            return

        # 선택된 이벤트 확인 - 내부 변수 우선 사용
        selected_indices = getattr(self, 'selected_events', [])
        if not selected_indices:
            # 내부 변수 없으면 리스트박스에서 직접 확인
            selected = self.event_listbox.curselection()
            if not selected:
                messagebox.showwarning("Warning", "Select event(s) to delete.")
                return
            selected_indices = list(selected)

        print(f"Deleting events with indices: {selected_indices}")

        # 에디터 확인
        if not hasattr(self, 'editor'):
            print("Error: editor not found.")
            messagebox.showerror("Error", "Macro editor is not available.")
            return

        # 에디터에서 이벤트 삭제 시도
        delete_result = False
        deleted_count = 0
        try:
            # delete_events 메서드가 있으면 사용
            if hasattr(self.editor, 'delete_events') and callable(self.editor.delete_events):
                print("Using editor.delete_events method")
                deleted_count = self.editor.delete_events(selected_indices)
                delete_result = deleted_count > 0
            # events 속성 직접 접근 (대안)
            elif hasattr(self.editor, 'events'):
                print("Accessing editor.events directly for deletion")
                initial_length = len(self.editor.events)
                sorted_indices = sorted(selected_indices, reverse=True)
                for idx in sorted_indices:
                    if 0 <= idx < len(self.editor.events):
                        print(f"Deleting event at index {idx}")
                        del self.editor.events[idx]
                deleted_count = initial_length - len(self.editor.events)
                delete_result = deleted_count > 0
            else:
                print("Deletion method not found in editor")
                messagebox.showerror(
                    "Error", "Editor does not support event deletion.")
                return
        except Exception as e:
            print(f"Exception during event deletion: {e}")
            import traceback
            traceback.print_exc()
            messagebox.showerror(
                "Error", f"An error occurred while deleting events: {e}")
            return

        if delete_result:
            print(f"Successfully deleted {deleted_count} event(s)")
            # 선택 해제
            self.clear_selection()
            # 이벤트 목록 업데이트
            if hasattr(self, 'update_event_list') and callable(self.update_event_list):
                self.update_event_list()
            # 상태 업데이트
            if hasattr(self, 'update_status') and callable(self.update_status):
                self.update_status(f"{deleted_count} event(s) deleted.")
        else:
            print("Failed to delete events or no valid events were selected")
            messagebox.showerror("Error", "Failed to delete selected events.")

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

    def move_event_up(self):
        # ... (existing placeholder) ...
        pass  # 임시로 pass 추가

    def move_event_down(self):
        # ... (existing placeholder) ...
        pass  # 임시로 pass 추가

    def on_event_select(self, event=None):
        # ... (existing code) ...
        pass  # 임시로 pass 추가
