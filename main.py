import tkinter as tk
import os
import sys
import time
from recorder import MacroRecorder
from player import MacroPlayer
from editor import MacroEditor
from storage import MacroStorage
from simple_gui import SimpleGUI
from gesture_manager import GestureManager

def auto_enable_gesture():
    """자동으로 제스처 인식 활성화"""
    print("제스처 인식 자동 활성화")
    gui.gesture_enabled.set(True)
    gui.toggle_gesture_recognition()

def main():
    # 루트 윈도우 생성
    root = tk.Tk()
    
    # 전역 변수 설정
    global gui, recorder, player, editor, storage, gesture_manager
    
    # 디버깅 정보 출력
    print("시스템 정보:", sys.platform)
    print("현재 디렉토리:", os.getcwd())
    
    # 인스턴스 생성
    storage = MacroStorage()
    recorder = MacroRecorder()
    player = MacroPlayer()
    editor = MacroEditor(storage)
    
    # 제스처 매니저 초기화
    gesture_manager = GestureManager(player, storage, recorder)
    
    # GUI 초기화
    gui = SimpleGUI(root, recorder, player, editor, storage, gesture_manager)
    gui.setup_ui()
    
    # 자동으로 제스처 인식 활성화 (0.5초 후)
    root.after(500, auto_enable_gesture)
    
    # 메인 루프 시작
    root.mainloop()

if __name__ == "__main__":
    main()