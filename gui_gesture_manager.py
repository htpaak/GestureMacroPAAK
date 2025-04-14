# gui_gesture_manager.py
import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
import os
import copy
import json

class GuiGestureManagerMixin:
    """GUI의 제스처 목록 관리(업데이트, 선택, 편집, 삭제, 이동) 및 이벤트 목록 연동을 담당하는 믹스인 클래스"""

    def update_status(self, message):
        """하단 상태 표시줄 업데이트 (구현은 gui_base.py에서)"""
        raise NotImplementedError

    def update_event_list(self):
        """이벤트 목록 업데이트 (GuiEventEditorMixin에 구현)"""
        raise NotImplementedError

    def clear_selection(self):
        """이벤트 목록 선택 해제 (GuiEventEditorMixin에 구현)"""
        raise NotImplementedError

    def display_event(self, event, index):
        """단일 이벤트 표시 (GuiEventEditorMixin에 구현)"""
        raise NotImplementedError

    def _get_internal_gesture_key(self, display_name):
        """UI 표시 이름으로부터 내부 제스처 키 찾기"""
        if not hasattr(self, 'gesture_manager') or not self.gesture_manager: return display_name # Fallback
        # 매핑에서 역변환 시도
        for internal_key, macro_file in self.gesture_manager.get_mappings().items():
            # 내부 키를 표시 이름으로 변환
            temp_display_name = internal_key.replace("A-", "Alt-").replace("AT", "Alt").replace("CT-", "Ctrl-")
            if temp_display_name == display_name:
                return internal_key
        # 못 찾으면 그냥 반환 (오류 가능성)
        print(f"Warning: Could not find internal key for display name '{display_name}'. Using display name itself.")
        return display_name

    def _get_display_gesture_name(self, internal_key):
        """내부 제스처 키로부터 UI 표시 이름 생성"""
        display_name = internal_key.replace("A-", "Alt-").replace("AT", "Alt").replace("CT-", "Ctrl-")
        return display_name

    def update_gesture_list(self):
        """제스처 목록 리스트박스를 현재 제스처 매핑으로 업데이트"""
        if not hasattr(self, 'gesture_listbox') or not hasattr(self, 'gesture_manager'): return

        # 현재 선택된 제스처 (내부 키 기준) 기억
        selected_internal_key = None
        if hasattr(self, 'selected_gesture_name') and self.selected_gesture_name:
            # selected_gesture_name이 내부 키라고 가정
            selected_internal_key = self.selected_gesture_name

        self.gesture_listbox.delete(0, tk.END)

        # 제스처 목록 (내부 키 기준) 가져와서 표시 이름으로 변환하여 추가
        new_selection_index = -1
        gestures_internal = list(self.gesture_manager.get_mappings().keys()) # 내부 키 리스트

        for idx, internal_key in enumerate(gestures_internal):
            display_name = self._get_display_gesture_name(internal_key)
            self.gesture_listbox.insert(tk.END, display_name)
            if internal_key == selected_internal_key:
                new_selection_index = idx # 이전에 선택된 항목의 새 인덱스

        # 이전 선택 복원 (새 인덱스 기준)
        if new_selection_index != -1:
            self.gesture_listbox.selection_clear(0, tk.END)
            self.gesture_listbox.selection_set(new_selection_index)
            self.gesture_listbox.see(new_selection_index)
            self.selected_gesture_index = new_selection_index
            # self.selected_gesture_name = selected_internal_key # 내부 이름은 이미 유지됨
            print(f"Gesture selection restored: {selected_internal_key} at index {new_selection_index}")
            # 제스처 선택 시 이벤트 목록 업데이트
            self.update_event_list_for_gesture(selected_internal_key)
        else:
            # 이전에 선택된 것이 없거나 목록에서 사라졌다면 선택 해제
            self.selected_gesture_index = None
            self.selected_gesture_name = None
            # 이벤트 목록도 비우기
            if hasattr(self, 'event_listbox'): self.event_listbox.delete(0, tk.END)
            if hasattr(self, 'editor') and hasattr(self.editor, 'events'): self.editor.events = []

    def on_gesture_select(self, event=None):
        """제스처 리스트박스에서 항목 선택 시 호출"""
        if not hasattr(self, 'gesture_listbox'): return
        if hasattr(self, '_skip_selection') and self._skip_selection: return

        selected_indices = self.gesture_listbox.curselection()
        if not selected_indices:
            # 선택 해제된 경우 (예: 빈 곳 클릭) - 이벤트 목록 비우기 등 처리 필요?
            # print("Gesture selection cleared.")
            # self.selected_gesture_index = None
            # self.selected_gesture_name = None
            # if hasattr(self, 'event_listbox'): self.event_listbox.delete(0, tk.END)
            # if hasattr(self, 'editor'): self.editor.events = []
            return

        selected_index = selected_indices[0]
        selected_display_name = self.gesture_listbox.get(selected_index)

        # 표시 이름으로부터 내부 키 가져오기
        selected_internal_key = self._get_internal_gesture_key(selected_display_name)

        # 이전 선택과 동일하면 처리 중복 방지
        if hasattr(self, 'selected_gesture_name') and self.selected_gesture_name == selected_internal_key:
            print(f"Same gesture '{selected_internal_key}' selected again. Skipping update.")
            return

        # 내부 상태 업데이트 (내부 키 기준)
        self.selected_gesture_index = selected_index
        self.selected_gesture_name = selected_internal_key # 내부 키 저장

        print(f"Gesture selected: '{selected_internal_key}' (Display: '{selected_display_name}') at index {selected_index}")

        # 이벤트 관련 상태 초기화
        self.selected_events = []
        if hasattr(self, 'clear_selection'): self.clear_selection() # 이벤트 리스트박스 선택 해제
        # 에디터 이벤트도 초기화 (선택된 제스처의 매크로를 로드하기 전에)
        if hasattr(self, 'editor'):
            if hasattr(self.editor, 'load_events'): self.editor.load_events([])
            elif hasattr(self.editor, 'events'): self.editor.events = []
            # 현재 편집 중인 매크로 이름도 초기화
            if hasattr(self.editor, 'set_current_macro'): self.editor.set_current_macro(None)

        # 선택된 제스처에 연결된 이벤트 목록 업데이트
        self.update_event_list_for_gesture(selected_internal_key)

    def update_event_list_for_gesture(self, gesture_internal_key):
        """주어진 제스처(내부 키)에 해당하는 이벤트 목록을 로드하고 표시"""
        # storage 객체 확인
        if not hasattr(self, 'storage'):
             print("Error: storage object not found.")
             if hasattr(self, 'update_status'): self.update_status("Error: Storage is not available.")
             return

        if not gesture_internal_key:
            if hasattr(self, 'event_listbox'): self.event_listbox.delete(0, tk.END)
            return

        print(f"Updating event list for gesture: {gesture_internal_key}")

        # gesture_manager 대신 storage 객체에서 매크로 로드
        # events = self.gesture_manager.get_macro_for_gesture(gesture_internal_key)
        events = self.storage.load_macro(gesture_internal_key) # 수정된 부분

        if events is None: # 매핑은 있으나 매크로 파일이 없는 경우 등 (빈 리스트와 구분)
            print(f"No macro file found or error loading for gesture: {gesture_internal_key}")
            display_name = self._get_display_gesture_name(gesture_internal_key)
            self.update_status(f"Macro for gesture '{display_name}' not found or invalid.")
            if hasattr(self, 'event_listbox'):
                self.event_listbox.delete(0, tk.END)
                self.event_listbox.insert(tk.END, f"♦ Macro file not found for gesture '{display_name}'.")
                self.event_listbox.itemconfig(tk.END, {'bg': '#FFE0E0'})
            # 에디터도 비우기
            if hasattr(self, 'editor'):
                if hasattr(self.editor, 'load_events'): self.editor.load_events([])
                elif hasattr(self.editor, 'events'): self.editor.events = []
                if hasattr(self.editor, 'set_current_macro'): self.editor.set_current_macro(None)
            return

        # 에디터에 로드된 이벤트 설정
        editor_updated = False
        if hasattr(self, 'editor'):
            try:
                if hasattr(self.editor, 'load_events') and callable(self.editor.load_events):
                    self.editor.load_events(copy.deepcopy(events)) # 에디터용 복사본
                    editor_updated = True
                elif hasattr(self.editor, 'events'): # Fallback
                    self.editor.events = copy.deepcopy(events)
                    editor_updated = True

                # 현재 편집 중인 매크로 이름 설정 (내부 키 사용)
                if hasattr(self.editor, 'set_current_macro') and callable(self.editor.set_current_macro):
                    self.editor.set_current_macro(gesture_internal_key)
                elif hasattr(self.editor, 'current_editing_macro'): # Fallback
                    self.editor.current_editing_macro = gesture_internal_key

            except Exception as e:
                print(f"Error setting events in editor: {e}")

        # 이벤트 목록 UI 업데이트
        if hasattr(self, 'event_listbox'):
            self.event_listbox.delete(0, tk.END)
            if not events: # 빈 매크로
                display_name = self._get_display_gesture_name(gesture_internal_key)
                self.event_listbox.insert(tk.END, f"♦ No events recorded for gesture '{display_name}'.")
                self.event_listbox.insert(tk.END, "♦ Click 'Record Macro' to add events.")
                for i in range(2): self.event_listbox.itemconfig(i, {'bg': '#FFFFD0'})
                self.update_status(f"Gesture '{display_name}' has an empty macro.")
            else: # 이벤트 표시
                for i, event in enumerate(events):
                    if hasattr(self, 'display_event'): self.display_event(event, i)
                if events: self.event_listbox.see(0)
                display_name = self._get_display_gesture_name(gesture_internal_key)
                self.update_status(f"Loaded {len(events)} events for gesture '{display_name}'.")
        else:
            print("Warning: event_listbox not found for displaying events.")

    def delete_selected_gesture(self):
        """선택된 제스처(들) 삭제"""
        if not hasattr(self, 'gesture_listbox') or not hasattr(self, 'gesture_manager'): return

        selected_indices = list(self.gesture_listbox.curselection())
        if not selected_indices:
            messagebox.showwarning("Warning", "Select gesture(s) to delete.")
            return

        confirm_msg = f"Delete {len(selected_indices)} selected gesture(s)?\nAssociated macros will also be removed."
        if not messagebox.askyesno("Confirm Deletion", confirm_msg):
            return

        deleted_count = 0
        gestures_to_delete = []
        # 먼저 삭제할 제스처 키 목록 만들기
        for index in selected_indices:
            display_name = self.gesture_listbox.get(index)
            internal_key = self._get_internal_gesture_key(display_name)
            gestures_to_delete.append(internal_key)

        # GestureManager에 삭제 요청
        for internal_key in gestures_to_delete:
            try:
                if self.gesture_manager.remove_mapping(internal_key): # 매핑 제거 (매크로 파일 삭제 포함 가정)
                    deleted_count += 1
            except Exception as e:
                print(f"Error removing gesture '{internal_key}': {e}")
                messagebox.showerror("Error", f"Could not delete gesture '{internal_key}'.")

        if deleted_count > 0:
            print(f"{deleted_count} gestures deleted.")
            # 선택 상태 초기화
            self.selected_gesture_index = None
            self.selected_gesture_name = None
            # 이벤트 목록 및 에디터 초기화
            if hasattr(self, 'event_listbox'): self.event_listbox.delete(0, tk.END)
            if hasattr(self, 'editor'):
                if hasattr(self.editor, 'load_events'): self.editor.load_events([])
                elif hasattr(self.editor, 'events'): self.editor.events = []
                if hasattr(self.editor, 'set_current_macro'): self.editor.set_current_macro(None)
            # 제스처 목록 새로고침
            self.update_gesture_list()
            self.update_status(f"{deleted_count} gesture(s) deleted.")
        else:
            print("No gestures were deleted.")

    def edit_gesture(self):
        """선택된 단일 제스처 수정 시작 (새 제스처 녹화) - 추출된 로직 적용"""
        if not hasattr(self, 'gesture_listbox') or not hasattr(self, 'gesture_manager'):
             print("Error: gesture_listbox or gesture_manager not found.")
             return

        selected_indices = self.gesture_listbox.curselection()
        if len(selected_indices) != 1:
            messagebox.showwarning("Warning", "Select exactly one gesture to edit.")
            return

        gesture_index = selected_indices[0]
        selected_display_name = self.gesture_listbox.get(gesture_index)
        selected_internal_key = self._get_internal_gesture_key(selected_display_name)

        # 매핑 존재 확인
        current_mappings = self.gesture_manager.get_mappings()
        if selected_internal_key not in current_mappings:
            messagebox.showerror("Error", f"Could not find mapping for gesture '{selected_internal_key}'. Cannot edit.")
            return

        macro_file_name = current_mappings[selected_internal_key]

        if not messagebox.askyesno("Edit Gesture", f"Record a new gesture to replace '{selected_display_name}'?\nThe associated macro will be kept."):
            return

        # 제스처 인식 활성화 확인 및 요청
        if not hasattr(self, 'gesture_enabled') or not self.gesture_enabled.get():
            if messagebox.askyesno("Activate Gesture Recognition",
                                   "Gesture recognition must be active to record gestures.\nActivate now?"):
                if not hasattr(self, 'gesture_enabled'): self.gesture_enabled = tk.BooleanVar(value=True)
                else: self.gesture_enabled.set(True)

                if hasattr(self, 'toggle_gesture_recognition') and callable(self.toggle_gesture_recognition):
                    self.toggle_gesture_recognition()
                    # 인식 활성화 대기 (필요시)
                    # self.root.after(100, lambda: self._proceed_with_edit(selected_internal_key, macro_file_name)) # 예시
                    # return # 바로 진행하지 않고 대기 후 진행
                else:
                    messagebox.showerror("Error", "Cannot toggle gesture recognition.")
                    return
            else:
                 return # 활성화 거부 시 중단

        # --- 제스처 편집 시작 로직 (이전 코드 기반) ---
        try:
            # 편집 상태 정보 저장
            self.edit_gesture_info = {
                "old_internal_key": selected_internal_key,
                "macro_file_name": macro_file_name
            }

            # GestureManager에 콜백 설정 (편집 완료 시 호출)
            if hasattr(self.gesture_manager, 'set_gesture_callback') and callable(self.on_gesture_edit_complete):
                self.gesture_manager.set_gesture_callback(self.on_gesture_edit_complete)
                print("Gesture edit callback set.")
            else:
                print("Warning: Cannot set gesture callback on GestureManager.")
                # 콜백 설정 실패 시 진행 중단?
                # raise Exception("Failed to set gesture callback for edit.")

            # 기존 매핑 임시 제거 (선택 사항, GestureManager 내부 처리 권장)
            # self.gesture_manager.gesture_mappings.pop(selected_internal_key, None)

            # GestureManager 녹화 모드 활성화 (메소드 호출 대신)
            if hasattr(self.gesture_manager, 'recording_mode'):
                self.gesture_manager.recording_mode = True
                print("GestureManager recording_mode set to True.")
            else:
                print("Warning: Cannot set recording_mode on GestureManager.")
                # raise Exception("GestureManager does not support recording_mode attribute.")

            # GestureManager 시각화 창 생성 (메소드 호출)
            if hasattr(self.gesture_manager, 'create_gesture_canvas') and callable(self.gesture_manager.create_gesture_canvas):
                self.gesture_manager.create_gesture_canvas()
                print("Gesture canvas created.")
            else:
                print("Warning: Cannot create gesture canvas via GestureManager.")
                # raise Exception("GestureManager does not support create_gesture_canvas method.")

            self.editing_gesture = True # 내부 편집 플래그
            if hasattr(self, 'update_status'): self.update_status(f"Editing gesture '{selected_display_name}'. Draw the new gesture.")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to start gesture recording for editing: {e}")
            # 실패 시 편집 정보 정리
            if hasattr(self, 'edit_gesture_info'): delattr(self, 'edit_gesture_info')
            if hasattr(self, 'editing_gesture'): self.editing_gesture = False
            # GestureManager 콜백도 초기화?
            if hasattr(self.gesture_manager, 'set_gesture_callback'):
                 self.gesture_manager.set_gesture_callback(None)

    def on_gesture_edit_complete(self, new_gesture_internal_key):
        """Callback from GestureManager when gesture editing is complete (extracted code)."""
        if not (hasattr(self, 'editing_gesture') and self.editing_gesture and hasattr(self, 'edit_gesture_info')):
            print("Warning: on_gesture_edit_complete called unexpectedly.")
            return

        print(f"Gesture edit complete. New gesture key: {new_gesture_internal_key}")
        old_internal_key = self.edit_gesture_info["old_internal_key"]
        macro_file_name = self.edit_gesture_info["macro_file_name"]

        # Check if the new gesture key already exists (excluding the old key itself)
        current_mappings = self.gesture_manager.get_mappings()
        if new_gesture_internal_key != old_internal_key and new_gesture_internal_key in current_mappings:
            new_display_name = self._get_display_gesture_name(new_gesture_internal_key)
            old_display_name = self._get_display_gesture_name(old_internal_key)
            messagebox.showwarning("Duplicate Gesture", f"The new gesture '{new_display_name}' is already mapped.\nEdit cancelled. Restoring original gesture '{old_display_name}'.")
            # Restore original mapping if it was temporarily removed
            # self.gesture_manager.gesture_mappings[old_internal_key] = macro_file_name
            # self.gesture_manager.save_mappings() # Assuming this is handled by GestureManager if needed
            if hasattr(self, 'update_gesture_list'): self.update_gesture_list()
        else:
            # Update mapping: remove old, add new (or let GestureManager handle update)
            try:
                # Assuming GestureManager has an update_mapping method
                if hasattr(self.gesture_manager, 'update_mapping'):
                    success = self.gesture_manager.update_mapping(old_internal_key, new_gesture_internal_key, macro_file_name)
                else:
                    # Fallback: Manually remove old and add new (less ideal)
                    print("Warning: GestureManager has no update_mapping method. Attempting manual update.")
                    if hasattr(self.gesture_manager, 'remove_mapping') and hasattr(self.gesture_manager, 'add_mapping'):
                         self.gesture_manager.remove_mapping(old_internal_key) # Assume this also saves
                         self.gesture_manager.add_mapping(new_gesture_internal_key, macro_file_name) # Assume this also saves
                         success = True # Assume success if no exceptions
                    else:
                         success = False
                         print("Error: Cannot manually update mapping.")

                if success:
                    new_display_name = self._get_display_gesture_name(new_gesture_internal_key)
                    old_display_name = self._get_display_gesture_name(old_internal_key)
                    if hasattr(self, 'update_gesture_list'): self.update_gesture_list()
                    if hasattr(self, 'update_status'): self.update_status(f"Gesture '{old_display_name}' changed to '{new_display_name}'.")
                    messagebox.showinfo("Gesture Edit Complete", f"Gesture changed from '{old_display_name}' to '{new_display_name}'.")
                else:
                    messagebox.showerror("Error", "Failed to update gesture mapping.")
                    # Attempt to restore?
                    if hasattr(self, 'update_gesture_list'): self.update_gesture_list()

            except Exception as e:
                 print(f"Error during gesture mapping update: {e}")
                 messagebox.showerror("Error", f"An error occurred while updating gesture mapping: {e}")
                 # Ensure list is updated even on error
                 if hasattr(self, 'update_gesture_list'): self.update_gesture_list()

        # Clean up edit state
        self.editing_gesture = False
        if hasattr(self, 'edit_gesture_info'): delattr(self, 'edit_gesture_info')
        # Reset GestureManager callback? (Might be handled by GestureManager itself)
        # if hasattr(self.gesture_manager, 'set_gesture_callback'):
        #      self.gesture_manager.set_gesture_callback(None)

    def move_gesture_up(self):
        """선택된 단일 제스처를 목록 위로 이동"""
        if not hasattr(self, 'gesture_listbox') or not hasattr(self, 'gesture_manager'): return

        selected_indices = self.gesture_listbox.curselection()
        if len(selected_indices) != 1:
            messagebox.showwarning("Warning", "Select exactly one gesture to move.")
            return

        current_index = selected_indices[0]
        if current_index == 0:
            messagebox.showinfo("Info", "Cannot move the first gesture further up.")
            return

        # GestureManager에 순서 변경 요청
        gestures_internal = list(self.gesture_manager.get_mappings().keys())
        if not (0 < current_index < len(gestures_internal)): return # 인덱스 오류 방지

        gesture_to_move = gestures_internal[current_index]

        try:
            if self.gesture_manager.move_gesture(gesture_to_move, current_index - 1):
                # 성공 시 목록 업데이트 및 새 위치 선택
                new_index = current_index - 1
                self.update_gesture_list() # 목록 업데이트 (선택 복원 로직 내장)
                # update_gesture_list에서 선택 복원이 안될 경우 대비
                if self.gesture_listbox.curselection() != (new_index,):
                    self._skip_selection = True
                    self.gesture_listbox.selection_clear(0, tk.END)
                    self.gesture_listbox.selection_set(new_index)
                    self.gesture_listbox.see(new_index)
                    self._skip_selection = False
                    self.selected_gesture_index = new_index
                    self.selected_gesture_name = gesture_to_move # 내부 키 저장
                    self.update_event_list_for_gesture(gesture_to_move) # 이벤트 목록도 업데이트

                display_name = self._get_display_gesture_name(gesture_to_move)
                self.update_status(f"Gesture '{display_name}' moved up.")
            else:
                messagebox.showerror("Error", "Failed to move gesture up in GestureManager.")
        except Exception as e:
            messagebox.showerror("Error", f"Error moving gesture up: {e}")

    def move_gesture_down(self):
        """선택된 단일 제스처를 목록 아래로 이동"""
        if not hasattr(self, 'gesture_listbox') or not hasattr(self, 'gesture_manager'): return

        selected_indices = self.gesture_listbox.curselection()
        if len(selected_indices) != 1:
            messagebox.showwarning("Warning", "Select exactly one gesture to move.")
            return

        current_index = selected_indices[0]
        gestures_internal = list(self.gesture_manager.get_mappings().keys())
        if current_index >= len(gestures_internal) - 1:
            messagebox.showinfo("Info", "Cannot move the last gesture further down.")
            return
        if not (0 <= current_index < len(gestures_internal) -1): return # 인덱스 오류 방지

        gesture_to_move = gestures_internal[current_index]

        try:
            if self.gesture_manager.move_gesture(gesture_to_move, current_index + 1):
                # 성공 시 목록 업데이트 및 새 위치 선택
                new_index = current_index + 1
                self.update_gesture_list()
                if self.gesture_listbox.curselection() != (new_index,):
                    self._skip_selection = True
                    self.gesture_listbox.selection_clear(0, tk.END)
                    self.gesture_listbox.selection_set(new_index)
                    self.gesture_listbox.see(new_index)
                    self._skip_selection = False
                    self.selected_gesture_index = new_index
                    self.selected_gesture_name = gesture_to_move
                    self.update_event_list_for_gesture(gesture_to_move)

                display_name = self._get_display_gesture_name(gesture_to_move)
                self.update_status(f"Gesture '{display_name}' moved down.")
            else:
                messagebox.showerror("Error", "Failed to move gesture down in GestureManager.")
        except Exception as e:
            messagebox.showerror("Error", f"Error moving gesture down: {e}")

    # --- Gesture Selection Maintenance ---

    def maintain_gesture_selection(self, event=None):
        """제스처 리스트박스에서 포커스 잃을 때 선택 유지 시도"""
        if not hasattr(self, 'gesture_listbox'): return
        # 현재 선택된 인덱스가 있으면 내부 변수에 저장된 것과 비교/업데이트?
        # 또는 단순히 현재 선택을 다시 설정? (원본 로직과 유사하게)
        current_selection = self.gesture_listbox.curselection()
        if current_selection:
            # 선택이 있으면 그대로 두거나, 내부 변수와 동기화
            idx = current_selection[0]
            display_name = self.gesture_listbox.get(idx)
            internal_key = self._get_internal_gesture_key(display_name)
            self.selected_gesture_index = idx
            self.selected_gesture_name = internal_key # 내부 변수 업데이트
        elif self.selected_gesture_index is not None: # 선택이 없고 내부 변수에 값이 있으면 복원 시도
            try:
                if 0 <= self.selected_gesture_index < self.gesture_listbox.size():
                    self._skip_selection = True
                    self.gesture_listbox.selection_set(self.selected_gesture_index)
                    self._skip_selection = False
            except tk.TclError: pass # 위젯 파괴 등

    def ensure_gesture_selection(self, event=None):
        """(루트 윈도우 클릭 시 등) 제스처 선택이 유지되도록 확인 및 복원"""
        if not hasattr(self, 'gesture_listbox'): return
        # 리스트박스에 현재 선택이 없고, 내부적으로 선택된 제스처가 있으면 복원
        if not self.gesture_listbox.curselection() and self.selected_gesture_index is not None:
            try:
                if 0 <= self.selected_gesture_index < self.gesture_listbox.size():
                    self._skip_selection = True
                    self.gesture_listbox.selection_set(self.selected_gesture_index)
                    # self.gesture_listbox.see(self.selected_gesture_index) # 스크롤은 불필요할 수 있음
                    self._skip_selection = False
            except tk.TclError: pass

    def _create_gesture_list_widgets(self, parent_frame):
        """제스처 목록 관련 위젯 생성 (추출된 코드)"""
        # 제스처 목록 프레임 (parent_frame은 gui_setup에서 전달된 left_frame)
        gesture_frame = ttk.LabelFrame(parent_frame, text="Gesture List", padding=10) # UI 텍스트 영어로
        gesture_frame.pack(fill=tk.BOTH, expand=True)

        # 제스처 리스트박스 및 스크롤바
        gesture_scrollbar = ttk.Scrollbar(gesture_frame)
        gesture_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 필요한 속성 확인 및 초기화
        if not hasattr(self, 'gesture_listbox'): self.gesture_listbox = None
        if not hasattr(self, 'repeat_count'): self.repeat_count = tk.StringVar(value="1")
        if not hasattr(self, 'infinite_repeat'): self.infinite_repeat = tk.BooleanVar(value=False)

        self.gesture_listbox = tk.Listbox(gesture_frame, font=('Consolas', 11), height=15,
                                         selectmode=tk.EXTENDED,
                                         exportselection=False)
        self.gesture_listbox.pack(fill=tk.BOTH, expand=True)
        self.gesture_listbox.config(yscrollcommand=gesture_scrollbar.set,
                                   selectbackground='#4a6cd4',
                                   selectforeground='white')
        gesture_scrollbar.config(command=self.gesture_listbox.yview)

        # 이벤트 바인딩 (콜백은 이 Mixin 또는 GuiBase에 있어야 함)
        on_select_cmd = getattr(self, 'on_gesture_select', lambda e: print("on_gesture_select not found"))
        maintain_selection_cmd = getattr(self, 'maintain_gesture_selection', lambda e: print("maintain_gesture_selection not found"))
        self.gesture_listbox.bind('<<ListboxSelect>>', on_select_cmd)
        self.gesture_listbox.bind('<FocusOut>', maintain_selection_cmd)

        # 제스처 목록 아래 버튼 프레임
        gesture_btn_frame = ttk.Frame(gesture_frame)
        gesture_btn_frame.pack(fill=tk.X, pady=(10, 0))

        edit_cmd = getattr(self, 'edit_gesture', lambda: print("edit_gesture not found"))
        delete_cmd = getattr(self, 'delete_selected_gesture', lambda: print("delete_selected_gesture not found"))

        ttk.Button(gesture_btn_frame, text="Edit", width=10, command=edit_cmd).pack(side=tk.LEFT, padx=5) # UI 텍스트 영어로
        ttk.Button(gesture_btn_frame, text="Delete", width=10, command=delete_cmd).pack(side=tk.LEFT, padx=5) # UI 텍스트 영어로

        # 반복 횟수 설정 프레임
        repeat_frame = ttk.Frame(gesture_frame)
        repeat_frame.pack(fill=tk.X, pady=(5, 0))

        ttk.Label(repeat_frame, text="Repeat Count:").pack(side=tk.LEFT, padx=5) # UI 텍스트 영어로

        self.repeat_count_entry = ttk.Entry(repeat_frame, textvariable=self.repeat_count, width=5)
        self.repeat_count_entry.pack(side=tk.LEFT, padx=5)

        move_up_cmd = getattr(self, 'move_gesture_up', lambda: print("move_gesture_up not found"))
        move_down_cmd = getattr(self, 'move_gesture_down', lambda: print("move_gesture_down not found"))

        ttk.Button(repeat_frame, text="↑", width=2, command=move_up_cmd).pack(side=tk.RIGHT, padx=2)
        ttk.Button(repeat_frame, text="↓", width=2, command=move_down_cmd).pack(side=tk.RIGHT, padx=2)

        # 무한 반복 체크박스 프레임
        infinite_frame = ttk.Frame(gesture_frame)
        infinite_frame.pack(fill=tk.X, pady=(5, 0))

        toggle_infinite_cmd = getattr(self, 'toggle_infinite_repeat', lambda: print("toggle_infinite_repeat not found"))

        self.infinite_checkbox = ttk.Checkbutton(infinite_frame, text="Infinite Repeat", variable=self.infinite_repeat, command=toggle_infinite_cmd) # UI 텍스트 영어로
        self.infinite_checkbox.pack(side=tk.LEFT, padx=5)
