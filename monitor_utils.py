import screeninfo

def get_monitors():
    """모든 모니터 정보를 리스트로 반환합니다."""
    return screeninfo.get_monitors()

def get_primary_monitor():
    """주 모니터 정보를 반환합니다."""
    monitors = get_monitors()
    for m in monitors:
        if m.is_primary:
            return m
    # 주 모니터를 찾지 못한 경우 첫 번째 모니터 반환 (예외 처리)
    return monitors[0] if monitors else None

def get_virtual_desktop_bounds():
    """전체 가상 데스크탑의 경계를 계산하여 (min_x, min_y, max_x, max_y) 튜플로 반환합니다."""
    monitors = get_monitors()
    if not monitors:
        return (0, 0, 0, 0)

    min_x = min(m.x for m in monitors)
    min_y = min(m.y for m in monitors)
    max_x = max(m.x + m.width for m in monitors)
    max_y = max(m.y + m.height for m in monitors)

    return (min_x, min_y, max_x, max_y)

def absolute_to_relative(x, y, monitor):
    """절대 좌표 (x, y)를 주어진 모니터의 상대 좌표로 변환합니다."""
    if not monitor:
        raise ValueError("유효한 모니터 객체를 제공해야 합니다.")
    return (x - monitor.x, y - monitor.y)

def relative_to_absolute(rel_x, rel_y, monitor):
    """주어진 모니터의 상대 좌표 (rel_x, rel_y)를 절대 좌표로 변환합니다."""
    if not monitor:
        raise ValueError("유효한 모니터 객체를 제공해야 합니다.")
    return (rel_x + monitor.x, rel_y + monitor.y)

def get_monitor_from_point(x, y):
    """주어진 절대 좌표 (x, y)가 속한 모니터 객체를 반환합니다.

    좌표가 어떤 모니터에도 속하지 않으면 None을 반환합니다.
    """
    monitors = get_monitors()
    for m in monitors:
        if m.x <= x < m.x + m.width and m.y <= y < m.y + m.height:
            return m
    return None

# 예시 사용법
if __name__ == "__main__":
    print("모든 모니터 정보:")
    all_monitors = get_monitors()
    for i, monitor in enumerate(all_monitors):
        print(f"  모니터 {i}: {monitor}")

    primary = get_primary_monitor()
    print(f"\n주 모니터: {primary}")

    bounds = get_virtual_desktop_bounds()
    print(f"\n가상 데스크탑 경계: {bounds}")

    # 테스트 좌표 (예: 첫 번째 모니터의 중앙)
    if all_monitors:
        test_monitor = all_monitors[0]
        test_rel_x, test_rel_y = test_monitor.width // 2, test_monitor.height // 2
        abs_x, abs_y = relative_to_absolute(test_rel_x, test_rel_y, test_monitor)
        print(f"\n모니터 {all_monitors.index(test_monitor)}의 상대 좌표 ({test_rel_x}, {test_rel_y}) -> 절대 좌표 ({abs_x}, {abs_y})")

        rel_x_check, rel_y_check = absolute_to_relative(abs_x, abs_y, test_monitor)
        print(f"절대 좌표 ({abs_x}, {abs_y}) -> 모니터 {all_monitors.index(test_monitor)}의 상대 좌표 ({rel_x_check}, {rel_y_check})")

        containing_monitor = get_monitor_from_point(abs_x, abs_y)
        if containing_monitor:
            print(f"절대 좌표 ({abs_x}, {abs_y})는 모니터 {all_monitors.index(containing_monitor)}에 속합니다.")
        else:
            print(f"절대 좌표 ({abs_x}, {abs_y})는 어떤 모니터에도 속하지 않습니다.") 