# gui_advanced_editor.py
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

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

    def add_mouse_move_event(self):
        """사용자 입력(절대/상대 좌표)을 받아 마우스 이동 이벤트를 현재 선택된 위치 또는 맨 끝에 추가"""
        if hasattr(self, 'recorder') and self.recorder.recording:
            messagebox.showwarning("Warning", "Cannot edit events while recording.")
            return

        if not hasattr(self, 'editor'):
            messagebox.showerror("Error", "Macro editor is not available.")
            return

        # --- 사용자 입력 대화상자 정의 ---
        dialog = tk.Toplevel(self.root)
        dialog.title("Add Mouse Move Event")
        dialog.geometry("350x200") # 창 크기 조절
        dialog.resizable(False, False)

        # 부모 창 중앙에 위치
        parent_x = self.root.winfo_x()
        parent_y = self.root.winfo_y()
        parent_width = self.root.winfo_width()
        parent_height = self.root.winfo_height()
        dialog_x = parent_x + (parent_width - 350) // 2
        dialog_y = parent_y + (parent_height - 200) // 2
        dialog.geometry(f"+{dialog_x}+{dialog_y}")

        dialog.transient(self.root) # 부모 창 위에 표시
        dialog.grab_set() # 모달 창으로 만듬

        coord_type_var = tk.StringVar(value="absolute") # 기본값: 절대 좌표
        x_var = tk.StringVar(value="0")
        y_var = tk.StringVar(value="0")

        # 좌표 타입 선택
        type_frame = ttk.Frame(dialog, padding=10)
        type_frame.pack(pady=5)
        ttk.Label(type_frame, text="Coordinate Type:").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(type_frame, text="Absolute", variable=coord_type_var, value="absolute").pack(side=tk.LEFT)
        ttk.Radiobutton(type_frame, text="Relative", variable=coord_type_var, value="relative").pack(side=tk.LEFT)

        # 좌표 입력
        coord_frame = ttk.Frame(dialog, padding=10)
        coord_frame.pack(pady=5)
        ttk.Label(coord_frame, text="X:").pack(side=tk.LEFT, padx=5)
        x_entry = ttk.Entry(coord_frame, textvariable=x_var, width=8)
        x_entry.pack(side=tk.LEFT, padx=5)
        ttk.Label(coord_frame, text="Y:").pack(side=tk.LEFT, padx=5)
        y_entry = ttk.Entry(coord_frame, textvariable=y_var, width=8)
        y_entry.pack(side=tk.LEFT, padx=5)

        result = {"x": None, "y": None, "is_relative": False, "cancelled": True}

        def on_ok():
            try:
                x_val = int(x_var.get())
                y_val = int(y_var.get())
                result["x"] = x_val
                result["y"] = y_val
                result["is_relative"] = (coord_type_var.get() == "relative")
                result["cancelled"] = False
                dialog.destroy()
            except ValueError:
                messagebox.showerror("Invalid Input", "Please enter valid integer coordinates.", parent=dialog)

        def on_cancel():
            result["cancelled"] = True
            dialog.destroy()

        # 확인/취소 버튼
        button_frame = ttk.Frame(dialog, padding=10)
        button_frame.pack(pady=10)
        ok_button = ttk.Button(button_frame, text="OK", command=on_ok)
        ok_button.pack(side=tk.LEFT, padx=10)
        cancel_button = ttk.Button(button_frame, text="Cancel", command=on_cancel)
        cancel_button.pack(side=tk.LEFT, padx=10)

        # Enter 키로 확인, Esc 키로 취소
        dialog.bind('<Return>', lambda event: on_ok())
        dialog.bind('<Escape>', lambda event: on_cancel())

        # 대화상자가 닫힐 때까지 대기
        dialog.wait_window()

        # --- 대화상자 종료 후 처리 ---
        if result["cancelled"]:
            self.update_status("Mouse move event addition cancelled.")
            return

        # 새 마우스 이동 이벤트 생성
        new_event = {
            'type': 'mouse',
            'event_type': 'move',
            'position': (result["x"], result["y"]),
            'is_relative': result["is_relative"], # 상대 좌표 여부 플래그 추가
            'button': None, # 이동 이벤트는 버튼 정보 없음
            'time': 0 # 시간은 삽입 시 에디터가 결정
        }

        # 삽입 위치 결정 (선택된 항목이 있으면 그 다음, 없으면 맨 끝)
        insert_index = -1 # 기본값: 맨 끝
        selected_indices = self._get_valid_selected_indices()
        if selected_indices:
            insert_index = max(selected_indices) + 1
            print(f"Inserting mouse move after index {max(selected_indices)}.")
        else:
            print("No selection, inserting mouse move at the end.")

        # 에디터에 삽입 요청
        try:
            inserted_idx = -1
            if hasattr(self.editor, 'insert_event') and callable(self.editor.insert_event):
                inserted_idx = self.editor.insert_event(insert_index, new_event)
            elif hasattr(self.editor, 'events') and insert_index != -1: # Fallback: 직접 삽입
                 self.editor.events.insert(insert_index, new_event)
                 inserted_idx = insert_index # 직접 삽입 시 인덱스 반환
            elif hasattr(self.editor, 'events'): # Fallback: 맨 끝에 추가
                 self.editor.events.append(new_event)
                 inserted_idx = len(self.editor.events) - 1
            else:
                 messagebox.showerror("Error", "Editor does not support event insertion.")
                 return

            if inserted_idx != -1:
                self.restore_selection = False # 삽입 후 선택 상태 유지 안 함
                self.clear_selection() # 선택 해제
                self.update_event_list() # 목록 갱신
                self.set_single_selection(inserted_idx) # 새로 추가된 항목 선택 및 표시
                self.restore_selection = True # 다음 업데이트부터 선택 유지
                coord_type_str = "Relative" if result["is_relative"] else "Absolute"
                self.update_status(f"{coord_type_str} mouse move event added at index {inserted_idx + 1}.")
            else:
                messagebox.showerror("Error", "Failed to add mouse move event.")

        except Exception as e:
            messagebox.showerror("Error", f"Error adding mouse move event: {e}")
