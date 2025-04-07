import tkinter as tk
from tkinter import messagebox

class GestureCanvas:
    """제스처 녹화를 위한 향상된 캔버스 클래스"""
    
    def __init__(self, parent=None, on_cancel=None):
        """
        제스처 녹화 캔버스 초기화
        
        Parameters:
        - parent: 부모 창 (기본값: None, 없으면 새 창 생성)
        - on_cancel: 취소 시 실행할 콜백 함수 (기본값: None)
        """
        self.parent = parent
        self.on_cancel = on_cancel
        self.window = None
        self.canvas = None
        
    def create(self):
        """캔버스 창 생성"""
        # 부모 창이 없으면 새 창 생성
        if not self.parent:
            self.window = tk.Toplevel()
            self.window.title("제스처 녹화")
            self.window.attributes('-alpha', 0.7)  # 반투명 창
            
            # 화면 크기 가져오기
            screen_width = self.window.winfo_screenwidth()
            screen_height = self.window.winfo_screenheight()
            
            # 전체 화면 크기로 설정
            self.window.geometry(f"{screen_width}x{screen_height}+0+0")
            
            # 창 속성 설정
            self.window.attributes('-topmost', True)  # 항상 위에 표시
            
            # 캔버스 생성
            self.canvas = tk.Canvas(self.window, bg="white")
            self.canvas.pack(fill=tk.BOTH, expand=True)
            
            # ESC 키로 창 닫기
            self.window.bind('<Escape>', lambda e: self.cancel())
            
            # 창이 닫힐 때 이벤트
            self.window.protocol("WM_DELETE_WINDOW", self.cancel)
            
            # 사용자에게 안내 메시지 표시
            self.canvas.create_text(
                screen_width//2, 50, 
                text="제스처 녹화를 시작합니다.\n" 
                     "Ctrl, Shift, Alt 키를 누른 상태에서 마우스로 제스처를 그려주세요.\n"
                     "키를 떼면 제스처 녹화가 완료됩니다.\n"
                     "ESC 키를 누르면 취소됩니다.",
                font=("Arial", 14),
                fill="black",
                justify=tk.CENTER
            )
        else:
            self.canvas = tk.Canvas(self.parent, bg="white")
            self.canvas.pack(fill=tk.BOTH, expand=True)
        
        return self.canvas
    
    def add_point(self, x, y, color="blue", size=3):
        """점 추가"""
        if self.canvas:
            self.canvas.create_oval(
                x-size, y-size, x+size, y+size, 
                fill=color, outline=color, tags="gesture"
            )
    
    def add_line(self, x1, y1, x2, y2, color="red", width=2):
        """선 추가"""
        if self.canvas:
            self.canvas.create_line(
                x1, y1, x2, y2,
                fill=color, width=width, tags="gesture"
            )
    
    def clear(self):
        """캔버스 내용 지우기"""
        if self.canvas:
            self.canvas.delete("gesture")
    
    def destroy(self):
        """캔버스 창 닫기"""
        if self.window:
            self.window.destroy()
            self.window = None
            self.canvas = None
    
    def cancel(self):
        """녹화 취소"""
        if self.on_cancel:
            self.on_cancel()
        
        if self.window:
            self.window.destroy()
            self.window = None
            self.canvas = None 