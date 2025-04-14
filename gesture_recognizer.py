from gesture_processor import process_gesture
import numpy as np # 디버깅을 위해 추가

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
        print(f"[Recognizer] 기록 시작: 시작점={point}, 모디파이어={modifiers}") # 디버깅 로그 추가
    
    def add_point(self, point):
        """마우스 포인트 추가"""
        if self.is_recording:
            # print(f"[Recognizer] 포인트 추가: {point}") # 너무 많은 로그, 필요시 주석 해제
            self.points.append(point)
    
    def stop_recording(self):
        """제스처 녹화 중지 및 인식 결과 반환"""
        print(f"[Recognizer] 녹화 중지 - 총 포인트 수: {len(self.points)}")
        # 디버깅: 입력된 포인트 전체 출력 (너무 길면 일부만 출력하도록 수정 가능)
        if len(self.points) > 0:
             print(f"[Recognizer] 입력된 상대 좌표 시퀀스 (첫 5개, 마지막 5개): {self.points[:5]} ... {self.points[-5:]}")
        else:
             print("[Recognizer] 입력된 좌표 없음")
        
        # 기본값 설정
        gesture_name = "unknown"
        
        # 충분한 포인트가 있는지 확인
        if len(self.points) < 5:
            print("[Recognizer] 인식 실패: 포인트가 너무 적음 (< 5)")
            gesture_name = f"{self.get_modifier_string()}+tooShort"
        else:
            # 제스처 인식 로직 - 복합 방향 패턴 감지
            print("[Recognizer] get_complex_direction 호출")
            direction_pattern = self.get_complex_direction(self.points)
            print(f"[Recognizer] get_complex_direction 결과: {direction_pattern}")
            gesture_name = f"{self.get_modifier_string()}+{direction_pattern}"
        
        # 녹화 상태 초기화
        self.is_recording = False
        
        # 결과 반환
        print(f"[Recognizer] 최종 인식 결과: {gesture_name}")
        return gesture_name
    
    def get_complex_direction(self, points):
        """제스처 포인트를 분석하여 주요 방향 변화를 감지하고 복합 패턴으로 반환"""
        if len(points) < 5:
            print("[Recognizer/Direction] 포인트 부족 (< 5) -> •")
            return "•"
        
        segment_size = max(5, len(points) // 10)
        print(f"[Recognizer/Direction] segment_size: {segment_size}")
        
        # 제스처 시작 시 불안정한 초기 포인트 건너뛰기
        skip_count = segment_size // 2  # 대략 세그먼트 크기의 절반만큼 건너뛰기
        if len(points) < skip_count + 5: # 건너뛴 후에도 충분한 포인트가 남는지 확인
            print(f"[Recognizer/Direction] 포인트 부족 (< {skip_count + 5}) after skipping initial -> •")
            return "•"

        print(f"[Recognizer/Direction] 안정성을 위해 처음 {skip_count}개의 포인트 건너뜀.")
        effective_start_point_index = skip_count
        prev_x, prev_y = points[effective_start_point_index]
        prev_direction = None
        print(f"[Recognizer/Direction] 유효 시작점 (인덱스 {effective_start_point_index}): ({prev_x:.1f}, {prev_y:.1f})")
        
        directions = []
        # 루프 시작점 변경: 건너뛴 지점부터 시작
        for i in range(effective_start_point_index + segment_size, len(points), segment_size):
            # 세그먼트 인덱스 조정
            segment_start_index = i - segment_size
            segment = points[segment_start_index:i]
            if not segment: continue # 세그먼트가 비어있으면 건너뜀

            avg_x = sum(p[0] for p in segment) / len(segment)
            avg_y = sum(p[1] for p in segment) / len(segment)
            dx = avg_x - prev_x
            dy = avg_y - prev_y

            current_direction = self.get_direction_from_delta(dx, dy)
            # 로그 개선: 세그먼트 범위 명시
            print(f"[Recognizer/Direction] 세그먼트 {i//segment_size} (인덱스 {segment_start_index}~{i-1}): Avg=({avg_x:.1f}, {avg_y:.1f}), Delta=({dx:.1f}, {dy:.1f}) -> Dir={current_direction}")

            # 방향이 변경되었거나 첫 방향인 경우
            if prev_direction is None or current_direction != prev_direction:
                min_move_threshold = 20 # 이 값을 조정해볼 수 있습니다.
                if abs(dx) > min_move_threshold or abs(dy) > min_move_threshold:
                    print(f"[Recognizer/Direction]  -> 유효한 방향 변경 감지: {current_direction}")
                    directions.append(current_direction)
                    prev_direction = current_direction
                else:
                    print(f"[Recognizer/Direction]  -> 방향 변경 무시 (이동 거리 < {min_move_threshold})")
            else:
                 print(f"[Recognizer/Direction]  -> 이전 방향과 동일 ({current_direction})")

            prev_x, prev_y = avg_x, avg_y

        # 마지막 세그먼트 처리 (루프에서 처리되지 못한 마지막 부분)
        # 마지막 세그먼트 인덱스 계산 시 skip_count 반영
        processed_points_count = (len(points) - effective_start_point_index)
        last_segment_start_index_relative = (processed_points_count // segment_size) * segment_size
        last_segment_start_index_absolute = effective_start_point_index + last_segment_start_index_relative

        if last_segment_start_index_absolute < len(points):
             last_segment = points[last_segment_start_index_absolute:]
             if len(last_segment) > 0:
                avg_x = sum(p[0] for p in last_segment) / len(last_segment)
                avg_y = sum(p[1] for p in last_segment) / len(last_segment)
                dx = avg_x - prev_x # 마지막 평균점과 그 이전 평균점(prev_x, prev_y) 비교
                dy = avg_y - prev_y
                final_direction = self.get_direction_from_delta(dx, dy)
                # 로그 개선: 세그먼트 범위 명시
                print(f"[Recognizer/Direction] 마지막 세그먼트 (인덱스 {last_segment_start_index_absolute}~끝): Avg=({avg_x:.1f}, {avg_y:.1f}), Delta=({dx:.1f}, {dy:.1f}) -> Dir={final_direction}")
                min_move_threshold = 20
                if (not directions or final_direction != directions[-1]) and (abs(dx) > min_move_threshold or abs(dy) > min_move_threshold):
                    print(f"[Recognizer/Direction]  -> 마지막 유효 방향 추가: {final_direction}")
                    directions.append(final_direction)
                else:
                    print(f"[Recognizer/Direction]  -> 마지막 방향 추가 안함 (중복 또는 이동 거리 부족)")
        
        # 중복 제거 및 길이 제한
        simplified_directions = []
        if directions:
            simplified_directions.append(directions[0])
            for i in range(1, len(directions)):
                if directions[i] != directions[i-1]:
                    simplified_directions.append(directions[i])
        
        print(f"[Recognizer/Direction] 초기 방향 목록: {directions}")
        print(f"[Recognizer/Direction] 단순화된 방향 목록 (중복 제거): {simplified_directions}")
        
        max_directions = 3 # 최대 방향 수를 줄여서 단순화 시도 (기존 5)
        if len(simplified_directions) > max_directions:
            simplified_directions = simplified_directions[:max_directions]
            print(f"[Recognizer/Direction] 최대 {max_directions}개로 제한됨: {simplified_directions}")
        
        # 결과 반환
        if not simplified_directions:
            # 방향 변화가 감지되지 않으면 시작-끝 점 기준으로 단일 방향 결정
            start_x, start_y = points[effective_start_point_index]
            end_x, end_y = points[-1]
            dx = end_x - start_x
            dy = end_y - start_y
            single_direction = self.get_direction_from_delta(dx, dy)
            print(f"[Recognizer/Direction] 유효한 방향 변화 없음. 시작-끝 기준 단일 방향: {single_direction}")
            return single_direction
        
        final_pattern = "".join(simplified_directions)
        print(f"[Recognizer/Direction] 최종 반환 패턴: {final_pattern}")
        return final_pattern
    
    def get_direction_from_delta(self, dx, dy):
        """x, y 변화량으로부터 방향 결정 (화살표 표시: →, ←, ↑, ↓)"""
        # 0으로 나누기 방지
        if dx == 0 and dy == 0:
            return "•" # 제자리
        
        # 대각선 방향 인식 추가 (옵션) -> 현재는 상하좌우만 사용
        # angle = np.degrees(np.arctan2(dy, dx))
        # if -22.5 <= angle < 22.5: return "→"
        # elif 22.5 <= angle < 67.5: return "↗"
        # elif 67.5 <= angle < 112.5: return "↑"
        # elif 112.5 <= angle < 157.5: return "↖"
        # elif abs(angle) >= 157.5: return "←"
        # elif -157.5 <= angle < -112.5: return "↙"
        # elif -112.5 <= angle < -67.5: return "↓"
        # elif -67.5 <= angle < -22.5: return "↘"
        
        # dx와 dy 중 절대값이 더 큰 방향으로 결정 (기존 로직)
        if abs(dx) > abs(dy):
            return "→" if dx > 0 else "←"
        else:
            # dy == 0 인 경우 수평 이동으로 간주 (↑/↓ 모호성 제거)
            if dy == 0:
                return "→" if dx > 0 else "←"
            return "↓" if dy > 0 else "↑"
    
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
            direction = self.get_direction_from_delta(dx, dy)
            directions.append(direction)
        
        # 중복 제거
        simplified_directions = []
        if directions:
            simplified_directions.append(directions[0])
            for i in range(1, len(directions)):
                 if directions[i] != directions[i-1]:
                    simplified_directions.append(directions[i])
        
        # 포인트가 너무 많으면 경로를 요약해서 표시
        if len(simplified_directions) > 15:
            return "".join(simplified_directions[:5]) + "..." + "".join(simplified_directions[-5:])
        
        return "".join(simplified_directions)
    
    def get_modifier_string(self):
        """현재 모디파이어 키 조합에 대한 문자열 반환"""
        if self.modifiers in self.mod_prefixes:
            return self.mod_prefixes[self.modifiers]
        return "NONE"  # 모디파이어가 없는 경우 