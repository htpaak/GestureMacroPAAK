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

            # 키보드 이벤트 처리 (ESC 및 기타 키 해제 처리)
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
            try:
                print("GestureCanvas.destroy() 메서드 호출됨")
                
                # 창을 닫기 전에 가능한 모든 에러 방지 조치
                try:
                    # 기존 이벤트 바인딩 제거
                    self.window.unbind('<Escape>')
                    self.window.unbind('<KeyPress>')
                    self.window.unbind('<KeyRelease>')
                    self.window.unbind('<Button>')
                    self.window.unbind('<Motion>')
                    
                    # 프로토콜 핸들러 제거
                    self.window.protocol("WM_DELETE_WINDOW", lambda: None)
                except Exception as bind_err:
                    print(f"바인딩 제거 중 오류(무시됨): {bind_err}")
                    pass
                
                # 캔버스의 모든 항목 제거
                if self.canvas:
                    try:
                        self.canvas.delete("all")
                    except Exception as canvas_err:
                        print(f"캔버스 내용 제거 중 오류(무시됨): {canvas_err}")
                        pass
                
                # 창 숨기기 (destroy 전 창을 보이지 않게 함)
                try:
                    self.window.withdraw()
                except Exception as withdraw_err:
                    print(f"창 숨기기 중 오류(무시됨): {withdraw_err}")
                    pass
                
                # 모든 자식 위젯 제거
                try:
                    for widget in self.window.winfo_children():
                        widget.destroy()
                except Exception as children_err:
                    print(f"자식 위젯 제거 중 오류(무시됨): {children_err}")
                    pass
                
                # Tkinter destroy 호출
                try:
                    self.window.destroy()
                    print("GestureCanvas 창 destroy() 호출 성공")
                except Exception as destroy_err:
                    print(f"창 destroy() 호출 중 오류: {destroy_err}")
                    
                    # 대체 방법 시도 - update 호출 후 다시 시도
                    try:
                        import tkinter as tk
                        tk._default_root.update()
                        self.window.destroy()
                        print("update 후 destroy 재시도 성공")
                    except Exception as update_err:
                        print(f"update 후 destroy 재시도 실패: {update_err}")
                
                print("GestureCanvas 창이 성공적으로 닫힘")
            except Exception as e:
                print(f"GestureCanvas 창 닫기 오류: {e}")
                import traceback
                traceback.print_exc()
            finally:
                # 참조 정리
                self.window = None
                self.canvas = None
                print("GestureCanvas 참조가 모두 초기화됨")
    
    def cancel(self):
        """녹화 취소"""
        print("GestureCanvas.cancel() 메서드 호출됨 - ESC 키 또는 창 닫기로 취소")
        
        # 콜백 호출 전에 참조 저장 (객체 정리 후에도 호출 가능하도록)
        callback = self.on_cancel
        
        # 캔버스 내용 지우기
        self.clear()
        
        # 창 종료하기
        if self.window:
            # 이벤트 모두 해제 (처리 중 문제를 방지하기 위해)
            for binding in ['<Escape>', '<KeyPress>', '<KeyRelease>', '<Button>', '<Motion>', '<Configure>']:
                try:
                    self.window.unbind(binding)
                except Exception as e:
                    print(f"바인딩 해제 오류(무시됨): {e}")
            
            # 프로토콜 핸들러도 제거
            try:
                self.window.protocol("WM_DELETE_WINDOW", lambda: None)
            except Exception as e:
                print(f"프로토콜 핸들러 제거 오류(무시됨): {e}")
            
            # 모든 자식 위젯 제거
            try:
                for widget in self.window.winfo_children():
                    widget.destroy()
            except Exception as e:
                print(f"자식 위젯 제거 오류(무시됨): {e}")
            
            # 먼저 창 숨기기
            try:
                self.window.withdraw()
                print("창 성공적으로 숨김")
            except Exception as e:
                print(f"창 숨기기 오류(무시됨): {e}")
            
            # 창 종료
            try:
                self.window.destroy()
                print("창 성공적으로 종료됨")
            except Exception as e:
                print(f"창 종료 오류: {e}")
                
                # 대체 방법 시도 - 메인 루프 처리 후 다시 시도
                try:
                    import tkinter as tk
                    if tk._default_root:
                        tk._default_root.update()
                        self.window.destroy()
                        print("update 후 창 종료 성공")
                except Exception as e2:
                    print(f"대체 종료 방법 오류: {e2}")
            
            # 모든 참조 제거
            self.window = None
            self.canvas = None
            print("모든 창 참조 제거 완료")
        
        # 객체 정리 후 취소 콜백 호출
        if callback:
            print("취소 콜백 함수 호출")
            try:
                callback()
                print("취소 콜백 함수 호출 완료")
            except Exception as e:
                print(f"취소 콜백 함수 호출 중 오류: {e}")
                import traceback
                traceback.print_exc()
    
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