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
            if hasattr(self, 'recorder') and self.recorder.recording: return # 녹화 중 선택 무시

            selected = self.event_listbox.curselection()
            self.selected_events = list(selected) # 내부 선택 상태 업데이트

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
                except Exception: pass # 오류 무시
                self.update_status(f"Event #{idx+1} selected (Type: {event_type})")
            elif count > 1:
                self.update_status(f"{count} events selected")
            # else: # 선택 해제 시 (curselection이 비어있으면 호출 안될 수 있음)
            #     self.update_status("Selection cleared.")


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
            if not hasattr(self, 'selected_events') or not self.selected_events:
                # 리스트박스 직접 확인 (Fallback)
                if hasattr(self, 'event_listbox'):
                    selected = self.event_listbox.curselection()
                    if selected: self.selected_events = list(selected)
                    else: return []
                else: return []

            # 에디터의 현재 이벤트 수 확인
            event_count = 0
            try:
                if hasattr(self.editor, 'get_event_count') and callable(self.editor.get_event_count):
                    event_count = self.editor.get_event_count()
                elif hasattr(self.editor, 'get_events') and callable(self.editor.get_events):
                    event_count = len(self.editor.get_events() or [])
                elif hasattr(self.editor, 'events'): # Fallback
                    event_count = len(self.editor.events or [])
            except Exception: pass

            # 유효한 인덱스만 필터링
            valid_indices = [idx for idx in self.selected_events if 0 <= idx < event_count]
            if len(valid_indices) != len(self.selected_events):
                print(f"Warning: Some selected indices were invalid. Original: {self.selected_events}, Valid: {valid_indices}")
                self.selected_events = valid_indices # 내부 상태 업데이트

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
            """선택된 이벤트 *아래*에 딜레이 추가"""
            if hasattr(self, 'recorder') and self.recorder.recording:
                messagebox.showwarning("Warning", "Cannot edit events while recording.")
                return

            selected = self._get_valid_selected_indices()
            if not selected:
                messagebox.showwarning("Warning", "Select the event *before* where you want to add delay.")
                return

            # 여러 개 선택 시 마지막 선택 위치 기준
            insert_index = max(selected) + 1

            delay_ms = simpledialog.askinteger("Add Delay", "Delay time (ms):",
                                               minvalue=1, maxvalue=600000) # 1ms ~ 10분
            if delay_ms is None: return

            delay_sec = delay_ms / 1000.0
            delay_event = {'type': 'delay', 'delay': delay_sec, 'time': 0} # 시간은 에디터가 처리

            # 에디터에 삽입 요청
            inserted_idx = -1
            try:
                if hasattr(self.editor, 'insert_event') and callable(self.editor.insert_event):
                    inserted_idx = self.editor.insert_event(insert_index, delay_event)
                elif hasattr(self.editor, 'events'): # Fallback
                    if 0 <= insert_index <= len(self.editor.events):
                        self.editor.events.insert(insert_index, delay_event)
                        inserted_idx = insert_index
                else:
                    messagebox.showerror("Error", "Editor does not support event insertion.")
                    return
            except Exception as e:
                messagebox.showerror("Error", f"Error adding delay: {e}")
                return

            if inserted_idx != -1:
                self.restore_selection = False
                self.clear_selection()
                self.update_event_list()
                self.set_single_selection(inserted_idx) # 새로 추가된 딜레이 선택
                self.restore_selection = True
                self.update_status(f"{delay_ms}ms delay added at position {inserted_idx + 1}.")
            else:
                messagebox.showerror("Error", "Failed to add delay.")


        def modify_delay_time(self):
            """선택된 딜레이 이벤트의 시간 수정"""
            if hasattr(self, 'recorder') and self.recorder.recording:
                messagebox.showwarning("Warning", "Cannot edit events while recording.")
                return

            indices_to_modify = self._get_valid_selected_indices()
            if not indices_to_modify:
                messagebox.showwarning("Warning", "Select delay event(s) to modify.")
                return

            # 선택된 것 중 실제 딜레이 이벤트만 필터링
            delay_indices = []
            try:
                events = []
                if hasattr(self.editor, 'get_events') and callable(self.editor.get_events):
                    events = self.editor.get_events() or []
                elif hasattr(self.editor, 'events'): # Fallback
                    events = self.editor.events or []

                for idx in indices_to_modify:
                    if 0 <= idx < len(events) and events[idx].get('type') == 'delay':
                        delay_indices.append(idx)
            except Exception: pass

            if not delay_indices:
                messagebox.showwarning("Warning", "No delay events selected.")
                return

            # 새 딜레이 시간 입력
            # 첫 번째 선택된 딜레이의 현재 값 보여주기 (선택 사항)
            current_delay_ms = 0
            if events and 0 <= delay_indices[0] < len(events):
                current_delay_ms = int(events[delay_indices[0]].get('delay', 0) * 1000)

            new_delay_ms = simpledialog.askinteger("Modify Delay", "New delay time (ms):",
                                                   initialvalue=current_delay_ms,
                                                   minvalue=1, maxvalue=600000)
            if new_delay_ms is None: return

            new_delay_sec = new_delay_ms / 1000.0

            # 에디터에 수정 요청
            modified_count = 0
            try:
                if hasattr(self.editor, 'modify_delays') and callable(self.editor.modify_delays):
                    modified_count = self.editor.modify_delays(delay_indices, new_delay_sec)
                elif hasattr(self.editor, 'events'): # Fallback
                    for idx in delay_indices:
                        if 0 <= idx < len(self.editor.events) and self.editor.events[idx]['type'] == 'delay':
                            self.editor.events[idx]['delay'] = new_delay_sec
                            # 랜덤 범위가 있다면 제거하거나 유지하는 정책 필요
                            if 'random_range' in self.editor.events[idx]:
                                print(f"Warning: Modifying delay at index {idx} might affect existing random range.")
                                # del self.editor.events[idx]['random_range'] # 예: 랜덤 범위 제거
                            modified_count += 1
                else:
                    messagebox.showerror("Error", "Editor does not support delay modification.")
                    return
            except Exception as e:
                messagebox.showerror("Error", f"Error modifying delays: {e}")
                return

            if modified_count > 0:
                self.restore_selection = True # 수정 후 선택 유지
                self.update_event_list() # 목록 업데이트 (선택 복원됨)
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
