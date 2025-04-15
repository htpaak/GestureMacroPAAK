# gui_event_editor.py
import tkinter as tk
from tkinter import messagebox, simpledialog
import os # update_event_list에서 사용될 수 있음
import copy # update_event_list에서 사용될 수 있음
import json # update_event_list에서 사용될 수 있음

class GuiEventEditorMixin:
    """GUI의 이벤트 목록 업데이트, 표시, 선택, 편집(추가, 삭제, 수정, 이동)을 담당하는 믹스인 클래스"""

    def update_status(self, message):
        """하단 상태 표시줄 업데이트 (구현은 gui_base.py에서)"""
        raise NotImplementedError

    # --- Event List Update & Display ---

    def update_event_list(self):
        """이벤트 목록 리스트박스를 현재 이벤트 데이터로 업데이트"""
        # print("update_event_list called") # 디버깅용
        if not hasattr(self, 'event_listbox'): return

        # 현재 선택 기억 (restore_selection 플래그에 따라)
        saved_selection = []
        if getattr(self, 'restore_selection', True):
            saved_selection = self.event_listbox.curselection()

        # 리스트박스 내용 지우기 (녹화 중이 아닐 때만)
        if not (hasattr(self, 'recorder') and self.recorder.recording):
            self.event_listbox.delete(0, tk.END)

        # 표시할 이벤트 목록 가져오기
        events_to_display = []
        if hasattr(self, 'recorder') and self.recorder.recording:
            # 녹화 중일 때는 recorder의 이벤트 사용
            events_to_display = self.recorder.events if hasattr(self.recorder, 'events') else []
            # 녹화 중에는 새로 추가된 것만 표시할 수도 있지만, 여기서는 전체 갱신 가정
        elif hasattr(self, 'editor'):
            # 에디터의 이벤트 사용
            if hasattr(self.editor, 'get_events') and callable(self.editor.get_events):
                try: events_to_display = self.editor.get_events() or []
                except Exception as e: print(f"Error calling get_events: {e}")
            elif hasattr(self.editor, 'events'): # Fallback
                events_to_display = self.editor.events or []
        else:
            print("Warning: No recorder or editor found to get events from.")

        # 이벤트 목록 표시
        if events_to_display:
            for i, event in enumerate(events_to_display):
                self.display_event(event, i)
        # else:
        #     print("No events to display.") # 디버깅용

        # 선택 복원 (필요하고 유효한 경우)
        if saved_selection and not (hasattr(self, 'recorder') and self.recorder.recording):
            max_index = self.event_listbox.size() - 1
            valid_selections = [idx for idx in saved_selection if 0 <= idx <= max_index]
            if valid_selections:
                self.event_listbox.selection_clear(0, tk.END)
                for idx in valid_selections:
                    self.event_listbox.selection_set(idx)
                if valid_selections: self.event_listbox.see(valid_selections[-1]) # 마지막 선택 보이게

        # 녹화 중 실시간 업데이트 타이머 설정 (GuiRecordingMixin에서 처리하는 것이 더 적합할 수 있음)
        # if hasattr(self, 'recorder') and self.recorder.recording:
        #     if hasattr(self, 'update_timer'): self.root.after_cancel(self.update_timer)
        #     self.update_timer = self.root.after(self.update_interval, self.update_event_list)

    def display_event(self, event, index):
        """주어진 이벤트를 리스트박스의 특정 인덱스에 맞게 포맷하여 표시"""
        if not hasattr(self, 'event_listbox'): return

        event_type = event.get('type', 'unknown')
        display_str = f"{index+1:3d} {event.get('time', 0):.3f} " # 기본 형식

        try:
            if event_type == 'keyboard':
                key = event.get('key', '')
                action = event.get('event_type', 'press') # 'down' -> 'press', 'up' -> 'release' ?
                display_str += f"K-{action.ljust(7)} {key}"
            elif event_type == 'mouse':
                button = event.get('button', 'move')
                action = event.get('event_type', '') # 'click', 'press', 'release', 'move', 'wheel'
                pos_x, pos_y = event.get('position', (0, 0))
                range_px = event.get('position_range', 0)
                wheel_delta = event.get('delta', 0) # Wheel 이벤트용

                action_str = action.ljust(7)
                pos_str = f"({pos_x}, {pos_y})"
                if range_px > 0: pos_str += f" ±{range_px}px"

                if action == 'wheel':
                    display_str += f"M-{action_str} Delta:{wheel_delta}"
                elif button == 'move':
                    display_str += f"M-move      {pos_str}"
                else:
                    display_str += f"M-{action_str} {button.ljust(5)} {pos_str}"

            elif event_type == 'delay':
                delay_ms = int(event.get('delay', 0) * 1000)
                range_ms = int(event.get('random_range', 0) * 1000)
                delay_str = f"Delay: {delay_ms}ms"
                if range_ms > 0: delay_str += f" ±{range_ms}ms"
                display_str += f"D {delay_str}"
            else:
                display_str += f"? Unknown type: {event_type}"

        except Exception as e:
            print(f"Error formatting event at index {index}: {e}")
            display_str = f"{index+1:3d} ??? Error displaying event ???"

        # 리스트박스에 삽입
        # 녹화 중일 때는 END에 추가, 아닐 때는 index 위치에 insert (더 정확하지만 느릴 수 있음)
        # 여기서는 항상 END에 추가하고 update_event_list에서 전체를 다시 그리는 것으로 가정
        self.event_listbox.insert(tk.END, display_str)

        # 배경색 설정
        bg_color = None
        if event_type == 'delay':
            bg_color = '#E6F9E6' if 'random_range' in event and event['random_range'] > 0 else '#E6E6FF'
        elif event_type == 'mouse' and 'position_range' in event and event['position_range'] > 0:
            bg_color = '#F9E6E6'

        if bg_color:
            try:
                self.event_listbox.itemconfig(tk.END, {'bg': bg_color})
            except tk.TclError: # 위젯이 파괴된 경우 등
                pass

    # --- Event Selection ---

    def on_event_select(self, event=None):
        """이벤트 리스트박스에서 항목 선택 시 호출"""
        if not hasattr(self, 'event_listbox'): return
        if hasattr(self, '_skip_selection') and self._skip_selection: return # 내부 처리 중 스킵
        if hasattr(self, 'recorder') and hasattr(self.recorder, 'recording') and self.recorder.recording: return # 녹화 중 선택 무시

        # 이벤트 리스트박스 크기 확인
        listbox_size = self.event_listbox.size()
        if listbox_size == 0: return # 비어있으면 처리 불필요

        # 보다 안정적인 방법으로 현재 선택 가져오기
        try:
            selected = list(self.event_listbox.curselection())
            
            # UI에서 선택된 항목이 없으면 내부 상태도 초기화
            if not selected:
                self.selected_events = []
                self.update_status("No events selected.")
                return
                
            # 선택이 변경되었는지 확인
            if hasattr(self, 'selected_events') and set(selected) == set(self.selected_events):
                return  # 변경 없으면 처리 중단
                
            # 드래그 상태의 선택 범위를 확인 - 연속된 범위가 있으면 모든 항목 포함시키기
            if len(selected) >= 2:
                min_idx = min(selected)
                max_idx = max(selected)
                # 선택 범위가 연속되지 않았다면 모든 범위 포함
                if max_idx - min_idx + 1 > len(selected):
                    selected = list(range(min_idx, max_idx + 1))
                    # 시각적 선택 업데이트
                    self._skip_selection = True
                    try:
                        self.event_listbox.selection_clear(0, tk.END)
                        for idx in selected:
                            self.event_listbox.selection_set(idx)
                    finally:
                        self._skip_selection = False
            
            # 항상 리스트박스의 실제 선택으로 내부 상태 갱신
            self.selected_events = list(self.event_listbox.curselection())
            print(f"Selection updated: {self.selected_events}") # 디버그용
            
        except Exception as e:
            print(f"Error updating selection: {e}")
            return

        # 상태 표시줄 업데이트
        count = len(self.selected_events)
        if count == 1:
            idx = self.selected_events[0]
            # 이벤트 타입 가져오기 (에디터 사용)
            event_type = "Unknown"
            try:
                if hasattr(self.editor, 'get_events') and callable(self.editor.get_events):
                    current_events = self.editor.get_events() or []
                    if 0 <= idx < len(current_events):
                        event_type = current_events[idx].get('type', 'Unknown')
                elif hasattr(self.editor, 'events'): # Fallback
                    if 0 <= idx < len(self.editor.events):
                        event_type = self.editor.events[idx].get('type', 'Unknown')
            except Exception as e: 
                print(f"Error getting event type: {e}")
                pass # 오류 무시

            self.update_status(f"Event #{idx+1} selected (Type: {event_type})")
        elif count > 1:
            self.update_status(f"{count} events selected")
        else:
            # 선택 해제 시 (curselection이 비어있을 때)
            self.selected_events = []
            self.update_status("No events selected.")
            
    # 추가 - 리스트박스 이벤트 바인딩 설정을 위한 메서드
    def setup_event_listbox_bindings(self):
        """이벤트 리스트박스의 추가 이벤트 바인딩 설정"""
        if not hasattr(self, 'event_listbox'): return
        
        # 이미 바인딩 설정되었는지 확인
        if hasattr(self, '_listbox_bindings_setup'): return
        
        # 마우스 버튼 떼는 이벤트에 대한 바인딩 (드래그 선택 후)
        self.event_listbox.bind('<ButtonRelease-1>', self.on_event_select)
        
        # 키보드 화살표 등의 이벤트에 대한 바인딩
        self.event_listbox.bind('<KeyRelease>', self.on_event_select)
        
        # 바인딩 완료 플래그 설정
        self._listbox_bindings_setup = True

    def clear_selection(self):
        """이벤트 리스트박스 선택 해제 및 내부 상태 초기화"""
        if hasattr(self, 'event_listbox'):
            self.event_listbox.selection_clear(0, tk.END)
        self.selected_events = []

    def set_single_selection(self, index):
        """주어진 인덱스의 이벤트만 선택하고 보이도록 스크롤"""
        if not hasattr(self, 'event_listbox'): return False
        if not (0 <= index < self.event_listbox.size()): return False

        self._skip_selection = True # on_event_select 콜백 방지
        try:
            self.event_listbox.selection_clear(0, tk.END)
            self.event_listbox.selection_set(index)
            self.event_listbox.see(index)
            self.selected_events = [index] # 내부 상태 업데이트
        finally:
            self._skip_selection = False
        return True

    def select_all_events(self):
        """모든 이벤트 선택"""
        if not hasattr(self, 'event_listbox'): return
        if hasattr(self, 'recorder') and self.recorder.recording: return # 녹화 중 불가

        count = self.event_listbox.size()
        if count == 0: return

        self._skip_selection = True
        try:
            self.event_listbox.selection_clear(0, tk.END)
            self.event_listbox.selection_set(0, tk.END) # 모든 항목 선택
            self.selected_events = list(range(count)) # 내부 상태 업데이트
            self.event_listbox.see(0) # 첫 항목 보이게
        finally:
            self._skip_selection = False

        self.update_status(f"All {count} events selected.")


    # --- Event Modification ---

    def _get_valid_selected_indices(self):
        """현재 선택된 유효한 이벤트 인덱스 목록 반환"""
        # 항상 리스트박스에서 직접 현재 선택 상태 가져오기 (가장 정확한 방법)
        direct_selection = []
        if hasattr(self, 'event_listbox'):
            try:
                direct_selection = list(self.event_listbox.curselection())
                if direct_selection:
                    # 내부 상태 업데이트 (UI에 표시된 선택으로 항상 동기화)
                    self.selected_events = direct_selection
                    print(f"Direct selection from listbox: {direct_selection}")
            except Exception as e:
                print(f"Error getting direct selection: {e}")

        # 만약 리스트박스에서 직접 선택을 가져오지 못했다면 내부 저장된 선택 사용
        if not direct_selection and hasattr(self, 'selected_events'):
            direct_selection = self.selected_events
            
        # 선택이 없으면 빈 리스트 반환
        if not direct_selection:
            return []
            
        # 에디터의 현재 이벤트 수 확인
        event_count = 0
        try:
            if hasattr(self.editor, 'get_event_count') and callable(self.editor.get_event_count):
                event_count = self.editor.get_event_count()
            elif hasattr(self.editor, 'get_events') and callable(self.editor.get_events):
                event_count = len(self.editor.get_events() or [])
            elif hasattr(self.editor, 'events'): # Fallback
                event_count = len(self.editor.events or [])
        except Exception as e:
            print(f"Error getting event count: {e}")
            return []  # 이벤트 수 확인 실패시 빈 목록 반환

        # 유효한 인덱스만 필터링
        valid_indices = [idx for idx in direct_selection if 0 <= idx < event_count]
        
        if len(valid_indices) != len(direct_selection):
            print(f"Some selected indices were invalid. Original: {direct_selection}, Valid: {valid_indices}")
            
            # 리스트박스 선택 업데이트 (유효한 항목만 선택)
            if hasattr(self, 'event_listbox') and valid_indices != direct_selection:
                self._skip_selection = True
                try:
                    self.event_listbox.selection_clear(0, tk.END)
                    for idx in valid_indices:
                        self.event_listbox.selection_set(idx)
                finally:
                    self._skip_selection = False
            
            # 내부 상태도 업데이트
            self.selected_events = valid_indices

        return valid_indices

    def delete_selected_event(self):
        """선택된 이벤트 삭제"""
        if hasattr(self, 'recorder') and self.recorder.recording:
            messagebox.showwarning("Warning", "Cannot edit events while recording.")
            return

        indices_to_delete = self._get_valid_selected_indices()
        if not indices_to_delete:
            messagebox.showwarning("Warning", "Select event(s) to delete.")
            return

        # 에디터에게 삭제 요청
        deleted_count = 0
        try:
            if hasattr(self.editor, 'delete_events') and callable(self.editor.delete_events):
                deleted_count = self.editor.delete_events(indices_to_delete)
            elif hasattr(self.editor, 'events'): # Fallback
                # 역순으로 삭제하여 인덱스 문제 방지
                for idx in sorted(indices_to_delete, reverse=True):
                    if 0 <= idx < len(self.editor.events):
                        del self.editor.events[idx]
                        deleted_count += 1
            else:
                messagebox.showerror("Error", "Editor does not support event deletion.")
                return
        except Exception as e:
            messagebox.showerror("Error", f"Error deleting events: {e}")
            return

        if deleted_count > 0:
            self.restore_selection = False # 삭제 후 선택 복원 안 함
            self.clear_selection()
            self.update_event_list()
            self.restore_selection = True
            self.update_status(f"{deleted_count} event(s) deleted.")
        else:
            messagebox.showerror("Error", "Failed to delete selected events.")


    def add_delay_to_event(self):
        """선택된 이벤트 바로 뒤 또는 목록 끝에 딜레이 추가"""
        if hasattr(self, 'recorder') and self.recorder.recording:
            messagebox.showwarning("Warning", "Cannot edit events while recording.")
            return

        # 딜레이 시간 입력 받기
        delay_ms = simpledialog.askinteger("Add Delay", "Delay time (ms):",
                                           minvalue=1, maxvalue=600000) # 1ms ~ 10분
        if delay_ms is None:
            self.update_status("Delay addition cancelled.")
            return

        delay_sec = delay_ms / 1000.0

        # 삽입 위치 결정
        insert_index = -1 # 기본값: 맨 끝에 추가
        selected_indices = self._get_valid_selected_indices()

        if selected_indices:
            # 선택된 항목이 있으면, 가장 마지막 선택된 항목 다음에 삽입
            insert_index = max(selected_indices) + 1
            print(f"Adding delay after selected index {max(selected_indices)} (at index {insert_index}).")
        else:
            # 선택된 항목이 없으면 맨 끝에 삽입
            print("No selection, adding delay at the end.")
            # insert_index는 이미 -1 (맨 끝)로 설정됨

        # 딜레이 이벤트 생성
        delay_event = {'type': 'delay', 'delay': delay_sec, 'time': 0} # 시간은 insert_event에서 계산

        # 에디터에 삽입 요청
        try:
            inserted_idx = -1
            if hasattr(self.editor, 'insert_event') and callable(self.editor.insert_event):
                inserted_idx = self.editor.insert_event(insert_index, delay_event)
            elif hasattr(self.editor, 'events') and insert_index != -1: # Fallback (직접 삽입 - 특정 위치)
                self.editor.events.insert(insert_index, delay_event)
                inserted_idx = insert_index
            elif hasattr(self.editor, 'events'): # Fallback (직접 삽입 - 맨 끝)
                self.editor.events.append(delay_event)
                inserted_idx = len(self.editor.events) - 1
            else:
                 messagebox.showerror("Error", "Editor does not support event insertion.")
                 return

            if inserted_idx != -1:
                self.restore_selection = False
                self.clear_selection()
                self.update_event_list()
                # 새로 추가된 딜레이를 선택하고 보이도록 함
                self.set_single_selection(inserted_idx)
                self.restore_selection = True
                self.update_status(f"Delay of {delay_ms}ms added at index {inserted_idx + 1}.")
            else:
                messagebox.showerror("Error", "Failed to add delay event.")

        except Exception as e:
            messagebox.showerror("Error", f"Error adding delay event: {e}")
            import traceback
            traceback.print_exc()


    def modify_delay_time(self):
        """선택된 딜레이 이벤트의 시간 수정"""
        if hasattr(self, 'recorder') and hasattr(self.recorder, 'recording') and self.recorder.recording:
            messagebox.showwarning("Warning", "Cannot edit events while recording.")
            return

        # 현재 선택 상태 다시 확인 (드래그 선택 시 정확히 인식하기 위함)
        if hasattr(self, 'event_listbox'):
            try:
                current_selection = list(self.event_listbox.curselection())
                if current_selection:  # 리스트박스에서 직접 현재 선택 가져오기
                    self.selected_events = current_selection
            except Exception as e:
                print(f"Error getting current selection: {e}")

        # 원래 선택한 항목 저장 (단일 선택 처리를 위해)
        original_selection = self._get_valid_selected_indices()
        if not original_selection:
            messagebox.showwarning("Warning", "Select delay event(s) to modify.")
            return
            
        # 단일 항목 선택 여부 확인
        single_selection = len(original_selection) == 1
        first_selected_index = original_selection[0] if single_selection else None

        # 이벤트 목록 가져오기
        events = []
        try:
            if hasattr(self.editor, 'get_events') and callable(self.editor.get_events):
                events = self.editor.get_events() or []
            elif hasattr(self.editor, 'events'):  # Fallback
                events = self.editor.events or []
        except Exception as e:
            print(f"Error getting events: {e}")
            events = []

        if not events:
            messagebox.showwarning("Warning", "No events available.")
            return

        # 선택된 것 중 실제 딜레이 이벤트만 필터링
        delay_indices = []
        for idx in original_selection:
            if 0 <= idx < len(events) and events[idx].get('type') == 'delay':
                delay_indices.append(idx)

        if not delay_indices:
            messagebox.showwarning("Warning", "No delay events selected.")
            return

        # 디버그 정보 출력
        print(f"Selected indices: {original_selection}")
        print(f"Delay indices to modify: {delay_indices}")

        # 새 딜레이 시간 입력
        # 첫 번째 선택된 딜레이의 현재 값 보여주기
        current_delay_ms = 0
        if delay_indices:
            current_delay_ms = int(events[delay_indices[0]].get('delay', 0) * 1000)

        new_delay_ms = simpledialog.askinteger("Modify Delay", "New delay time (ms):",
                                               initialvalue=current_delay_ms,
                                               minvalue=1, maxvalue=600000)
        if new_delay_ms is None: return

        new_delay_sec = new_delay_ms / 1000.0

        # 에디터에 수정 요청
        modified_count = 0
        try:
            # 함수 이름 수정: set_selected_delays_time 사용
            if hasattr(self.editor, 'set_selected_delays_time') and callable(self.editor.set_selected_delays_time):
                result = self.editor.set_selected_delays_time(delay_indices, new_delay_sec)
                if result:
                    modified_count = len(delay_indices)
            elif hasattr(self.editor, 'events'):  # Fallback
                for idx in delay_indices:
                    if 0 <= idx < len(self.editor.events) and self.editor.events[idx]['type'] == 'delay':
                        self.editor.events[idx]['delay'] = new_delay_sec
                        modified_count += 1
            else:
                messagebox.showerror("Error", "Editor does not support delay modification.")
                return

        except Exception as e:
            messagebox.showerror("Error", f"Error modifying delays: {e}")
            return

        if modified_count > 0:
            # 수정 전 선택 상태 초기화
            self.restore_selection = False
            self.clear_selection()
            
            # 이벤트 목록 업데이트
            self.update_event_list()
            
            # 단일 선택이었던 경우 원래 선택했던 항목만 다시 선택
            if single_selection and first_selected_index is not None:
                self._skip_selection = True
                try:
                    self.event_listbox.selection_set(first_selected_index)
                    self.event_listbox.see(first_selected_index)
                    self.selected_events = [first_selected_index]
                finally:
                    self._skip_selection = False
            
            # 선택 상태 복원 설정
            self.restore_selection = True
            
            # 상태 메시지 업데이트
            self.update_status(f"{modified_count} delay event(s) set to {new_delay_ms}ms.")
        else:
            messagebox.showerror("Error", "Failed to modify selected delay events.")


    def move_event_up(self):
        """선택된 단일 이벤트를 위로 이동"""
        if hasattr(self, 'recorder') and self.recorder.recording:
            messagebox.showwarning("Warning", "Cannot edit events while recording.")
            return

        selected = self._get_valid_selected_indices()
        if len(selected) != 1:
            messagebox.showwarning("Warning", "Select exactly one event to move.")
            return

        current_index = selected[0]
        if current_index == 0:
            messagebox.showinfo("Info", "Cannot move the first event further up.")
            return

        # 에디터에 이동 요청
        new_index = -1
        try:
            if hasattr(self.editor, 'move_event_up') and callable(self.editor.move_event_up):
                new_index = self.editor.move_event_up(current_index)
            elif hasattr(self.editor, 'events'): # Fallback
                if 0 < current_index < len(self.editor.events):
                    self.editor.events.insert(current_index - 1, self.editor.events.pop(current_index))
                    new_index = current_index - 1
                else:
                    messagebox.showerror("Error", "Editor does not support moving events.")
                    return
        except Exception as e:
            messagebox.showerror("Error", f"Error moving event up: {e}")
            return

        if new_index != -1:
            self.restore_selection = False
            self.clear_selection()
            self.update_event_list()
            self.set_single_selection(new_index) # 이동된 위치 선택
            self.restore_selection = True
            self.update_status(f"Event moved up to position {new_index + 1}.")
        else:
            messagebox.showerror("Error", "Failed to move event up.")


    def move_event_down(self):
        """선택된 단일 이벤트를 아래로 이동"""
        if hasattr(self, 'recorder') and self.recorder.recording:
            messagebox.showwarning("Warning", "Cannot edit events while recording.")
            return

        selected = self._get_valid_selected_indices()
        if len(selected) != 1:
            messagebox.showwarning("Warning", "Select exactly one event to move.")
            return

        current_index = selected[0]

        # 에디터의 이벤트 수 확인
        event_count = 0
        try:
            if hasattr(self.editor, 'get_event_count') and callable(self.editor.get_event_count):
                event_count = self.editor.get_event_count()
            elif hasattr(self.editor, 'get_events') and callable(self.editor.get_events):
                event_count = len(self.editor.get_events() or [])
            elif hasattr(self.editor, 'events'): # Fallback
                event_count = len(self.editor.events or [])
        except Exception: pass

        if current_index >= event_count - 1:
            messagebox.showinfo("Info", "Cannot move the last event further down.")
            return

        # 에디터에 이동 요청
        new_index = -1
        try:
            if hasattr(self.editor, 'move_event_down') and callable(self.editor.move_event_down):
                new_index = self.editor.move_event_down(current_index)
            elif hasattr(self.editor, 'events'): # Fallback
                if 0 <= current_index < len(self.editor.events) - 1:
                    self.editor.events.insert(current_index + 1, self.editor.events.pop(current_index))
                    new_index = current_index + 1
            else:
                messagebox.showerror("Error", "Editor does not support moving events.")
                return
        except Exception as e:
            messagebox.showerror("Error", f"Error moving event down: {e}")
            return

        if new_index != -1:
            self.restore_selection = False
            self.clear_selection()
            self.update_event_list()
            self.set_single_selection(new_index) # 이동된 위치 선택
            self.restore_selection = True
            self.update_status(f"Event moved down to position {new_index + 1}.")
        else:
            messagebox.showerror("Error", "Failed to move event down.")


    # --- Event Double Click (Placeholder) ---
    def on_event_double_click(self, event=None):
        """이벤트 리스트박스 더블클릭 시 동작 (예: 이벤트 수정 창 열기)"""
        selected = self._get_valid_selected_indices()
        if len(selected) == 1:
            index = selected[0]
            print(f"Event at index {index} double-clicked. (Placeholder for editing)")
            # TODO: 이벤트 수정 다이얼로그 열기 로직 추가
            messagebox.showinfo("Edit Event (Not Implemented)", f"Double-clicked event #{index+1}.\nEditing functionality is not yet implemented in this module.")
        else:
            print("Double-click ignored (no single event selected).")
