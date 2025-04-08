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
            1: "Ctrl",           # CTRL_MODIFIER
            2: "SHIFT",          # SHIFT_MODIFIER
            4: "Alt",            # ALT_MODIFIER
            3: "Ctrl+SHIFT",     # CTRL_MODIFIER | SHIFT_MODIFIER
            5: "Ctrl+Alt",       # CTRL_MODIFIER | ALT_MODIFIER
            6: "SHIFT+Alt",      # SHIFT_MODIFIER | ALT_MODIFIER
            7: "Ctrl+SHIFT+Alt"  # CTRL_MODIFIER | SHIFT_MODIFIER | ALT_MODIFIER
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
            # 제스처 인식 로직 - 복합 방향 패턴 감지
            direction_pattern = self.get_complex_direction(self.points)
            gesture_name = f"{self.get_modifier_string()}+{direction_pattern}"
        
        # 녹화 상태 초기화
        self.is_recording = False
        
        # 결과 반환
        print(f"제스처 인식 결과: {gesture_name}")  # 디버깅 로그 추가
        return gesture_name
    
    def get_complex_direction(self, points):
        """제스처 포인트를 분석하여 주요 방향 변화를 감지하고 복합 패턴으로 반환"""
        if len(points) < 5:
            return "•"  # 점 이모티콘 (포인트가 충분하지 않은 경우)
        
        # 주요 방향 변화 식별
        segment_size = max(5, len(points) // 10)  # 최소 5개 포인트, 또는 전체의 1/10
        
        # 방향 변화를 감지하기 위해 이동 평균 계산
        directions = []
        
        prev_x, prev_y = points[0]
        prev_direction = None
        
        for i in range(segment_size, len(points), segment_size):
            # 현재 세그먼트 평균 좌표 계산
            segment = points[i-segment_size:i]
            avg_x = sum(p[0] for p in segment) / len(segment)
            avg_y = sum(p[1] for p in segment) / len(segment)
            
            # 이전 위치와의 차이 계산
            dx = avg_x - prev_x
            dy = avg_y - prev_y
            
            # 주요 방향 결정
            current_direction = self.get_direction_from_delta(dx, dy)
            
            # 방향이 변경되었는지 확인
            if prev_direction is None or current_direction != prev_direction:
                # 추가할 가치가 있는 방향인지 확인 (무의미한 작은 움직임 필터링)
                if abs(dx) > 20 or abs(dy) > 20:  # 최소 이동 거리
                    directions.append(current_direction)
                    prev_direction = current_direction
            
            prev_x, prev_y = avg_x, avg_y
        
        # 마지막 방향 추가 (이전 루프에서 추가되지 않았을 경우)
        if len(points) > segment_size:
            end_x, end_y = points[-1]
            final_dx = end_x - prev_x
            final_dy = end_y - prev_y
            
            final_direction = self.get_direction_from_delta(final_dx, final_dy)
            if (not directions or final_direction != directions[-1]) and (abs(final_dx) > 20 or abs(final_dy) > 20):
                directions.append(final_direction)
        
        # 중복 제거 (연속된 같은 방향)
        simplified_directions = []
        for d in directions:
            if not simplified_directions or d != simplified_directions[-1]:
                simplified_directions.append(d)
        
        # 최대 5개 방향으로 제한 (3개에서 5개로 증가)
        if len(simplified_directions) > 5:
            simplified_directions = simplified_directions[:5]
        
        # 결과 반환
        if not simplified_directions:
            # 단일 방향 (시작점과 끝점)
            start_x, start_y = points[0]
            end_x, end_y = points[-1]
            dx = end_x - start_x
            dy = end_y - start_y
            return self.get_direction_from_delta(dx, dy)
        
        return "".join(simplified_directions)
    
    def get_direction_from_delta(self, dx, dy):
        """x, y 변화량으로부터 방향 결정 (화살표 표시: →, ←, ↑, ↓)"""
        # dx와 dy 중 절대값이 더 큰 방향으로 결정
        if abs(dx) > abs(dy):
            return "→" if dx > 0 else "←"  # 오른쪽, 왼쪽
        else:
            return "↓" if dy > 0 else "↑"  # 아래, 위
    
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
            
            # 주요 방향 결정 (대각선 없이 상하좌우만)
            if abs(dx) > abs(dy):
                # 수평 이동이 더 큰 경우
                if dx > 0:
                    directions.append("→")  # 오른쪽
                else:
                    directions.append("←")  # 왼쪽
            else:
                # 수직 이동이 더 큰 경우
                if dy > 0:
                    directions.append("↓")  # 아래
                else:
                    directions.append("↑")  # 위
        
        # 포인트가 너무 많으면 경로를 요약해서 표시
        if len(directions) > 15:
            return "".join(directions[:5]) + "..." + "".join(directions[-5:])
        
        return "".join(directions)
    
    def get_modifier_string(self):
        """현재 모디파이어 키 조합에 대한 문자열 반환"""
        if self.modifiers in self.mod_prefixes:
            return self.mod_prefixes[self.modifiers]
        return "NONE"  # 모디파이어가 없는 경우 