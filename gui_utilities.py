# gui_utilities.py
import tkinter as tk
from tkinter import messagebox
try:
    import keyboard # Optional dependency
except ImportError:
    keyboard = None
    print("Warning: 'keyboard' library not found. Hotkeys will be disabled.")

# Class definition moved outside the try-except block
class GuiUtilitiesMixin:
    """GUI의 기타 유틸리티 기능(녹화 설정, 실시간 업데이트, 단축키)을 담당하는 믹스인 클래스"""

    # --- 의존성 메서드/속성 ---
    def update_status(self, message): raise NotImplementedError
    # recorder, gesture_manager, root 등 객체
    # record_mouse_move, record_delay, use_absolute_coords, use_relative_coords, record_keyboard 등 tk.BooleanVar

    # --- 녹화 설정 ---
    def update_record_settings(self):
        """녹화 옵션 체크박스 변경 시 레코더 설정 업데이트"""
        if not hasattr(self, 'recorder'): return

        # 좌표계 라디오 버튼 동기화 로직 (use_absolute_coords만 사용)
        # 이 로직은 toggle_absolute/relative_coords 에서 처리하는 것이 더 나음

        try:
            if hasattr(self, 'record_mouse_move'):
                self.recorder.record_mouse_movement = self.record_mouse_move.get()
            # use_relative_coords 값은 toggle 함수에서 recorder에 직접 설정됨
            # if hasattr(self, 'use_relative_coords'):
            #     self.recorder.use_relative_coords = self.use_relative_coords.get()
            if hasattr(self, 'record_keyboard'):
                self.recorder.record_keyboard = self.record_keyboard.get()
            if hasattr(self, 'record_delay'):
                self.recorder.record_delay = self.record_delay.get()

            # 상태 메시지 업데이트
            settings = []
            if hasattr(self, 'record_delay') and self.record_delay.get(): settings.append("Delay")
            if hasattr(self, 'record_mouse_move') and self.record_mouse_move.get():
                coord_type = "Relative" if hasattr(self, 'use_absolute_coords') and not self.use_absolute_coords.get() else "Absolute"
                settings.append(f"Mouse Move ({coord_type})")
            if hasattr(self, 'record_keyboard') and self.record_keyboard.get(): settings.append("Keyboard")

            status_msg = "Recording settings updated: " + ", ".join(settings) if settings else \
                         "Warning: All recording inputs are disabled."
            self.update_status(status_msg)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to update recording settings: {e}")


    def toggle_absolute_coords(self):
        """절대 좌표 라디오 버튼 선택 시 호출"""
        if not hasattr(self, 'use_absolute_coords') or not hasattr(self, 'recorder'): return

        # 라디오 버튼 값(True)에 따라 recorder 설정 업데이트
        is_absolute = self.use_absolute_coords.get() # 라디오 버튼이므로 항상 True일 것임
        # recorder의 use_relative_coords를 False로 설정
        self.recorder.use_relative_coords = not is_absolute
        print(f"Coordinate mode set to: {'Absolute' if is_absolute else 'Relative'}")
        self.update_status("Coordinate mode set to Absolute.")


    def toggle_relative_coords(self):
        """상대 좌표 라디오 버튼 선택 시 호출"""
        if not hasattr(self, 'use_absolute_coords') or not hasattr(self, 'recorder'): return

        # 라디오 버튼 값(False)에 따라 recorder 설정 업데이트
        is_relative = not self.use_absolute_coords.get() # 라디오 버튼 값(False)의 반대
        self.recorder.use_relative_coords = is_relative
        print(f"Coordinate mode set to: {'Relative' if is_relative else 'Absolute'}")
        self.update_status("Coordinate mode set to Relative.")


    # --- 실시간 이벤트 업데이트 (Extracted and refined) ---
    def start_event_list_updates(self):
        """Start real-time event list updates during recording (extracted logic)."""
        if not hasattr(self, 'root') or not hasattr(self, 'update_event_list') or not callable(self.update_event_list):
            print("Error: Cannot start event list updates - missing components.")
            return

        print("Starting event list updates.")
        # Stop existing timer if any
        self.stop_event_list_updates()

        # Immediately update once and schedule the next update
        self.update_event_list() # Initial update
        interval = getattr(self, 'update_interval', 100) # Default 100ms
        try:
            self.update_timer = self.root.after(interval, self._periodic_update_event_list)
        except Exception as e:
            print(f"Error scheduling event list update: {e}")
            self.update_timer = None

    def _periodic_update_event_list(self):
        """Periodically update the event list (only while recording)."""
        # Check if still recording
        is_recording = hasattr(self, 'recorder') and self.recorder.recording

        if is_recording:
            if hasattr(self, 'update_event_list') and callable(self.update_event_list):
                try:
                    self.update_event_list()
                except Exception as e:
                    print(f"Error during periodic event list update: {e}")
                    self.stop_event_list_updates() # Stop updates on error
                    return

            interval = getattr(self, 'update_interval', 100)
            # Schedule next update (ensure timer ID is managed correctly)
            current_timer_id = getattr(self, 'update_timer', None)
            self.update_timer = None # Clear before scheduling next
            try:
                self.update_timer = self.root.after(interval, self._periodic_update_event_list)
            except Exception as e:
                 print(f"Error rescheduling event list update: {e}")
                 self.update_timer = None
        else:
            print("Recording stopped, halting periodic event list updates.")
            self.stop_event_list_updates() # Stop if not recording anymore

    def stop_event_list_updates(self):
        """실시간 이벤트 목록 업데이트 중지"""
        if hasattr(self, 'update_timer') and self.update_timer:
            self.root.after_cancel(self.update_timer)
            self.update_timer = None

    # --- Delete 키 핸들러 추가 ---
    def handle_delete_key(self):
        """Delete 키 입력 처리: 포커스에 따라 이벤트 또는 제스처 삭제 (녹화 중에는 비활성화)"""
        # 녹화 중일 때는 단축키 비활성화
        if hasattr(self, 'recorder') and self.recorder.recording:
            print("Recording active, Delete hotkey disabled.")
            return
            
        try:
            focused_widget = self.root.focus_get()
            # print(f"[DEBUG handle_delete_key] Focused widget: {focused_widget}") # 디버깅용
            if focused_widget == getattr(self, 'event_listbox', None):
                print("Delete key pressed on Event Listbox.")
                if hasattr(self, 'delete_selected_event') and callable(self.delete_selected_event):
                    self.delete_selected_event()
            elif focused_widget == getattr(self, 'gesture_listbox', None):
                print("Delete key pressed on Gesture Listbox.")
                if hasattr(self, 'delete_selected_gesture') and callable(self.delete_selected_gesture):
                    self.delete_selected_gesture()
            else:
                 # 다른 위젯에 포커스가 있다면 아무것도 하지 않음 (선택적)
                 print(f"Delete key pressed, but focus is on other widget: {focused_widget}")
        except Exception as e:
            print(f"Error in handle_delete_key: {e}")

    # --- 키보드 단축키 ---
    def setup_keyboard_shortcuts(self):
        """키보드 단축키 설정"""
        if keyboard is None: return # 라이브러리 없으면 설정 불가

        # 단축키와 연결될 메서드 목록
        # 각 메서드는 해당 믹스인 또는 gui_base에 구현되어 있어야 함
        shortcuts = {
            'f9': getattr(self, 'toggle_recording', None),
            'f10': getattr(self, 'stop_recording', None),
            'f11': getattr(self, 'start_gesture_recognition', None),
            'f12': getattr(self, 'stop_gesture_recognition', None),
            # 'delete': getattr(self, 'delete_selected_event', None), # 이전 방식 주석 처리
            'delete': self.handle_delete_key, # 새 핸들러 연결
            'ctrl+a': getattr(self, 'select_all_events', None)
        }

        print("Setting up keyboard shortcuts...")
        try:
            # 기존 단축키 제거 시도
            for hotkey in shortcuts.keys():
                try: keyboard.remove_hotkey(hotkey)
                except Exception: pass # 제거 실패 무시

            # 새 단축키 등록
            for hotkey, func in shortcuts.items():
                if func and callable(func):
                    # 제스처 인식 단축키는 gesture_manager가 있을 때만 등록
                    if hotkey in ['f11', 'f12'] and not hasattr(self, 'gesture_manager'):
                        continue
                    keyboard.add_hotkey(hotkey, func)
                    print(f"Hotkey '{hotkey}' registered to function '{func.__name__}'.")
                else:
                    print(f"Warning: Function for hotkey '{hotkey}' not found or not callable.")

        except Exception as e:
            print(f"Error setting up keyboard shortcuts: {e}")
            messagebox.showwarning("Hotkey Error", f"Failed to set up keyboard shortcuts.\n{e}")

    # 애플리케이션 종료 시 단축키 해제 (선택 사항, graceful_exit 등에서 호출)
    def unhook_keyboard_shortcuts(self):
        if keyboard is None: return
        print("Unhooking all keyboard shortcuts...")
        keyboard.unhook_all()
