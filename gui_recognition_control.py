# gui_recognition_control.py
import tkinter as tk
from tkinter import messagebox

class GuiRecognitionControlMixin:
    """GUI의 제스처 인식 시작/중지 제어 로직을 담당하는 믹스인 클래스"""

    def update_status(self, message):
        """하단 상태 표시줄 업데이트 (구현은 gui_base.py에서)"""
        raise NotImplementedError

    def start_gesture_recognition(self):
        """제스처 인식 시작"""
        if not hasattr(self, 'gesture_manager') or not self.gesture_manager:
            messagebox.showerror("Error", "Gesture Manager not initialized.")
            return
        # 제스처 활성화 상태 변수가 없으면 생성
        if not hasattr(self, 'gesture_enabled'):
            self.gesture_enabled = tk.BooleanVar(value=False)

        if self.gesture_enabled.get():
            print("Gesture recognition is already active.")
            return

        try:
            # GestureManager의 start 메서드 호출
            if hasattr(self.gesture_manager, 'start') and callable(self.gesture_manager.start):
                self.gesture_manager.start() # 리스너 시작 등
                self.gesture_enabled.set(True)
                self.update_status("Gesture recognition activated.")
                print("Gesture recognition started via GUI/Hotkey.")
                # 버튼 상태 업데이트
                if hasattr(self, 'gesture_start_btn'): self.gesture_start_btn.config(state=tk.DISABLED)
                if hasattr(self, 'gesture_stop_btn'): self.gesture_stop_btn.config(state=tk.NORMAL)
            else:
                messagebox.showerror("Error", "Gesture Manager does not support start method.")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to start gesture recognition: {e}")
            self.gesture_enabled.set(False) # 실패 시 상태 복원
            # 버튼 상태도 복원
            if hasattr(self, 'gesture_start_btn'): self.gesture_start_btn.config(state=tk.NORMAL)
            if hasattr(self, 'gesture_stop_btn'): self.gesture_stop_btn.config(state=tk.DISABLED)


    def stop_gesture_recognition(self):
        """제스처 인식 중지"""
        if not hasattr(self, 'gesture_manager') or not self.gesture_manager:
            messagebox.showerror("Error", "Gesture Manager not initialized.")
            return
        if not hasattr(self, 'gesture_enabled'): # 변수 없으면 중지 불가
            return
        if not self.gesture_enabled.get():
            print("Gesture recognition is already inactive.")
            return

        try:
            # GestureManager의 stop 메서드 호출
            if hasattr(self.gesture_manager, 'stop') and callable(self.gesture_manager.stop):
                self.gesture_manager.stop() # 리스너 중지 등

            # --- 현재 재생 중인 매크로 중지 호출 추가 ---
            if hasattr(self, 'player') and hasattr(self.player, 'stop_playing') and callable(self.player.stop_playing):
                print("Stopping any currently playing macro...")
                self.player.stop_playing()
            # --- 추가 끝 ---

            self.gesture_enabled.set(False)
            self.update_status("Gesture recognition deactivated.")
            print("Gesture recognition stopped via GUI/Hotkey.")
            # 버튼 상태 업데이트
            if hasattr(self, 'gesture_start_btn'): self.gesture_start_btn.config(state=tk.NORMAL)
            if hasattr(self, 'gesture_stop_btn'): self.gesture_stop_btn.config(state=tk.DISABLED)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to stop gesture recognition or macro playback: {e}") # 오류 메시지 수정
            # 실패 시 상태는? 일단 False로 유지? 아니면 True로 복원? -> False 유지
            self.gesture_enabled.set(False)
            # 버튼 상태는? -> 중지 시도했으므로 비활성화 상태 유지?
            if hasattr(self, 'gesture_start_btn'): self.gesture_start_btn.config(state=tk.NORMAL)
            if hasattr(self, 'gesture_stop_btn'): self.gesture_stop_btn.config(state=tk.DISABLED)


    def toggle_gesture_recognition(self):
        """제스처 인식 상태 토글 (주로 내부 호출용)"""
        if not hasattr(self, 'gesture_enabled'): return # 변수 없으면 토글 불가

        if self.gesture_enabled.get():
            self.stop_gesture_recognition()
        else:
            self.start_gesture_recognition()
