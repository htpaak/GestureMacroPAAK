from PyQt5.QtCore import Qt
from gesture_processor import process_gesture

class GestureRecognizer:
    def __init__(self):
        # 제스처 기록 상태
        self.is_recording = False
        
        # 기록된 포인트
        self.points = []
        
        # 현재 제스처 기록 시 모디파이어 키
        self.modifiers = Qt.NoModifier
        
        # 키보드 모디파이어와 제스처를 구분하기 위한 접두사
        self.mod_prefixes = {
            Qt.ControlModifier: "CTRL",
            Qt.ShiftModifier: "SHIFT",
            Qt.AltModifier: "ALT",
            Qt.ControlModifier | Qt.ShiftModifier: "CTRL+SHIFT",
            Qt.ControlModifier | Qt.AltModifier: "CTRL+ALT", 
            Qt.ShiftModifier | Qt.AltModifier: "SHIFT+ALT",
            Qt.ControlModifier | Qt.ShiftModifier | Qt.AltModifier: "CTRL+SHIFT+ALT"
        }
    
    def start_recording(self, point, modifiers=Qt.NoModifier):
        """제스처 기록 시작"""
        self.is_recording = True
        self.points = [point]  # 시작 포인트 추가
        self.modifiers = modifiers
    
    def add_point(self, point):
        """마우스 포인트 추가"""
        if self.is_recording:
            self.points.append(point)
    
    def stop_recording(self):
        """제스처 기록 종료 및 인식"""
        self.is_recording = False
        
        # 포인트가 충분한지 확인
        if len(self.points) < 5:
            return "none"
            
        # 제스처 인식
        gesture = process_gesture(self.points)
        
        # 모디파이어가 있는 경우 접두사 추가
        if self.modifiers != Qt.NoModifier:
            for mod_flag, prefix in self.mod_prefixes.items():
                if self.modifiers & mod_flag == mod_flag:
                    return f"{prefix}+{gesture}"
        
        # 모디파이어가 없는 경우 제스처만 반환
        return gesture
    
    def get_current_path(self):
        """현재까지의 제스처 경로 반환 (디버깅/표시용)"""
        if not self.points:
            return ""
            
        # 포인트 목록을 방향으로 변환
        directions = []
        for i in range(1, len(self.points)):
            prev = self.points[i-1]
            curr = self.points[i]
            
            # 포인트 간의 차이 계산
            dx = curr[0] - prev[0]
            dy = curr[1] - prev[1]
            
            # 주요 방향 결정
            if abs(dx) > abs(dy) * 2:
                # 수평 이동이 더 큰 경우
                if dx > 0:
                    directions.append("→")
                else:
                    directions.append("←")
            elif abs(dy) > abs(dx) * 2:
                # 수직 이동이 더 큰 경우
                if dy > 0:
                    directions.append("↓")
                else:
                    directions.append("↑")
            else:
                # 대각선 이동
                if dx > 0 and dy < 0:
                    directions.append("↗")
                elif dx > 0 and dy > 0:
                    directions.append("↘")
                elif dx < 0 and dy < 0:
                    directions.append("↖")
                elif dx < 0 and dy > 0:
                    directions.append("↙")
        
        # 포인트가 너무 많으면 경로를 요약해서 표시
        if len(directions) > 15:
            return "".join(directions[:5]) + "..." + "".join(directions[-5:])
        
        return "".join(directions) 