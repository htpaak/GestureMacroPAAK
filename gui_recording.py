# gui_recording.py
import tkinter as tk
from tkinter import messagebox

class GuiRecordingMixin:
    """GUI의 매크로 및 제스처 녹화 관련 액션(시작, 중지, 저장) 처리를 담당하는 믹스인 클래스"""

    # --- 의존성 메서드 (다른 곳에서 구현 필요) ---
    def update_status(self, message): raise NotImplementedError
    def update_event_list(self): raise NotImplementedError
    def start_event_list_updates(self): raise NotImplementedError
    def stop_event_list_updates(self): raise NotImplementedError
    def toggle_gesture_recognition(self): raise NotImplementedError # start_gesture_recording에서 사용

    # --- 녹화 관련 메서드 ---

    def start_gesture_recording(self):
        """새 제스처 녹화 시작 (UI 버튼 등에서 호출)"""
        if not hasattr(self, 'gesture_manager') or not self.gesture_manager:
            messagebox.showwarning("Warning", "Gesture Manager is not available.")
            return

        # 제스처 인식 활성화 확인 및 요청
        if not hasattr(self, 'gesture_enabled') or not self.gesture_enabled.get():
            if messagebox.askyesno("Activate Gesture Recognition",
                                 "Gesture recognition must be active to record gestures.\nActivate now?"):
                # gesture_enabled 변수가 없다면 생성 (임시)
                if not hasattr(self, 'gesture_enabled'): self.gesture_enabled = tk.BooleanVar(value=True)
                else: self.gesture_enabled.set(True)
                # 실제 활성화 함수 호출 (다른 믹스인에 구현)
                self.toggle_gesture_recognition()
            else:
                return # 사용자가 활성화 거부

        # 제스처 녹화 시작 요청
        try:
            if hasattr(self.gesture_manager, 'start_gesture_recording') and callable(self.gesture_manager.start_gesture_recording):
                self.gesture_manager.start_gesture_recording()
                self.update_status("Recording gesture...")
            else:
                messagebox.showerror("Error", "Gesture Manager does not support start_gesture_recording method.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start gesture recording: {e}")


    def start_recording_for_selected_gesture(self):
        """선택된 제스처에 대한 매크로 녹화 시작 (UI 버튼 등에서 호출)"""
        if not hasattr(self, 'gesture_listbox') or not hasattr(self, 'gesture_manager'):
             messagebox.showerror("Error", "Required components (gesture listbox/manager) not initialized.")
             return

        selected_indices = self.gesture_listbox.curselection()
        if not selected_indices:
            messagebox.showwarning("Selection Error", "Select a gesture to record the macro for.")
            return

        selected_index = selected_indices[0]
        selected_display_name = self.gesture_listbox.get(selected_index)
        # 내부 키 변환 (GuiGestureManagerMixin의 헬퍼 사용 또는 직접 구현)
        internal_gesture_key = selected_display_name.replace("Alt-", "A-").replace("Ctrl-", "CT-") # 임시

        # 내부 상태 업데이트
        self.current_gesture = internal_gesture_key # 현재 녹화 대상 제스처 (내부 키)
        self.selected_gesture_name = internal_gesture_key # 선택된 제스처 이름도 내부 키로 통일 권장
        self.selected_gesture_index = selected_index

        print(f"Starting macro recording for gesture: {internal_gesture_key} (Display: {selected_display_name})")
        self.start_recording() # 공통 녹화 시작 로직 호출
        self.update_status(f"Recording macro for '{selected_display_name}' (Press F10 to finish)")


    def start_recording(self):
        """공통 매크로 녹화 시작 로직"""
        if not hasattr(self, 'recorder'):
             messagebox.showerror("Error", "Recorder not initialized.")
             return
        if self.recorder.recording:
            print("Already recording.")
            return

        try:
            self.recorder.start_recording()
            print("Recorder started.")

            # UI 업데이트
            if hasattr(self, 'record_btn'): self.record_btn.config(state=tk.DISABLED)
            if hasattr(self, 'stop_btn'): self.stop_btn.config(state=tk.NORMAL)
            if hasattr(self, 'record_status'): self.record_status.config(text="RECORDING", foreground="red")
            if hasattr(self, 'event_listbox'): self.event_listbox.delete(0, tk.END) # 이전 이벤트 지우기

            # 실시간 업데이트 시작
            self.start_event_list_updates()

            # 상태 메시지 (제스처 녹화 아닐 때만)
            if not getattr(self, 'current_gesture', None):
                 self.update_status("Recording macro...")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to start recording: {e}")


    def stop_recording(self):
        """매크로 녹화 중지 (UI 버튼, 단축키 등에서 호출)"""
        if not hasattr(self, 'recorder') or not self.recorder.recording:
            # print("Not recording.") # 필요 시 로그
            return

        try:
            self.recorder.stop_recording()
            print("Recorder stopped.")

            # UI 업데이트
            if hasattr(self, 'record_btn'): self.record_btn.config(state=tk.NORMAL)
            if hasattr(self, 'stop_btn'): self.stop_btn.config(state=tk.DISABLED)
            if hasattr(self, 'record_status'): self.record_status.config(text="Ready", foreground="black")

            # 실시간 업데이트 중지 및 최종 업데이트
            self.stop_event_list_updates()
            self.update_event_list() # 최종 이벤트 목록 표시

            # 제스처 매크로였다면 자동 저장
            current_recording_gesture = getattr(self, 'current_gesture', None)
            if current_recording_gesture:
                 print(f"Recording finished for gesture '{current_recording_gesture}'. Saving automatically.")
                 self.save_gesture_macro() # 자동 저장 함수 호출
                 self.current_gesture = None # 대상 제스처 초기화
            else:
                 self.update_status("Recording finished. Click 'Save Macro' to save.")

        except Exception as e:
             messagebox.showerror("Error", f"Error stopping recording: {e}")
             # 오류 발생 시 UI 상태 복구 시도
             if hasattr(self, 'record_btn'): self.record_btn.config(state=tk.NORMAL)
             if hasattr(self, 'stop_btn'): self.stop_btn.config(state=tk.DISABLED)
             if hasattr(self, 'record_status'): self.record_status.config(text="Error", foreground="red")


    def save_gesture_macro(self):
        """현재 recorder의 이벤트를 self.current_gesture에 연결하여 저장 (stop_recording에서 호출)"""
        gesture_key_to_save = getattr(self, 'current_gesture', None)
        if not gesture_key_to_save or not hasattr(self, 'gesture_manager') or not hasattr(self, 'recorder'):
            print("Error: Cannot save gesture macro - missing context.")
            return

        events = self.recorder.events if hasattr(self.recorder, 'events') else []
        display_name = getattr(self, 'selected_gesture_name', gesture_key_to_save) # 표시용 이름

        # 빈 이벤트 저장 확인
        if not events:
            if not messagebox.askyesno("Save Empty Macro", f"Save empty event list for gesture '{display_name}'?"):
                self.update_status("Save cancelled.")
                return # 저장 취소

        # 저장 시도
        try:
            if hasattr(self.gesture_manager, 'save_macro_for_gesture'):
                 success = self.gesture_manager.save_macro_for_gesture(gesture_key_to_save, events)
                 if success:
                     msg = f"Empty macro saved for '{display_name}'." if not events else \
                           f"Macro ({len(events)} events) saved for '{display_name}'."
                     messagebox.showinfo("Save Complete", msg)
                     self.update_status(msg.replace(f" ({len(events)} events)", ""))
                 else:
                     messagebox.showerror("Save Error", f"Failed to save macro for gesture '{display_name}'.")
                     self.update_status(f"Error saving macro for '{display_name}'.")
            else:
                 messagebox.showerror("Error", "Gesture Manager does not support save_macro_for_gesture.")

        except Exception as e:
             messagebox.showerror("Save Error", f"Error saving gesture macro: {e}")
             self.update_status("Error during gesture macro save.")


    def save_macro(self):
        """'Save Macro' 버튼 클릭 시: 현재 에디터의 이벤트를 선택된 제스처에 저장"""
        if not hasattr(self, 'editor') or not hasattr(self, 'gesture_manager'):
             messagebox.showerror("Error", "Required components (editor/gesture manager) not initialized.")
             return

        # 현재 선택된 제스처 확인 (내부 키 기준)
        selected_internal_key = getattr(self, 'selected_gesture_name', None)
        if not selected_internal_key and hasattr(self, 'gesture_listbox'): # 리스트박스 확인 (Fallback)
             sel_indices = self.gesture_listbox.curselection()
             if sel_indices:
                  display_name = self.gesture_listbox.get(sel_indices[0])
                  selected_internal_key = display_name.replace("Alt-", "A-").replace("Ctrl-", "CT-") # 임시 변환

        if not selected_internal_key:
            messagebox.showwarning("Selection Error", "Select a gesture to save the macro to.")
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

        display_name = selected_internal_key.replace("A-", "Alt-").replace("CT-", "Ctrl-") # 표시용 이름 생성

        # 빈 이벤트 저장 확인
        if not events:
            if not messagebox.askyesno("Save Empty Macro", f"Save empty event list for gesture '{display_name}'?"):
                self.update_status("Save cancelled.")
                return

        # 저장 시도
        try:
            if hasattr(self.gesture_manager, 'save_macro_for_gesture'):
                success = self.gesture_manager.save_macro_for_gesture(selected_internal_key, events)
                if success:
                     msg = f"Empty macro saved for '{display_name}'." if not events else \
                           f"Macro ({len(events)} events) saved for '{display_name}'."
                     messagebox.showinfo("Save Complete", msg)
                     self.update_status(msg.replace(f" ({len(events)} events)", ""))
                     # 저장 후 에디터 상태 변경? (예: '수정됨' 표시 제거)
                else:
                     messagebox.showerror("Save Error", f"Failed to save macro for gesture '{display_name}'.")
                     self.update_status(f"Error saving macro for '{display_name}'.")
            else:
                 messagebox.showerror("Error", "Gesture Manager does not support save_macro_for_gesture.")

        except Exception as e:
             messagebox.showerror("Save Error", f"Error saving macro: {e}")
             self.update_status("Error during macro save.")


    def toggle_recording(self, event=None):
        """녹화 시작/중지 토글 (단축키 등에서 사용)"""
        if hasattr(self, 'recorder') and self.recorder.recording:
            self.stop_recording()
        else:
            # 선택된 제스처가 있으면 해당 제스처에 대한 녹화 시작
            if hasattr(self, 'gesture_listbox') and self.gesture_listbox.curselection():
                self.start_recording_for_selected_gesture()
            else:
                # 선택된 제스처 없으면 녹화 시작 불가 메시지 표시 (혼란 방지)
                messagebox.showinfo("Start Recording", "Select a gesture first to start recording.")
                # 또는 여기서 일반 녹화(self.start_recording())를 시작할 수도 있음 - 정책 결정 필요