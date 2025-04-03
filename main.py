import tkinter as tk
from gui import MacroGUI
from recorder import MacroRecorder
from player import MacroPlayer
from editor import MacroEditor
from storage import MacroStorage

def main():
    root = tk.Tk()
    root.title("매크로 프로그램")
    
    # 매크로 관련 모듈 초기화
    storage = MacroStorage()
    recorder = MacroRecorder()
    player = MacroPlayer()
    editor = MacroEditor(storage)
    
    # GUI 초기화 및 실행
    app = MacroGUI(root, recorder, player, editor, storage)
    app.setup_ui()
    
    root.mainloop()

if __name__ == "__main__":
    main()