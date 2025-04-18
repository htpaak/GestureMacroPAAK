# gui_utilities.py
import tkinter as tk
from tkinter import messagebox, ttk
# try: # keyboard import 부분 주석 처리 또는 삭제
#     import keyboard # Optional dependency
# except ImportError:
#     keyboard = None
#     print("Warning: 'keyboard' library not found. Hotkeys will be disabled.")
# import keyboard # 단축키 설정용
import logging # 로깅 추가

# --- pynput import 추가 ---
try:
    from pynput import keyboard as pynput_keyboard
except ImportError:
    pynput_keyboard = None
    print("Warning: 'pynput' library not found. Hotkeys will be disabled.")
    messagebox.showwarning(
        "Dependency Error",
        "The 'pynput' library is required for hotkey functionality.\n" +
        "Please install it using: pip install pynput"
    )

# --- 좌표 입력 대화 상자 클래스 추가 ---
class CoordinateDialog(tk.Toplevel):
    """X, Y 좌표 및 좌표 모드를 입력받는 모달 대화 상자"""
    def __init__(self, parent, title="Enter Coordinates", initial_x=0, initial_y=0, show_mode_options=False):
        super().__init__(parent)
        self.parent = parent # 부모 창 저장
        self.title(title)
        dialog_width = 330 if show_mode_options else 250 # 폭은 유지
        dialog_height = 260 if show_mode_options else 120 # 높이 증가 (240 -> 260)
        # self.geometry("280x180" if show_mode_options else "250x120") # 이전 코드 주석 처리

        # --- 창 중앙 정렬 로직 추가 ---
        parent_x = parent.winfo_x()
        parent_y = parent.winfo_y()
        parent_width = parent.winfo_width()
        parent_height = parent.winfo_height()
        x = parent_x + (parent_width // 2) - (dialog_width // 2)
        y = parent_y + (parent_height // 2) - (dialog_height // 2)
        self.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")
        # --- 중앙 정렬 로직 끝 ---

        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self.result = None # 결과: (x, y, mode) 튜플 또는 None
        self.coord_mode_var = tk.StringVar(value="absolute") # 기본값: 절대좌표

        frame = ttk.Frame(self, padding="10 10 10 10")
        frame.pack(expand=True, fill=tk.BOTH)

        # 좌표 입력 필드
        coord_frame = ttk.Frame(frame)
        coord_frame.pack(pady=5)
        ttk.Label(coord_frame, text="X:").grid(column=0, row=0, sticky=tk.W, padx=5)
        self.x_entry = ttk.Entry(coord_frame, width=10)
        self.x_entry.grid(column=1, row=0, padx=5)
        self.x_entry.insert(0, str(initial_x))
        ttk.Label(coord_frame, text="Y:").grid(column=2, row=0, sticky=tk.W, padx=5)
        self.y_entry = ttk.Entry(coord_frame, width=10)
        self.y_entry.grid(column=3, row=0, padx=5)
        self.y_entry.insert(0, str(initial_y))

        # 좌표 모드 선택 (옵션 활성화 시 표시)
        if show_mode_options:
            mode_frame = ttk.LabelFrame(frame, text="Coordinate Mode", padding=5)
            mode_frame.pack(pady=5, fill=tk.X)
            ttk.Radiobutton(mode_frame, text="Absolute", variable=self.coord_mode_var, value="absolute").pack(anchor=tk.W)
            ttk.Radiobutton(mode_frame, text="Gesture Relative", variable=self.coord_mode_var, value="gesture_relative").pack(anchor=tk.W)
            # --- Mouse Relative 라디오 버튼 확인 및 추가 ---
            ttk.Radiobutton(mode_frame, text="Mouse Relative", variable=self.coord_mode_var, value="playback_relative").pack(anchor=tk.W)

        # OK/Cancel 버튼
        button_frame = ttk.Frame(frame)
        button_frame.pack(side=tk.BOTTOM, pady=10)
        ok_button = ttk.Button(button_frame, text="OK", command=self.on_ok, width=8)
        ok_button.pack(side=tk.LEFT, padx=5)
        cancel_button = ttk.Button(button_frame, text="Cancel", command=self.on_cancel, width=8)
        cancel_button.pack(side=tk.LEFT, padx=5)

        self.bind('<Return>', self.on_ok)
        self.bind('<Escape>', self.on_cancel)
        self.x_entry.focus_set()
        self.x_entry.selection_range(0, tk.END)
        self.wait_window(self)

    def on_ok(self, event=None):
        try:
            x = int(self.x_entry.get())
            y = int(self.y_entry.get())
            mode = self.coord_mode_var.get()
            self.result = (x, y, mode) # 결과를 튜플로 반환
            self.destroy()
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter valid integers for X and Y.", parent=self)
            self.x_entry.focus_set()
            self.x_entry.selection_range(0, tk.END)

    def on_cancel(self, event=None):
        self.result = None
        self.destroy()

# --- 좌표 입력 대화 상자 호출 함수 ---
def ask_coordinates(parent, title="Enter Coordinates", initial_x=0, initial_y=0, show_mode_options=False):
    """좌표 입력 대화 상자를 표시하고 (x, y, mode) 튜플 또는 None을 반환"""
    dialog = CoordinateDialog(parent, title, initial_x, initial_y, show_mode_options)
    return dialog.result

# --- 기존 GuiUtilitiesMixin 클래스 ---
class GuiUtilitiesMixin:
    """GUI의 기타 유틸리티 기능(녹화 설정, 실시간 업데이트, 단축키)을 담당하는 믹스인 클래스"""

    # --- 의존성 메서드/속성 ---
    def update_status(self, message): raise NotImplementedError
    # recorder, gesture_manager, root 등 객체
    # record_mouse_move, record_delay, use_absolute_coords, use_relative_coords, record_keyboard 등 tk.BooleanVar
    hotkey_listener = None # pynput 리스너 객체 저장용

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
        print("[DEBUG _periodic_update_event_list] Periodic update check...") # 주기적 호출 확인 로그
        # Check if still recording
        is_recording = hasattr(self, 'recorder') and self.recorder.recording
        print(f"[DEBUG _periodic_update_event_list] Recording state: {is_recording}") # 녹화 상태 확인 로그

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
        # else: # 녹화 중이 아니면 아무것도 하지 않음 (다음 업데이트 예약 안 함)
        #     print("Recording stopped, halting periodic event list updates.")
        #     self.stop_event_list_updates() # 여기서 호출 제거

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
            
        logging.info("handle_delete_key callback triggered.")
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
            logging.exception(f"!!! Exception in handle_delete_key callback: {e}")
            print(f"Error in handle_delete_key: {e}")
        finally:
            logging.info("handle_delete_key callback finished.")

    # --- 키보드 단축키 (pynput 사용) ---
    def setup_keyboard_shortcuts(self):
        """키보드 단축키 설정 (pynput 사용, F1으로 재등록 기능 포함)"""
        if pynput_keyboard is None:
            logging.warning("pynput library not found, skipping hotkey setup.")
            return

        logging.info("Setting up keyboard shortcuts using pynput...")

        # --- 기존 리스너 중지 --- (unhook 대신)
        self.unhook_keyboard_shortcuts() # 기존 리스너가 있다면 중지

        try:
            # --- pynput 형식의 단축키 매핑 --- 
            # <ctrl>+a, <alt>+f, <cmd>+k 등, 특수키는 <> 사용
            # 일반 문자 키는 그냥 'a', 'b' 등
            # 함수 키는 '<f1>', '<f9>' 등
            shortcuts = {
                '<f9>': getattr(self, 'toggle_recording', None),
                '<f11>': getattr(self, 'start_gesture_recognition', None),
                '<f12>': getattr(self, 'stop_gesture_recognition', None),
                '<delete>': getattr(self, 'handle_delete_key', None), # delete 키 핸들러 확인 필요
                '<ctrl>+a': getattr(self, 'select_all_events', None),
                # '<f1>': self.setup_keyboard_shortcuts # F1으로 재등록 기능 제거
            }

            # 유효한 콜백 함수만 필터링
            valid_shortcuts = {}
            for hotkey, func in shortcuts.items():
                if func and callable(func):
                    # 제스처 관련 핫키는 gesture_manager 확인
                    if hotkey in ['<f11>', '<f12>'] and not hasattr(self, 'gesture_manager'):
                        logging.warning(f"Gesture manager not found, skipping hotkey '{hotkey}'.")
                        continue
                    valid_shortcuts[hotkey] = func
                    # 로그는 리스너 시작 시 한 번에 기록 (개별 등록 로그 제거)
                else:
                    # F1 제거했으므로, 다른 함수가 None이거나 callable하지 않은 경우 경고
                    logging.warning(f"Function for hotkey '{hotkey}' not found or not callable.")

            if not valid_shortcuts:
                logging.warning("No valid hotkeys to register.")
                return

            # --- GlobalHotKeys 리스너 생성 및 시작 --- 
            logging.info(f"Registering hotkeys: {list(valid_shortcuts.keys())}")
            # GlobalHotKeys는 데몬 스레드에서 실행됨
            self.hotkey_listener = pynput_keyboard.GlobalHotKeys(valid_shortcuts)
            self.hotkey_listener.start()
            logging.info("pynput GlobalHotKeys listener started.")

        except Exception as e:
            logging.exception(f"!!! Error during pynput setup_keyboard_shortcuts: {e}")
            messagebox.showerror("Hotkey Error", f"An unexpected error occurred while setting up pynput hotkeys.\n{e}")
            self.hotkey_listener = None # 실패 시 리스너 참조 제거

    # 애플리케이션 종료 시 단축키 해제 (pynput 용)
    def unhook_keyboard_shortcuts(self):
        """pynput 핫키 리스너 중지"""
        if hasattr(self, 'hotkey_listener') and self.hotkey_listener:
            logging.info("Stopping pynput GlobalHotKeys listener...")
            try:
                self.hotkey_listener.stop()
                self.hotkey_listener = None # 리스너 참조 제거
                logging.info("pynput listener stopped.")
            except Exception as e:
                logging.exception(f"Error stopping pynput listener: {e}")
        # else:
        #     logging.info("No active pynput listener found to stop.")
