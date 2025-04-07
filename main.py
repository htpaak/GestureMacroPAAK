import tkinter as tk
from recorder import MacroRecorder
from player import MacroPlayer
from editor import MacroEditor
from storage import MacroStorage
from simple_gui import SimpleGUI
from gesture_manager import GestureManager

def main():
    # 루트 윈도우 생성
    root = tk.Tk()
    
    # 초기화를 위해 즉시 업데이트
    root.update_idletasks()
    
    # 모듈 초기화
    recorder = MacroRecorder()
    player = MacroPlayer()
    storage = MacroStorage()
    editor = MacroEditor(storage)
    
    # 제스처 관리자 초기화 (레코더 전달)
    gesture_manager = GestureManager(player, storage, recorder)
    
    # GUI 초기화 - 간소화된 GUI 사용 (제스처 관리자 전달)
    gui = SimpleGUI(root, recorder, player, editor, storage, gesture_manager)
    gui.setup_ui()
    
    # 시작 시 제스처 인식 자동 활성화 (0.5초 후)
    def auto_enable_gesture():
        if hasattr(gui, 'gesture_enabled'):
            print("제스처 인식 자동 활성화")
            gui.gesture_enabled.set(True)
            gui.toggle_gesture_recognition()
    
    root.after(500, auto_enable_gesture)
    
    # 메인 루프 시작
    root.mainloop()

if __name__ == "__main__":
    main()