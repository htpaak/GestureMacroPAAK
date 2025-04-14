# gui_playback.py
import tkinter as tk
from tkinter import messagebox
import threading # player 실행을 위해

class GuiPlaybackMixin:
    """GUI의 매크로 및 제스처 재생, 중지, 관련 옵션 처리를 담당하는 믹스인 클래스"""

    def update_status(self, message):
        """하단 상태 표시줄 업데이트 (구현은 gui_base.py에서)"""
        raise NotImplementedError

        def _get_repeat_count(self):
            """반복 횟수 입력값 가져오기"""
            if hasattr(self, 'infinite_repeat') and self.infinite_repeat.get():
                return -1 # 무한 반복
            elif hasattr(self, 'repeat_count_entry'):
                try:
                    count = int(self.repeat_count_entry.get())
                    return count if count >= 1 else 1
                except ValueError:
                    return 1 # 잘못된 값이면 1번 반복
            else:
                return 1 # 입력 필드 없으면 1번 반복

        def _update_playback_buttons(self, playing):
            """재생 상태에 따라 재생/중지 버튼 상태 업데이트"""
            if hasattr(self, 'play_btn'):
                self.play_btn.config(state=tk.DISABLED if playing else tk.NORMAL)
            if hasattr(self, 'stop_play_btn'):
                self.stop_play_btn.config(state=tk.NORMAL if playing else tk.DISABLED)
            # 필요하다면 다른 버튼들도 비활성화 (예: 녹화 버튼)
            if hasattr(self, 'record_btn'):
                self.record_btn.config(state=tk.DISABLED if playing else tk.NORMAL)
            if hasattr(self, 'gesture_record_btn'):
                self.gesture_record_btn.config(state=tk.DISABLED if playing else tk.NORMAL)

        def play_gesture_macro(self):
            """선택된 제스처의 매크로 실행"""
            if not hasattr(self, 'gesture_manager') or not self.gesture_manager:
                messagebox.showerror("Error", "Gesture Manager is not available.")
                return
            if not hasattr(self, 'gesture_listbox'):
                messagebox.showerror("Error", "Gesture listbox not initialized.")
                return

            selected = self.gesture_listbox.curselection()
            if not selected:
                messagebox.showwarning("Selection Error", "Select a gesture to play.")
                return

            gesture_display_name = self.gesture_listbox.get(selected[0])
            # 내부 키 찾기 (여기서도 필요) - GuiRecordingMixin과 유사 로직 또는 helper 함수 필요
            # 임시 변환 사용
            gesture_internal_key = gesture_display_name.replace("Alt-", "A-").replace("Ctrl-", "CT-")

            repeat_count = self._get_repeat_count()

            # 매크로 실행 (백그라운드 스레드에서 실행하는 것이 좋을 수 있음)
            # 여기서는 gesture_manager의 execute_gesture_action 사용
            try:
                # TODO: execute_gesture_action이 반복 횟수를 인자로 받도록 수정 필요할 수 있음
                # 현재는 GestureManager가 알아서 처리한다고 가정
                print(f"Executing action for gesture: {gesture_internal_key} (Repeat: {repeat_count})")
                # GestureManager에서 직접 실행하거나, Player 사용
                # self.gesture_manager.execute_gesture_action(gesture_internal_key, repeat_count=repeat_count)
                # 만약 Player를 직접 사용한다면:
                macro_events = self.gesture_manager.get_macro_for_gesture(gesture_internal_key)
                if macro_events is not None:
                    if not self.player.playing:
                        threading.Thread(target=self.player.play_macro,
                                         args=(macro_events, repeat_count, self._on_playback_complete),
                                         daemon=True).start()
                        self._update_playback_buttons(True)
                        self.update_status(f"Playing macro for gesture '{gesture_display_name}'...")
                    else:
                        messagebox.showwarning("Busy", "Another macro is already playing.")
                else:
                    messagebox.showwarning("No Macro", f"No macro found for gesture '{gesture_display_name}'.")

            except Exception as e:
                messagebox.showerror("Playback Error", f"Error playing macro for gesture: {e}")
                self.update_status("Error during playback.")
                self._update_playback_buttons(False)


        def play_macro(self):
            """'Play Macro' 버튼 클릭 시: 현재 이벤트 목록 실행"""
            if not hasattr(self, 'player'):
                messagebox.showerror("Error", "Player not initialized.")
                return

            # 현재 이벤트 목록 가져오기 (에디터 또는 녹화 결과)
            events = None
            if hasattr(self, 'editor') and hasattr(self.editor, 'get_events') and callable(self.editor.get_events):
                events = self.editor.get_events()
            elif hasattr(self, 'recorder') and self.recorder.events: # 녹화 직후
                events = self.recorder.events
            elif hasattr(self, 'editor') and hasattr(self.editor, 'events'): # 임시 fallback
                events = self.editor.events

            if not events:
                messagebox.showwarning("No Events", "There are no events to play.")
                return

            repeat_count = self._get_repeat_count()

            if not self.player.playing:
                # 백그라운드 스레드에서 재생 실행
                threading.Thread(target=self.player.play_macro,
                                 args=(events, repeat_count, self._on_playback_complete),
                                 daemon=True).start()
                self._update_playback_buttons(True)
                self.update_status(f"Playing macro (Repeat: {'Infinite' if repeat_count == -1 else repeat_count})...")
            else:
                messagebox.showwarning("Busy", "Another macro is already playing.")


        def stop_macro(self):
            """매크로 실행 중지"""
            if hasattr(self, 'player') and self.player.playing:
                self.player.stop_macro()
                self._update_playback_buttons(False)
                self.update_status("Macro playback stopped.")
            else:
                print("No macro is currently playing.") # 디버깅용

        def _on_playback_complete(self):
            """재생 완료 시 호출될 콜백 (Player에서 호출)"""
            # 메인 스레드에서 UI 업데이트 실행
            self.root.after(0, self.__update_ui_after_playback)

        def __update_ui_after_playback(self):
            """메인 스레드에서 실행되는 UI 업데이트 함수"""
            self._update_playback_buttons(False)
            self.update_status("Macro playback finished.")


        def toggle_infinite_repeat(self):
            """무한 반복 체크박스 토글 시 호출"""
            if not hasattr(self, 'infinite_repeat') or not hasattr(self, 'repeat_count_entry'):
                return # 관련 위젯 없으면 무시

            if self.infinite_repeat.get():
                self.repeat_count_entry.config(state=tk.DISABLED)
                # self.repeat_count_entry.delete(0, tk.END) # 값 지우기 (선택 사항)
                # self.repeat_count_entry.insert(0, "∞") # 무한대 기호 표시 (Entry는 숫자만 받는게 좋음)
            else:
                self.repeat_count_entry.config(state=tk.NORMAL)
                # 마지막 유효한 값 복원 또는 기본값 '1' 설정
                # current_val = self.repeat_count_entry.get()
                # if not current_val.isdigit() or int(current_val) < 1:
                #     self.repeat_count_entry.delete(0, tk.END)
                #     self.repeat_count_entry.insert(0, "1")

        # update_repeat_count 함수 (Entry 값 변경 시) - 필요 시 추가
        # def update_repeat_count(self, event=None):
        #     if hasattr(self, 'repeat_count_entry'):
        #         try:
        #             val = int(self.repeat_count_entry.get())
        #             if val < 1:
        #                 self.repeat_count_entry.delete(0, tk.END)
        #                 self.repeat_count_entry.insert(0, "1")
        #         except ValueError:
        #             self.repeat_count_entry.delete(0, tk.END)
        #             self.repeat_count_entry.insert(0, "1")
