import tkinter as tk
from tkinter import messagebox

class GestureCanvas:
    """제스처 녹화를 위한 향상된 캔버스 클래스"""
    
    def __init__(self, parent=None, on_cancel=None, line_color="red", is_overlay=False):
        """
        제스처 녹화 캔버스 초기화
        
        Parameters:
        - parent: 부모 창 (기본값: None, 없으면 새 창 생성)
        - on_cancel: 취소 시 실행할 콜백 함수 (기본값: None)
        - line_color: 제스처 경로 선 색상 (기본값: "red")
        - is_overlay: 오버레이 모드 여부 (기본값: False)
        """
        self.parent = parent
        self.on_cancel = on_cancel
        self.line_color = line_color
        self.is_overlay = is_overlay
        self.window = None
        self.canvas = None
        self.points = []
        
    def create(self):
        """캔버스 창 생성"""
        # 부모 창이 없으면 새 창 생성 (오버레이 또는 일반 Toplevel)
        if not self.parent:
            self.window = tk.Toplevel()
            if self.is_overlay:
                self.window.overrideredirect(True) # 창 테두리 제거
                # 화면 크기 가져오기
                screen_width = self.window.winfo_screenwidth()
                screen_height = self.window.winfo_screenheight()
                # 전체 화면 크기로 설정
                self.window.geometry(f"{screen_width}x{screen_height}+0+0")
                self.window.attributes('-topmost', True)  # 항상 위에 표시
                # 투명 배경 설정 (예: 'magenta'를 투명색으로)
                transparent_color = 'magenta'
                self.window.attributes('-transparentcolor', transparent_color)
                self.canvas = tk.Canvas(self.window, bg=transparent_color, highlightthickness=0)
            else: # 기존 제스처 녹화용 Toplevel (반투명)
                self.window.title("제스처 녹화")
                self.window.attributes('-alpha', 0.7)  # 반투명 창
                # 화면 크기 가져오기
                screen_width = self.window.winfo_screenwidth()
                screen_height = self.window.winfo_screenheight()
                # 전체 화면 크기로 설정
                self.window.geometry(f"{screen_width}x{screen_height}+0+0")
                self.window.attributes('-topmost', True)  # 항상 위에 표시
                self.canvas = tk.Canvas(self.window, bg="white")
                # 사용자에게 안내 메시지 표시 (오버레이가 아닐 때만)
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

            self.window.bind('<Escape>', lambda e: self.cancel())
            self.window.protocol("WM_DELETE_WINDOW", self.cancel)
        else:
            # 부모 창이 있으면 해당 부모 내에 캔버스 생성
            self.canvas = tk.Canvas(self.parent, bg="white", highlightthickness=0)
        
        if self.canvas: # 캔버스가 성공적으로 생성되었는지 확인
            self.canvas.pack(fill=tk.BOTH, expand=True)
        return self.canvas
    
    def add_point(self, x, y, color=None, size=3):
        """점을 추가하고, 이전 점에서 현재 점까지 선을 그립니다."""
        if not self.canvas:
            return

        current_point = (x, y)
        self.points.append(current_point)

        # 오버레이 모드에서는 점을 그리지 않고 선만 그림
        if not self.is_overlay:
            # 점 그리기 (기존 add_point의 기능과 유사)
            self.canvas.create_oval(
                x-size, y-size, x+size, y+size, 
                fill=color if color else self.line_color, 
                outline=color if color else self.line_color, 
                tags="gesture_points"
            )

        if len(self.points) > 1:
            prev_point = self.points[-2]
            # 선 그리기 (add_line 호출 대신 직접 구현 또는 add_line 활용)
            self.add_line(prev_point[0], prev_point[1], current_point[0], current_point[1], 
                          color if color else self.line_color, width=2 if self.is_overlay else 2) # 오버레이 시 선 두께 조정 가능
    
    def add_line(self, x1, y1, x2, y2, color=None, width=2):
        """선 추가"""
        if self.canvas:
            self.canvas.create_line(
                x1, y1, x2, y2,
                fill=color if color else self.line_color, width=width, tags="gesture_lines"
            )
    
    def clear(self):
        """캔버스 내용 지우기"""
        if self.canvas:
            self.canvas.delete("gesture")
            self.canvas.delete("gesture_points")
            self.canvas.delete("gesture_lines")
        self.points = []
    
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
        
        # 캔버스 내용도 지움
        self.clear()
        
        if self.window:
            self.window.destroy()
            self.window = None
            self.canvas = None
    
    def set_line_color(self, color):
        """선 색상을 설정합니다."""
        self.line_color = color
    
    def show(self):
        """오버레이 윈도우를 보이도록 설정"""
        if self.window and self.is_overlay:
            self.window.deiconify() # 창을 보이게 함
            self.window.attributes("-topmost", True) # 항상 위로 유지
    
    def hide(self):
        """오버레이 윈도우를 숨기도록 설정"""
        if self.window and self.is_overlay:
            self.clear() # 숨기기 전에 현재 그려진 내용 삭제
            self.window.withdraw() # 창을 숨김 