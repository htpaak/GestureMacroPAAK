# minimal_hook_test.py (예시)
import mouse
import time
import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(message)s')

def handle_mouse_event(event):
    if isinstance(event, mouse.MoveEvent):
        # 아무 계산도 하지 않고 로그만 남김 (또는 pass)
        logging.debug(f"Mouse Move: ({event.x}, {event.y})")
        pass

logging.info("Starting minimal mouse hook test...")
mouse.hook(handle_mouse_event)

try:
    # 테스트를 위해 일정 시간 실행 (예: 5분)
    # 실제로는 사용자가 직접 Ctrl+C 로 종료
    logging.info("Mouse hook active. Press Ctrl+C to stop.")
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    logging.info("Stopping hook...")
    mouse.unhook_all()
    logging.info("Hook stopped. Exiting.")
