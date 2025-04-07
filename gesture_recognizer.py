from gesture_processor import process_gesture

class GestureRecognizer:
    def __init__(self):
        # 제스처 기록 상태
        self.is_recording = False
        
        # 기록된 포인트
        self.points = []
        
        # 현재 제스처 기록 시 모디파이어 키 (정수 타입 사용)
        self.modifiers = 0
        
        # 키보드 모디파이어와 제스처를 구분하기 위한 접두사 (정수 타입으로 변경)
        self.mod_prefixes = {
            1: "CTRL",           # CTRL_MODIFIER
            2: "SHIFT",          # SHIFT_MODIFIER
            4: "ALT",            # ALT_MODIFIER
            3: "CTRL+SHIFT",     # CTRL_MODIFIER | SHIFT_MODIFIER
            5: "CTRL+ALT",       # CTRL_MODIFIER | ALT_MODIFIER
            6: "SHIFT+ALT",      # SHIFT_MODIFIER | ALT_MODIFIER
            7: "CTRL+SHIFT+ALT"  # CTRL_MODIFIER | SHIFT_MODIFIER | ALT_MODIFIER
        }
    
    def start_recording(self, point, modifiers=0):
        """제스처 기록 시작"""
        self.is_recording = True
        self.points = [point]  # 시작 포인트 추가
        self.modifiers = modifiers
    
    def add_point(self, point):
        """마우스 포인트 추가"""
        if self.is_recording:
            self.points.append(point)
    
    def stop_recording(self):
        """제스처 녹화 중지 및 인식 결과 반환"""
        print(f"제스처 녹화 중지 - 포인트 수: {len(self.points)}")  # 디버깅 로그 추가
        
        # 기본값 설정
        gesture_name = "unknown"
        
        # 충분한 포인트가 있는지 확인
        if len(self.points) < 5:
            print("제스처 인식 실패: 포인트가 충분하지 않음")  # 디버깅 로그 추가
            gesture_name = f"{self.get_modifier_string()}+tooShort"
        else:
            # 제스처 인식 로직
            # 실제 인식 로직을 여기에 구현 (현재는 간단히 모디파이어 키 조합으로만 구분)
            gesture_name = f"{self.get_modifier_string()}+{self.points[0][0]}_{self.points[0][1]}"
        
        # 녹화 상태 초기화
        self.is_recording = False
        
        # 결과 반환
        print(f"제스처 인식 결과: {gesture_name}")  # 디버깅 로그 추가
        return gesture_name
    
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
    
    def get_modifier_string(self):
        """현재 모디파이어 키 조합에 대한 문자열 반환"""
        if self.modifiers in self.mod_prefixes:
            return self.mod_prefixes[self.modifiers]
        return "NONE"  # 모디파이어가 없는 경우 