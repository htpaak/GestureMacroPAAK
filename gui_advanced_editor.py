# gui_advanced_editor.py
import tkinter as tk
from tkinter import messagebox, simpledialog

class GuiAdvancedEditorMixin:
    """GUI의 고급 이벤트 편집 기능 (딜레이 일괄 추가/삭제, 랜덤 딜레이/위치 추가)을 담당하는 믹스인 클래스"""

    # --- 의존성 메서드 (다른 믹스인에서 구현 필요) ---
    # def update_status(self, message): raise NotImplementedError # GuiBase
    # def update_event_list(self): raise NotImplementedError # GuiEventEditorMixin

    # --- 고급 편집 기능 ---

    def add_delay_between_all_events(self):
        """모든 이벤트 사이에 딜레이 추가 (Add Delay 버튼에서 전체 선택 시 호출)"""
        if hasattr(self, 'recorder') and self.recorder.recording:
            messagebox.showwarning("Warning", "Cannot edit events while recording.")
            return

        delay_ms = simpledialog.askinteger("Add Delay Between All Events",
                                           "Delay time (ms):",
                                           minvalue=1, maxvalue=600000)
        if delay_ms is None: return

        delay_sec = delay_ms / 1000.0
        print(f"Adding delay of {delay_ms}ms between non-delay events.")

        # 에디터에서 이벤트 가져오기
        events = []
        try:
            if hasattr(self.editor, 'get_events') and callable(self.editor.get_events):
                events = self.editor.get_events() or []
            elif hasattr(self.editor, 'events'): # Fallback
                events = self.editor.events or []
        except Exception as e:
            messagebox.showerror("Error", f"Could not get events from editor: {e}")
            return

        if len(events) < 2:
            messagebox.showinfo("Info", "Not enough events to add delay between.")
            return

        # 삽입할 위치 찾기 (기존 딜레이 제외)
        insert_positions = []
        for i in range(len(events) - 1, 0, -1):
            if events[i-1].get('type') != 'delay' and events[i].get('type') != 'delay':
                insert_positions.append(i)

        if not insert_positions:
            messagebox.showinfo("Info", "Delay already exists between all non-delay events.")
            return

        delay_event_template = {'type': 'delay', 'delay': delay_sec, 'time': 0}
        inserted_count = 0
        insert_success = False

        try:
            # 에디터에 삽입 요청 (insert_event 사용 또는 직접 조작)
            if hasattr(self.editor, 'insert_event') and callable(self.editor.insert_event):
                # insert_event는 단일 삽입만 지원할 수 있으므로 반복 호출
                # 인덱스 문제 방지를 위해 역순 삽입
                for i in sorted(insert_positions, reverse=True):
                    new_event = delay_event_template.copy()
                    if self.editor.insert_event(i, new_event) != -1:
                        inserted_count += 1
                if inserted_count == len(insert_positions): insert_success = True

            elif hasattr(self.editor, 'events'): # Fallback: 직접 삽입
                for i in sorted(insert_positions, reverse=True):
                    new_event = delay_event_template.copy()
                    # 시간 정보 설정 (선택 사항, 에디터가 처리하는 것이 나음)
                    # if i > 0 and 'time' in events[i-1]: new_event['time'] = events[i-1]['time'] + 0.001
                    self.editor.events.insert(i, new_event)
                    inserted_count += 1
                insert_success = True # 직접 삽입은 성공으로 간주
            else:
                messagebox.showerror("Error", "Editor does not support event insertion.")
                return

        except Exception as e:
            messagebox.showerror("Error", f"Error adding delays between events: {e}")
            return # 실패

        if insert_success and inserted_count > 0:
            self.restore_selection = False
            self.clear_selection()
            self.update_event_list()
            self.restore_selection = True
            self.update_status(f"Added {inserted_count} delay(s) of {delay_ms}ms between events.")
        elif inserted_count > 0: # 부분 성공?
            self.update_event_list()
            messagebox.showwarning("Warning", f"Only {inserted_count} out of {len(insert_positions)} delays could be added.")
        else:
            messagebox.showerror("Error", "Failed to add delays between events.")

    def delete_delay_events(self):
        """선택된 이벤트 중 딜레이 이벤트만 삭제"""
        if hasattr(self, 'recorder') and self.recorder.recording:
            messagebox.showwarning("Warning", "Cannot edit events while recording.")
            return

        indices_to_check = self._get_valid_selected_indices()
        if not indices_to_check:
            messagebox.showwarning("Warning", "Select event(s) to check for delays.")
            return

        # 에디터에서 이벤트 가져오기
        events = []
        try:
            if hasattr(self.editor, 'get_events') and callable(self.editor.get_events):
                events = self.editor.get_events() or []
            elif hasattr(self.editor, 'events'): # Fallback
                events = self.editor.events or []
        except Exception as e:
            messagebox.showerror("Error", f"Could not get events from editor: {e}")
            return

        # 선택된 인덱스 중 딜레이 이벤트만 필터링
        delay_indices_to_delete = [idx for idx in indices_to_check if 0 <= idx < len(events) and events[idx].get('type') == 'delay']

        if not delay_indices_to_delete:
            messagebox.showinfo("Info", "No delay events found in selection.")
            return

        if not messagebox.askyesno("Confirm Deletion", f"Delete {len(delay_indices_to_delete)} selected delay event(s)?"):
            return

        # 에디터에 삭제 요청
        deleted_count = 0
        try:
            if hasattr(self.editor, 'delete_events') and callable(self.editor.delete_events):
                deleted_count = self.editor.delete_events(delay_indices_to_delete)
            elif hasattr(self.editor, 'events'): # Fallback
                for idx in sorted(delay_indices_to_delete, reverse=True):
                    if 0 <= idx < len(self.editor.events): # 삭제 전 재확인
                        if self.editor.events[idx].get('type') == 'delay':
                            del self.editor.events[idx]
                            deleted_count += 1
            else:
                messagebox.showerror("Error", "Editor does not support event deletion.")
                return
        except Exception as e:
            messagebox.showerror("Error", f"Error deleting delay events: {e}")
            return

        if deleted_count > 0:
            self.restore_selection = False
            self.clear_selection()
            self.update_event_list()
            self.restore_selection = True
            self.update_status(f"{deleted_count} delay event(s) deleted.")
        else:
            messagebox.showerror("Error", "Failed to delete selected delay events.")

    def add_random_delay(self):
        """선택한 딜레이 이벤트에 랜덤 범위 추가/수정"""
        if hasattr(self, 'recorder') and self.recorder.recording:
            messagebox.showwarning("Warning", "Cannot edit events while recording.")
            return

        indices_to_check = self._get_valid_selected_indices()
        if not indices_to_check:
            messagebox.showwarning("Warning", "Select delay event(s) to add/modify random range.")
            return

        # 에디터 이벤트 가져오기
        events = []
        try:
            if hasattr(self.editor, 'get_events') and callable(self.editor.get_events):
                events = self.editor.get_events() or []
            elif hasattr(self.editor, 'events'): # Fallback
                events = self.editor.events or []
        except Exception as e:
            messagebox.showerror("Error", f"Could not get events from editor: {e}")
            return

        # 선택된 인덱스 중 딜레이 이벤트만 필터링
        delay_indices = [idx for idx in indices_to_check if 0 <= idx < len(events) and events[idx].get('type') == 'delay']

        if not delay_indices:
            messagebox.showwarning("Warning", "No delay events selected.")
            return

        # 첫 번째 선택된 딜레이의 현재 랜덤 범위 가져오기 (initialvalue용)
        current_random_ms = 0
        if 0 <= delay_indices[0] < len(events):
            current_random_ms = int(events[delay_indices[0]].get('random_range', 0) * 1000)

        # 새 랜덤 범위 입력
        new_random_ms = simpledialog.askinteger("Set Random Delay Range",
                                                "Random range ± (ms):\n(Enter 0 to remove randomness)",
                                                initialvalue=current_random_ms,
                                                minvalue=0, maxvalue=30000) # 0 ~ 30초
        if new_random_ms is None: return

        new_random_sec = new_random_ms / 1000.0

        # 에디터에 수정 요청
        modified_count = 0
        try:
            # 에디터에 전용 메서드가 있다면 사용 (예: modify_random_delay)
            if hasattr(self.editor, 'modify_random_delays') and callable(self.editor.modify_random_delays):
                modified_count = self.editor.modify_random_delays(delay_indices, new_random_sec)
            elif hasattr(self.editor, 'events'): # Fallback
                for idx in delay_indices:
                    if 0 <= idx < len(self.editor.events) and self.editor.events[idx]['type'] == 'delay':
                        if new_random_sec > 0:
                            self.editor.events[idx]['random_range'] = new_random_sec
                        elif 'random_range' in self.editor.events[idx]:
                            del self.editor.events[idx]['random_range'] # 0이면 랜덤 범위 제거
                        modified_count += 1
            else:
                messagebox.showerror("Error", "Editor does not support modifying random delays.")
                return
        except Exception as e:
            messagebox.showerror("Error", f"Error setting random delay range: {e}")
            return

        if modified_count > 0:
            self.restore_selection = True # 선택 유지
            self.update_event_list()
            if new_random_ms > 0:
                self.update_status(f"{modified_count} delay event(s) set to random range ±{new_random_ms}ms.")
            else:
                self.update_status(f"Random range removed from {modified_count} delay event(s).")
        else:
            messagebox.showerror("Error", "Failed to modify random delay range.")

    def add_random_position(self):
        """선택한 마우스 이벤트에 랜덤 좌표 범위 추가/수정"""
        if hasattr(self, 'recorder') and self.recorder.recording:
            messagebox.showwarning("Warning", "Cannot edit events while recording.")
            return
        
        # --- 디버깅 코드 추가 V5 ---
        print("--- Debugging V5: Checking selected indices ---")
        indices_to_check = None # 초기화
        assignment_error = None
        try:
            # _get_valid_selected_indices 호출 시도
            indices_to_check = self._get_valid_selected_indices()
            print(f"Call to _get_valid_selected_indices successful. Indices: {indices_to_check}")
        except Exception as e:
            print(f"ERROR during _get_valid_selected_indices call: {e}")
            import traceback
            traceback.print_exc() # 상세 트레이스백 출력
            assignment_error = e

        # 할당 오류 또는 유효하지 않은 인덱스 처리
        if assignment_error:
            messagebox.showerror("Error", f"Failed to get selected indices: {assignment_error}")
            return
        if indices_to_check is None: # _get_valid_selected_indices가 None을 반환했거나 예외 발생 (위에서 처리됨)
            messagebox.showwarning("Warning", "Could not determine selected events.")
            return
        if not indices_to_check: # 빈 리스트 반환 (선택된 항목 없음)
             messagebox.showwarning("Warning", "Select mouse event(s) to add/modify random position.")
             return

        # 에디터 이벤트 가져오기 (선택된 인덱스가 유효할 때만 진행)
        events = []
        try:
            if hasattr(self.editor, 'get_events') and callable(self.editor.get_events):
                events = self.editor.get_events() or []
            elif hasattr(self.editor, 'events'): # Fallback
                events = self.editor.events or []
            else:
                 raise RuntimeError("Editor has no way to get events.")
            print(f"Successfully retrieved {len(events)} events from editor.")
        except Exception as e:
            messagebox.showerror("Error", f"Could not get events from editor: {e}")
            return

        # 선택된 인덱스 중 마우스 이벤트만 필터링 (이제 indices_to_check는 유효함)
        print("Filtering for mouse events in selected indices:", indices_to_check)
        mouse_indices = []
        for idx in indices_to_check:
            if 0 <= idx < len(events):
                event_data = events[idx]
                event_type = event_data.get('type', 'N/A')
                print(f"  Index {idx}: Type='{event_type}'") # 타입 확인 로그
                if event_type == 'mouse':
                    mouse_indices.append(idx)
            else:
                 print(f"  Index {idx}: Invalid index for events list (len={len(events)})")
        # --- 디버깅 코드 끝 V5 ---

        if not mouse_indices:
            messagebox.showwarning("Warning", "No mouse events selected.") # 이제 이 메시지가 정확히 떠야 함
            return

        # ... (이후 랜덤 범위 설정 로직) ...

        # 첫 번째 선택된 이벤트의 현재 랜덤 범위 가져오기
        current_random_pixels = 0
        if 0 <= mouse_indices[0] < len(events):
            current_random_pixels = int(events[mouse_indices[0]].get('random_range', 0))

        # 새 랜덤 범위 입력
        new_random_pixels = simpledialog.askinteger("Set Random Position Range",
                                                    "Random position range ± (pixels):\n(Enter 0 to remove randomness)",
                                                    initialvalue=current_random_pixels,
                                                    minvalue=0, maxvalue=1000)
        if new_random_pixels is None: return

        # 에디터에 수정 요청
        modified_count = 0
        try:
            if hasattr(self.editor, 'modify_random_positions') and callable(self.editor.modify_random_positions):
                modified_count = self.editor.modify_random_positions(mouse_indices, new_random_pixels)
            elif hasattr(self.editor, 'events'): # Fallback
                for idx in mouse_indices:
                    # 마우스 이벤트 타입 확인 수정
                    if 0 <= idx < len(self.editor.events) and self.editor.events[idx].get('type') == 'mouse':
                        if new_random_pixels > 0:
                            self.editor.events[idx]['random_range'] = new_random_pixels
                        elif 'random_range' in self.editor.events[idx]:
                            del self.editor.events[idx]['random_range']
                        modified_count += 1
            else:
                messagebox.showerror("Error", "Editor does not support modifying random positions.")
                return
        except Exception as e:
            messagebox.showerror("Error", f"Error setting random position range: {e}")
            return

        if modified_count > 0:
            self.restore_selection = True
            self.update_event_list()
            if new_random_pixels > 0:
                self.update_status(f"{modified_count} mouse event(s) set to random position range ±{new_random_pixels} pixels.")
            else:
                self.update_status(f"Random position range removed from {modified_count} mouse event(s).")
        else:
            messagebox.showerror("Error", "Failed to modify random position range.")
