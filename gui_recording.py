# gui_recording.py
import tkinter as tk
from tkinter import messagebox, ttk
import logging # 로깅 임포트 추가

class GuiRecordingMixin:
    """GUI의 매크로 및 제스처 녹화 관련 액션(시작, 중지, 저장) 처리를 담당하는 믹스인 클래스"""

    # --- 의존성 메서드 (다른 곳에서 구현 필요) ---
    def update_status(self, message): raise NotImplementedError
    # def update_event_list(self): raise NotImplementedError # 이제 GuiEventListMixin에 구현
    # def start_event_list_updates(self): raise NotImplementedError # 이제 GuiUtilitiesMixin에 구현
    # def stop_event_list_updates(self): raise NotImplementedError # 이제 GuiUtilitiesMixin에 구현
    def toggle_gesture_recognition(self): raise NotImplementedError # GuiRecognitionControlMixin에 구현

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
        """선택된 제스처에 대한 매크로 녹화 시작 (추출된 코드)"""
        if not hasattr(self, 'gesture_listbox'):
            messagebox.showerror("Error", "Gesture listbox not found.")
            return

        selected_indices = self.gesture_listbox.curselection()
        if not selected_indices:
            messagebox.showwarning("Selection Error", "Select a gesture to record the macro for.") # UI 텍스트 영어로
            return

        try:
            selected_gesture_name = self.gesture_listbox.get(selected_indices[0])
        except tk.TclError:
             messagebox.showerror("Error", "Could not get selected gesture name.")
             return

        # 내부 키 이름으로 변환 (GuiGestureManagerMixin의 메소드 사용 가정)
        if hasattr(self, '_get_internal_gesture_key') and callable(self._get_internal_gesture_key):
            internal_gesture_name = self._get_internal_gesture_key(selected_gesture_name)
        else:
            # Fallback or error
            print("Warning: _get_internal_gesture_key not found. Using display name.")
            internal_gesture_name = selected_gesture_name

        # 현재 녹화 대상 제스처 설정
        self.current_gesture = internal_gesture_name
        # 선택 상태 유지를 위한 변수들도 업데이트 (GuiGestureManagerMixin과 공유?)
        # if hasattr(self, 'selected_gesture_name'): self.selected_gesture_name = internal_gesture_name
        # if hasattr(self, 'selected_gesture_index'): self.selected_gesture_index = selected_indices[0]

        print(f"Recording macro for selected gesture: {selected_gesture_name} (Internal key: {internal_gesture_name})")

        # 실제 녹화 시작 함수 호출
        if hasattr(self, 'start_recording') and callable(self.start_recording):
            self.start_recording()
        else:
             messagebox.showerror("Error", "Start recording function is not available.")
             self.current_gesture = None # 실패 시 초기화
             return

        # 상태 업데이트
        if hasattr(self, 'update_status') and callable(self.update_status):
            self.update_status(f"Recording macro for gesture '{selected_gesture_name}' (Press F10 to stop)") # UI 텍스트 영어로


    def start_recording(self):
        """Start the actual macro recording process (extracted code)."""
        print("start_recording method called")
        if not hasattr(self, 'recorder'):
            messagebox.showerror("Error", "Recorder component not available.")
            return

        if self.recorder.recording:
            print("Already recording.")
            return

        # Start recorder
        try:
            self.recorder.start_recording()
            print("recorder.start_recording() called successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start recording: {e}")
            return

        # --- Update GUI States ---
        # Update button states
        if hasattr(self, 'record_btn') and self.record_btn.winfo_exists():
            # self.record_btn.config(state=tk.DISABLED) # <<< 이 줄을 주석 처리 또는 삭제
            pass # 버튼 상태 변경 안 함
        if hasattr(self, 'stop_btn') and self.stop_btn.winfo_exists():
            self.stop_btn.config(state=tk.NORMAL)
        # save_btn state remains unchanged

        # Update recording status label
        if hasattr(self, 'record_status') and self.record_status.winfo_exists():
            self.record_status.config(text="Recording...", foreground="red")

        # Clear event listbox
        if hasattr(self, 'event_listbox') and self.event_listbox.winfo_exists():
            try:
                self.event_listbox.delete(0, tk.END)
            except tk.TclError:
                 print("Error clearing event listbox (likely destroyed).")

        # Start real-time event list updates
        if hasattr(self, 'start_event_list_updates') and callable(self.start_event_list_updates):
            self.start_event_list_updates()
        else:
             print("Warning: start_event_list_updates method not found.")

        # Update main status bar (only if not recording for a specific gesture)
        if not getattr(self, 'current_gesture', None):
             if hasattr(self, 'update_status') and callable(self.update_status):
                 self.update_status("Macro recording started...")


    def stop_recording(self):
        """Stop the macro recording process (extracted code)."""
        if not hasattr(self, 'recorder') or not self.recorder.recording:
            print("Not currently recording.")
            return

        # Stop recorder
        try:
            self.recorder.stop_recording()
            print("Recorder stopped successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to stop recorder: {e}")
            # Attempt to restore UI state even on error?
            if hasattr(self, 'record_btn') and self.record_btn.winfo_exists(): self.record_btn.config(state=tk.NORMAL)
            if hasattr(self, 'stop_btn') and self.stop_btn.winfo_exists(): self.stop_btn.config(state=tk.DISABLED)
            if hasattr(self, 'record_status') and self.record_status.winfo_exists(): self.record_status.config(text="Error", foreground="red")
            return

        # --- Update GUI States ---
        # Update button states
        if hasattr(self, 'record_btn') and self.record_btn.winfo_exists():
            self.record_btn.config(state=tk.NORMAL)
        if hasattr(self, 'stop_btn') and self.stop_btn.winfo_exists():
            self.stop_btn.config(state=tk.DISABLED)
        # 저장 버튼 직접 활성화
        if hasattr(self, 'save_btn') and self.save_btn.winfo_exists():
            self.save_btn.config(state=tk.NORMAL)

        # Update recording status label
        if hasattr(self, 'record_status') and self.record_status.winfo_exists():
            self.record_status.config(text="Ready", foreground="black")

        # Stop real-time event list updates
        if hasattr(self, 'stop_event_list_updates') and callable(self.stop_event_list_updates):
            self.stop_event_list_updates()
        else:
            print("Warning: stop_event_list_updates method not found.")

        # 단축키로 녹화 종료 시 UI가 즉시 반영되도록 강제 업데이트
        if hasattr(self, 'root'):
            # 두 가지 업데이트 메소드 모두 사용하여 강제 업데이트
            self.root.update_idletasks()
            self.root.update()  # 더 강력한 업데이트 메소드 추가
            
            # 포커스 강제 조정 - 단축키 후 포커스 문제 해결
            if hasattr(self, 'event_listbox') and self.event_listbox.winfo_exists():
                self.event_listbox.focus_force()
            elif hasattr(self, 'save_btn') and self.save_btn.winfo_exists():
                self.save_btn.focus_force()  # 저장 버튼에 포커스
            else:
                self.root.focus_force()

        # Auto-save if recording was for a specific gesture
        current_rec_gesture = getattr(self, 'current_gesture', None)
        if current_rec_gesture:
            print(f"Recording finished for gesture '{current_rec_gesture}'. Attempting auto-save...")
            # 추가 업데이트 강제 적용
            if hasattr(self, 'root'): self.root.update()
            
            if hasattr(self, 'save_gesture_macro') and callable(self.save_gesture_macro):
                self.save_gesture_macro() # This method should handle status updates and clearing current_gesture
            else:
                print("Warning: save_gesture_macro method not found for auto-saving.")
                # Clear the current gesture manually if save method is missing?
                self.current_gesture = None
                if hasattr(self, 'update_status'): self.update_status("Recording finished, but auto-save failed.")
        else:
            # Update status for generic macro recording
            if hasattr(self, 'update_status') and callable(self.update_status):
                self.update_status("Recording finished. Click 'Save Macro' to save.")


    def save_gesture_macro(self):
        """Save the recorded macro events to the current gesture."""
        print("Warning: save_gesture_macro called from GuiRecordingMixin, consider moving.")
        if not hasattr(self, 'gesture_manager') or not hasattr(self, 'current_gesture') or not self.current_gesture:
            print("Cannot save: gesture manager or current gesture missing.")
            return
        if not hasattr(self, 'recorder'):
            print("Cannot save: recorder missing.")
            return

        events = self.recorder.events
        if not events:
            events = []
            if not messagebox.askyesno("Save Empty Macro?",
                                     f"Save an empty event list for gesture '{self.current_gesture}'?"):
                if hasattr(self, 'update_status'): self.update_status("Save cancelled.")
                self.current_gesture = None # Clear gesture if save is cancelled
                return

        # Use GestureManager to save (handles storage and callback)
        success = False
        try:
            if hasattr(self.gesture_manager, 'save_macro_for_gesture') and callable(self.gesture_manager.save_macro_for_gesture):
                 success = self.gesture_manager.save_macro_for_gesture(self.current_gesture, events)
            else:
                 print("Error: GestureManager has no save_macro_for_gesture method.")
                 messagebox.showerror("Error", "Failed to save macro: Save function not available.")

            if success:
                msg = f"Empty macro saved for gesture '{self.current_gesture}'." if not events else \
                      f"Macro ({len(events)} events) saved for gesture '{self.current_gesture}'."
                messagebox.showinfo("Save Complete", msg)
                if hasattr(self, 'update_status'): self.update_status(msg)
            else:
                 # Error message already shown or logged
                 if hasattr(self, 'update_status'): self.update_status("Error saving macro.")
        except Exception as e:
             print(f"Exception during save_gesture_macro: {e}")
             messagebox.showerror("Error", f"An error occurred while saving the macro: {e}")
             if hasattr(self, 'update_status'): self.update_status("Error saving macro.")

        # Clear the current gesture regardless of save success/failure after attempt
        self.current_gesture = None


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
        logging.info("toggle_recording callback triggered.") # 콜백 시작 로그
        try:
            if hasattr(self, 'recorder') and self.recorder.recording:
                print("Toggle Recording: Stopping...") # 로그 추가
                # 녹화 중지
                self.stop_recording()
                # --- 버튼 텍스트 업데이트 --- 
                if hasattr(self, 'record_btn') and self.record_btn.winfo_exists():
                    self.record_btn.config(text="Start Recording Macro (F9)") # <--- 텍스트 수정
                    # stop_recording에서 이미 state=NORMAL 로 설정됨
                # --- 업데이트 끝 --- 
            else:
                print("Toggle Recording: Starting...") # 로그 추가
                # 선택된 제스처가 있으면 해당 제스처에 대한 녹화 시작
                if hasattr(self, 'gesture_listbox') and self.gesture_listbox.curselection():
                    try:
                        self.start_recording_for_selected_gesture() 
                        # --- 버튼 텍스트 업데이트 --- 
                        if hasattr(self, 'record_btn') and self.record_btn.winfo_exists():
                            self.record_btn.config(text="Stop Recording Macro (F9)") # <--- 텍스트 수정
                        # --- 업데이트 끝 --- 
                    except Exception as start_error:
                         print(f"Error during start_recording_for_selected_gesture: {start_error}")
                else:
                    messagebox.showinfo("Start Recording", "Select a gesture first to start recording.")
        except Exception as e:
            logging.exception(f"!!! Exception in toggle_recording callback: {e}") # 예외 발생 시 로그 기록
        finally:
            logging.info("toggle_recording callback finished.") # 콜백 종료 로그