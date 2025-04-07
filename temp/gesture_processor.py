import math
import numpy as np
from scipy import signal

def process_gesture(points):
    """
    마우스 포인트 시퀀스를 분석하여 제스처 패턴 식별
    
    Args:
        points: 마우스 포인트 리스트 [(x1, y1), (x2, y2), ...]
        
    Returns:
        gesture_name: 식별된 제스처 이름
    """
    # 포인트가 충분하지 않으면 제스처 인식 불가
    if len(points) < 5:
        return "none"
        
    # 좌표 추출
    x_coords = [p[0] for p in points]
    y_coords = [p[1] for p in points]
    
    # 노이즈 제거를 위한 스무딩
    x_coords = smooth_coordinates(x_coords)
    y_coords = smooth_coordinates(y_coords)
    
    # 방향 패턴 추출
    directions = extract_directions(x_coords, y_coords)
    
    # 방향 패턴 단순화 (연속된 같은 방향 제거)
    simplified_dirs = simplify_directions(directions)
    
    # 기본 패턴 인식
    if is_horizontal_swipe(simplified_dirs, x_coords):
        if x_coords[-1] > x_coords[0]:
            return "swipe-right"
        else:
            return "swipe-left"
            
    if is_vertical_swipe(simplified_dirs, y_coords):
        if y_coords[-1] > y_coords[0]:
            return "swipe-down"
        else:
            return "swipe-up"
            
    if is_diagonal_swipe(simplified_dirs):
        if "NE" in simplified_dirs or "SE" in simplified_dirs:
            if "NE" in simplified_dirs and "SE" not in simplified_dirs:
                return "swipe-up-right"
            elif "SE" in simplified_dirs and "NE" not in simplified_dirs:
                return "swipe-down-right"
        else:
            if "NW" in simplified_dirs and "SW" not in simplified_dirs:
                return "swipe-up-left"
            elif "SW" in simplified_dirs and "NW" not in simplified_dirs:
                return "swipe-down-left"
    
    # 원 모양 패턴 인식
    if is_circle(x_coords, y_coords):
        direction = determine_circle_direction(x_coords, y_coords)
        if direction > 0:
            return "circle-clockwise"
        else:
            return "circle-counterclockwise"
            
    # 지그재그 패턴
    if is_zigzag(simplified_dirs):
        return "zigzag"
        
    # N 모양 패턴
    if is_n_shape(simplified_dirs):
        return "N-shape"
        
    # Z 모양 패턴
    if is_z_shape(simplified_dirs):
        return "Z-shape"
        
    # V 모양 패턴
    if is_v_shape(simplified_dirs):
        return "V-shape"
        
    # ^ 모양 (캐럿) 패턴
    if is_caret_shape(simplified_dirs):
        # 방향에 따라 구분
        if "E" in simplified_dirs and "W" not in simplified_dirs:
            return "caret-right"
        elif "W" in simplified_dirs and "E" not in simplified_dirs:
            return "caret-left"
        elif "S" in simplified_dirs and "N" not in simplified_dirs:
            return "caret-down"
        else:
            return "caret-up"
    
    # 인식된 제스처가 없을 경우
    return "unknown"

def smooth_coordinates(coords, window_size=5):
    """좌표 스무딩을 통한 노이즈 제거"""
    if len(coords) < window_size:
        return coords
        
    # 이동 평균 필터 적용
    return signal.savgol_filter(coords, window_size, 2).tolist()

def extract_directions(x_coords, y_coords):
    """좌표에서 방향 패턴 추출"""
    directions = []
    
    for i in range(1, len(x_coords)):
        dx = x_coords[i] - x_coords[i-1]
        dy = y_coords[i] - y_coords[i-1]
        
        # 작은 움직임은 무시
        if abs(dx) < 5 and abs(dy) < 5:
            continue
            
        # 8방향 결정
        if abs(dx) > abs(dy) * 2:
            directions.append("E" if dx > 0 else "W")
        elif abs(dy) > abs(dx) * 2:
            directions.append("S" if dy > 0 else "N")
        else:
            if dx > 0 and dy < 0:
                directions.append("NE")
            elif dx > 0 and dy > 0:
                directions.append("SE")
            elif dx < 0 and dy < 0:
                directions.append("NW")
            elif dx < 0 and dy > 0:
                directions.append("SW")
    
    return directions

def simplify_directions(directions):
    """연속된 같은 방향 제거"""
    if not directions:
        return []
        
    simplified = [directions[0]]
    
    for i in range(1, len(directions)):
        if directions[i] != simplified[-1]:
            simplified.append(directions[i])
            
    return simplified

def is_horizontal_swipe(dirs, x_coords):
    """수평 스와이프 인식"""
    # 수평 방향이 대부분인지 확인
    horizontal_count = dirs.count("E") + dirs.count("W")
    
    # 이동 거리도 확인
    distance = abs(x_coords[-1] - x_coords[0])
    
    return (horizontal_count > len(dirs) * 0.6 and 
            (dirs.count("E") > dirs.count("W") * 3 or dirs.count("W") > dirs.count("E") * 3) and
            distance > 50)

def is_vertical_swipe(dirs, y_coords):
    """수직 스와이프 인식"""
    # 수직 방향이 대부분인지 확인
    vertical_count = dirs.count("N") + dirs.count("S")
    
    # 이동 거리도 확인
    distance = abs(y_coords[-1] - y_coords[0])
    
    return (vertical_count > len(dirs) * 0.6 and 
            (dirs.count("N") > dirs.count("S") * 3 or dirs.count("S") > dirs.count("N") * 3) and
            distance > 50)

def is_diagonal_swipe(dirs):
    """대각선 스와이프 인식"""
    # 대각선 방향이 대부분인지 확인
    diagonal_count = (dirs.count("NE") + dirs.count("NW") + 
                     dirs.count("SE") + dirs.count("SW"))
    
    return diagonal_count > len(dirs) * 0.6

def is_circle(x_coords, y_coords):
    """원 모양 인식"""
    # 시작점과 끝점이 가까운지 확인
    start = (x_coords[0], y_coords[0])
    end = (x_coords[-1], y_coords[-1])
    
    distance = math.sqrt((end[0] - start[0])**2 + (end[1] - start[1])**2)
    
    # 전체 경로 길이 계산
    path_length = 0
    for i in range(1, len(x_coords)):
        dx = x_coords[i] - x_coords[i-1]
        dy = y_coords[i] - y_coords[i-1]
        path_length += math.sqrt(dx**2 + dy**2)
    
    # 원은 시작점과 끝점이 가깝고, 경로 길이가 충분히 길어야 함
    return distance < path_length * 0.3 and path_length > 200

def determine_circle_direction(x_coords, y_coords):
    """원의 방향 결정 (시계방향 또는 반시계방향)"""
    # 원의 중심 계산
    center_x = sum(x_coords) / len(x_coords)
    center_y = sum(y_coords) / len(y_coords)
    
    # 각도 변화 계산
    angles = []
    for i in range(len(x_coords)):
        dx = x_coords[i] - center_x
        dy = y_coords[i] - center_y
        angles.append(math.atan2(dy, dx))
    
    # 각도 변화량 계산
    angle_changes = []
    for i in range(1, len(angles)):
        change = angles[i] - angles[i-1]
        # 각도 변화가 큰 경우 (-π에서 π로 이동)
        if change > math.pi:
            change -= 2 * math.pi
        elif change < -math.pi:
            change += 2 * math.pi
        angle_changes.append(change)
    
    # 각도 변화 합계가 양수면 시계방향, 음수면 반시계방향
    return sum(angle_changes)

def is_zigzag(dirs):
    """지그재그 패턴 인식"""
    if len(dirs) < 3:
        return False
    
    # 방향이 반복적으로 바뀌는지 확인
    direction_changes = 0
    for i in range(1, len(dirs)):
        # 수평 방향 변경 확인
        if (dirs[i-1] in ["E", "NE", "SE"] and dirs[i] in ["W", "NW", "SW"]) or \
           (dirs[i-1] in ["W", "NW", "SW"] and dirs[i] in ["E", "NE", "SE"]):
            direction_changes += 1
    
    return direction_changes >= 2

def is_n_shape(dirs):
    """N 모양 패턴 인식"""
    if len(dirs) < 3:
        return False
    
    # N 모양 패턴: 위->아래->위 또는 유사한 패턴
    n_pattern = ["N", "SE", "N"] 
    n_pattern2 = ["NW", "S", "NE"]
    
    # 주요 방향만 추출
    main_dirs = []
    for d in dirs:
        if len(main_dirs) < 3:
            main_dirs.append(d)
        else:
            break
    
    # 패턴 매칭
    return "".join(main_dirs).find("".join(n_pattern)) >= 0 or \
           "".join(main_dirs).find("".join(n_pattern2)) >= 0

def is_z_shape(dirs):
    """Z 모양 패턴 인식"""
    if len(dirs) < 3:
        return False
    
    # Z 모양 패턴: 왼쪽위->오른쪽 또는 오른쪽위->왼쪽
    z_pattern = ["E", "SW", "E"]
    z_pattern2 = ["W", "SE", "W"]
    
    # 주요 방향만 추출
    main_dirs = []
    for d in dirs:
        if len(main_dirs) < 3:
            main_dirs.append(d)
        else:
            break
    
    # 패턴 매칭
    return "".join(main_dirs).find("".join(z_pattern)) >= 0 or \
           "".join(main_dirs).find("".join(z_pattern2)) >= 0

def is_v_shape(dirs):
    """V 모양 패턴 인식"""
    if len(dirs) < 3:
        return False
    
    # V 모양 패턴: 아래로 내려갔다가 올라옴
    v_pattern1 = ["SW", "SE"]
    v_pattern2 = ["SE", "SW"]
    
    # 주요 방향만 추출
    main_dirs = []
    for d in dirs:
        if len(main_dirs) < 2:
            main_dirs.append(d)
        else:
            break
    
    # 패턴 매칭
    return "".join(main_dirs).find("".join(v_pattern1)) >= 0 or \
           "".join(main_dirs).find("".join(v_pattern2)) >= 0

def is_caret_shape(dirs):
    """캐럿(^) 모양 패턴 인식"""
    if len(dirs) < 3:
        return False
    
    # ^ 모양 패턴: 위로 올라갔다가 내려옴
    caret_pattern1 = ["NW", "NE"]
    caret_pattern2 = ["NE", "NW"]
    
    # 주요 방향만 추출
    main_dirs = []
    for d in dirs:
        if len(main_dirs) < 2:
            main_dirs.append(d)
        else:
            break
    
    # 패턴 매칭
    return "".join(main_dirs).find("".join(caret_pattern1)) >= 0 or \
           "".join(main_dirs).find("".join(caret_pattern2)) >= 0 