import tkinter as tk
from recorder import MacroRecorder
from player import MacroPlayer
from editor import MacroEditor
from storage import MacroStorage
from gui import MacroGUI

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
    
    # GUI 초기화
    gui = MacroGUI(root, recorder, player, editor, storage)
    gui.setup_ui()
    
    # 메인 루프 시작
    root.mainloop()

if __name__ == "__main__":
    main()