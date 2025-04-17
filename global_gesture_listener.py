import tkinter as tk
# import pyautogui # 사용하지 않음
import time
# from pynput import keyboard, mouse # pynput.mouse 제거
import mouse # mouse 라이브러리 임포트 유지 (hook 사용 위함)
from pynput import keyboard # pynput.keyboard 는 유지
from pynput.mouse import Listener as PynputMouseListener # Listener 명시적 임포트
from pynput.mouse import Controller as PynputMouseController # Controller도 유지
# from pynput.mouse import Controller as MouseController # 제거
import monitor_utils  # monitor_utils 모듈 임포트
import logging # 로깅 추가
import threading # 사용 안 함 (multiprocessing 사용)
import multiprocessing # 멀티프로세싱 임포트
from multiprocessing import Process, Queue, Event # 필요한 클래스 임포트

# monitor_utils 임포트 순서 조정 (get_monitors() 호출 위함)
import monitor_utils 

# --- 별도 프로세스에서 실행될 함수 ---
def mouse_hook_process_target(queue, stop_event):
    """별도 프로세스에서 마우스 이벤트를 감지하고 큐에 넣는 함수"""
    import mouse # 프로세스 내에서 임포트
    import time
    import logging # 프로세스 내 로깅 설정
    import os # pid 로깅 위해
    
    # 로깅 기본 설정 (프로세스별로 필요할 수 있음)
    log_format = '%(asctime)s - PID:%(process)d - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.DEBUG, format=log_format) # DEBUG 레벨로 변경
    
    logging.info(f"[Mouse Process {os.getpid()}] Starting hook...")
    
    def _minimal_hook_callback(event):
        if isinstance(event, mouse.MoveEvent):
            try:
                # 필수 데이터만 큐에 넣음
                queue.put(('move', event.x, event.y), block=False) 
                # logging.debug(f"[Mouse Process {os.getpid()}] Put event in queue: ({event.x}, {event.y})") # 로그 추가 (너무 많을 수 있음)
            except queue.Full:
                logging.warning(f"[Mouse Process {os.getpid()}] Event queue is full, dropping event.")
            except Exception as e:
                 logging.error(f"[Mouse Process {os.getpid()}] Error in hook callback: {e}", exc_info=True)

    try:
        mouse.hook(_minimal_hook_callback)
        logging.info(f"[Mouse Process {os.getpid()}] Hook installed. Waiting for stop event...")
        
        # stop_event가 설정될 때까지 대기 (wait() 사용으로 복귀)
        stop_event.wait() # 이벤트가 set() 될 때까지 여기서 블록됨
            
        logging.info(f"[Mouse Process {os.getpid()}] Stop event received.")

    except Exception as e:
        logging.error(f"[Mouse Process {os.getpid()}] Error in hook process: {e}", exc_info=True)
    finally:
        logging.info(f"[Mouse Process {os.getpid()}] Unhooking and exiting...")
        mouse.unhook_all()
        logging.info(f"[Mouse Process {os.getpid()}] Exited.")
# --- 별도 프로세스 함수 끝 ---

class GlobalGestureListener:
    def __init__(self, monitors):
        # self.root = root # 제거
        # 상태 플래그
        self.is_running = False
        self.is_recording = False
        self.start_monitor = None # 제스처 시작 시점의 모니터 저장
        
        # 현재 눌린 모디파이어 키 추적
        self.current_modifiers = 0  # tkinter에서는 Qt 대신 일반 정수 값 사용
        
        # 모디파이어 값 정의 (Qt 대신 자체 정의)
        self.CTRL_MODIFIER = 1
        self.SHIFT_MODIFIER = 2
        self.ALT_MODIFIER = 4
        
        # 모디파이어 키가 눌렸는지 상태
        self.ctrl_pressed = False
        self.shift_pressed = False
        self.alt_pressed = False
        
        # 콜백 함수 (시그니처 변경됨)
        self.on_gesture_started = None # (rel_pos, monitor, modifiers)
        self.on_gesture_moved = None   # (rel_pos, monitor)
        self.on_gesture_ended = None   # ()
        
        # 키보드 리스너
        self.keyboard_listener = None
        self.mouse_listener = None # pynput 리스너 참조
        self.keyboard_listener_running = False # 키보드 리스너 실행 상태 플래그 추가
        
        # --- 스로틀링 관련 속성 추가 ---
        self.last_move_time = 0
        self.min_move_interval = 0.015 # 초 단위 (15ms)
        
        # --- 모니터 정보 (생성 시 주입) ---
        self._cached_monitors = monitors if monitors is not None else []
        if monitors is not None:
            logging.info(f"Received and cached {len(self._cached_monitors)} monitors.")
        else:
             logging.warning("Received None for monitors, caching empty list.")
        # --- 캐싱 끝 ---
        
        # --- 멀티프로세싱 관련 속성 --- 
        self.mouse_event_queue = None # Queue()는 프로세스 시작 시 생성
        self.mouse_process = None
        self.stop_mouse_process_event = None # Event()는 프로세스 시작 시 생성
        self.queue_check_id = None
        self.QUEUE_POLL_INTERVAL = 10 # ms 단위 (큐 확인 간격)
        # --- 속성 끝 ---

    def set_callbacks(self, started_cb, moved_cb, ended_cb):
        """콜백 함수 설정 (변경된 시그니처에 맞춰 사용해야 함)"""
        self.on_gesture_started = started_cb
        self.on_gesture_moved = moved_cb
        self.on_gesture_ended = ended_cb
        print(f"콜백 설정 완료 (변경된 시그니처): {started_cb}, {moved_cb}, {ended_cb}")
    
    def start(self):
        """글로벌 제스처 리스너 시작"""
        if self.is_running:
            print("이미 실행 중")
            return
            
        self.is_running = True
        print("제스처 리스너 시작 (키보드 리스너만)")
        
        try:
            # 키보드 리스너 설정 및 시작 -> 시작은 별도 메소드로 분리
            # self.keyboard_listener = keyboard.Listener(...)
            # self.keyboard_listener.start()
            # print("Keyboard listener started successfully (using pynput)")
            pass # start()에서는 아무것도 하지 않음

        except Exception as e:
            # print(f"Error starting keyboard listener: {e}") # 오류 메시지 수정 불필요
            print(f"Error in GlobalGestureListener start (should be empty): {e}")
            self.is_running = False
    
    def stop(self):
        """글로벌 제스처 리스너 중지 (프로세스 종료 포함)"""
        if not self.is_running:
            logging.debug("GlobalGestureListener already stopped") 
            return
            
        self.is_running = False
        logging.info("Stopping GlobalGestureListener...") 
        
        # 진행 중인 제스처 종료 (내부에서 _stop_mouse_process 호출)
        if self.is_recording:
            self.is_recording = False
            self.start_monitor = None 
            self._stop_mouse_listener_if_active() # pynput 마우스 리스너 중지
            if self.on_gesture_ended:
                logging.debug("Calling on_gesture_ended callback due to listener stop") 
                self.on_gesture_ended()
        
        # 키보드 리스너 중지
        self.stop_keyboard_listener() 

        # --- 마우스 프로세스 확실히 중지 --- 
        self._stop_mouse_listener_if_active() # stop() 에서도 확실히 중지
        # --- 중지 끝 ---

        logging.info("Global gesture listener stopped successfully") 

    def on_key_press(self, key):
        """키보드 키 누름 이벤트 처리 (pynput 리스너 시작 로직)"""
        try:
            # ESC 키 처리
            if key == keyboard.Key.esc:
                logging.info("ESC key pressed - Cancelling gesture") 
                if self.is_recording:
                    self.is_recording = False
                    self._stop_mouse_listener_if_active() # 마우스 리스너 중지
                    self.start_monitor = None
                    logging.info("Gesture cancelled (ESC).") 
                    self.reset_modifiers()
                    if self.on_gesture_ended:
                        self.on_gesture_ended()
                return
                
            # 모디파이어 키 확인
            modifier_pressed = False
            is_first_modifier_press = False 
            if key == keyboard.Key.ctrl or key == keyboard.Key.ctrl_l or key == keyboard.Key.ctrl_r:
                if not self.ctrl_pressed: 
                    modifier_pressed = True
                    if not self._any_modifier_pressed(): is_first_modifier_press = True
                self.ctrl_pressed = True
            elif key == keyboard.Key.shift or key == keyboard.Key.shift_l or key == keyboard.Key.shift_r:
                if not self.shift_pressed: 
                    modifier_pressed = True
                    if not self._any_modifier_pressed(): is_first_modifier_press = True
                self.shift_pressed = True
            elif key == keyboard.Key.alt or key == keyboard.Key.alt_l or key == keyboard.Key.alt_gr or key == keyboard.Key.alt_r:
                if not self.alt_pressed: 
                    modifier_pressed = True
                    if not self._any_modifier_pressed(): is_first_modifier_press = True
                self.alt_pressed = True

            if modifier_pressed:
                self._update_modifiers()
                
                # 첫 모디파이어 & 비녹화 -> 제스처 시작 & pynput 마우스 리스너 시작
                if is_first_modifier_press and not self.is_recording:
                    try:
                        # 명시적으로 임포트한 컨트롤러 사용
                        with PynputMouseController() as mc:
                             abs_x, abs_y = mc.position
                    except Exception as e_pos:
                         logging.error(f"Error getting mouse position: {e_pos}", exc_info=True)
                         return 
                    
                    current_monitor = self._get_monitor_from_point_cached(abs_x, abs_y) # 캐싱 사용

                    if current_monitor:
                        self.is_recording = True 
                        self.start_monitor = current_monitor 
                        rel_x, rel_y = monitor_utils.absolute_to_relative(abs_x, abs_y, current_monitor)
                        logging.info(f"Gesture started: Monitor {self._cached_monitors.index(current_monitor)} Rel({rel_x}, {rel_y}) ...")
                        
                        # --- pynput 마우스 리스너 시작 ---
                        self._start_mouse_listener_if_inactive()
                        # --- 시작 끝 ---

                        if self.on_gesture_started:
                            self.on_gesture_started((rel_x, rel_y), current_monitor, self.current_modifiers)
                    else:
                        logging.warning(f"Mouse ({abs_x}, {abs_y}) outside monitors.")
                        self.reset_modifiers()
        except Exception as e:
            logging.error(f"Error in on_key_press: {e}", exc_info=True)
    
    def on_key_release(self, key):
        """키보드 키 해제 이벤트 처리 (pynput 리스너 종료 로직)"""
        try:
            if key == keyboard.Key.esc:
                return
            modifier_released = False
            was_recording = self.is_recording 
            if key == keyboard.Key.ctrl or key == keyboard.Key.ctrl_l or key == keyboard.Key.ctrl_r:
                if self.ctrl_pressed: modifier_released = True
                self.ctrl_pressed = False
            elif key == keyboard.Key.shift or key == keyboard.Key.shift_l or key == keyboard.Key.shift_r:
                if self.shift_pressed: modifier_released = True
                self.shift_pressed = False
            elif key == keyboard.Key.alt or key == keyboard.Key.alt_l or key == keyboard.Key.alt_gr or key == keyboard.Key.alt_r:
                if self.alt_pressed: modifier_released = True
                self.alt_pressed = False

            if modifier_released:
                self._update_modifiers()
                if not self._any_modifier_pressed() and was_recording: 
                    self.is_recording = False
                    self.start_monitor = None 
                    logging.info("Gesture ended - All modifiers released.")
                    # --- pynput 마우스 리스너 종료 ---
                    self._stop_mouse_listener_if_active()
                    # --- 종료 끝 ---
                    if self.on_gesture_ended:
                        self.on_gesture_ended()
        except Exception as e:
            logging.error(f"Error in on_key_release: {e}", exc_info=True)
    
    def _start_mouse_listener_if_inactive(self):
        """pynput 마우스 리스너가 비활성 상태이면 시작 (Listener 명시적 사용)"""
        if self.mouse_listener is None or not self.mouse_listener.is_alive():
            try:
                logging.debug("Starting pynput mouse listener...")
                # 명시적으로 임포트한 리스너 사용
                self.mouse_listener = PynputMouseListener(
                    on_move=self.on_mouse_move,
                    on_click=None, # 클릭/스크롤 무시
                    on_scroll=None
                )
                self.mouse_listener.start()
                logging.debug("pynput mouse listener started.")
            except Exception as e:
                logging.error(f"Error starting pynput mouse listener: {e}", exc_info=True)
                self.mouse_listener = None

    def _stop_mouse_listener_if_active(self):
        """pynput 마우스 리스너가 활성 상태이면 중지"""
        if self.mouse_listener and self.mouse_listener.is_alive():
            try:
                logging.debug("Stopping pynput mouse listener...")
                self.mouse_listener.stop()
                # self.mouse_listener.join() # Join 은 리스너 스레드 자체에서 호출하면 데드락 발생 가능성
                logging.debug("pynput mouse listener stop requested.")
            except Exception as e:
                 logging.error(f"Error stopping pynput mouse listener: {e}", exc_info=True)
            finally:
                 self.mouse_listener = None # 참조 제거 중요

    def _get_monitor_from_point_cached(self, x, y):
        """캐싱된 모니터 정보(_cached_monitors)를 사용하여 좌표가 속한 모니터를 찾습니다."""
        # --- 지연 로딩 로직 제거됨 ---
        # if self._cached_monitors is None:
        #     ...
        
        for m in self._cached_monitors:
            if m.x <= x < m.x + m.width and m.y <= y < m.y + m.height:
                return m
        return None

    def _update_modifiers(self):
        """현재 모디파이어 상태 업데이트"""
        prev_modifiers = self.current_modifiers
        self.current_modifiers = 0
        
        if self.ctrl_pressed:
            self.current_modifiers |= self.CTRL_MODIFIER
            
        if self.shift_pressed:
            self.current_modifiers |= self.SHIFT_MODIFIER
            
        if self.alt_pressed:
            self.current_modifiers |= self.ALT_MODIFIER
            
        if prev_modifiers != self.current_modifiers:
            logging.debug(f"Modifiers updated: {self.current_modifiers}")
    
    def _any_modifier_pressed(self):
        """현재 모디파이어 키가 눌려있는지 확인"""
        return self.ctrl_pressed or self.shift_pressed or self.alt_pressed 

    def reset_modifiers(self):
        """모디파이어 상태 초기화"""
        self.current_modifiers = 0
        self.ctrl_pressed = False
        self.shift_pressed = False
        self.alt_pressed = False
        logging.debug("Modifiers reset")

    # --- 키보드 리스너 시작/중지 메소드 추가 ---
    def start_keyboard_listener(self):
        if self.keyboard_listener_running:
            logging.info("Keyboard listener already running.")
            return True
        if not self.is_running:
             logging.warning("Cannot start keyboard listener, GlobalGestureListener is not running.")
             return False

        try:
            logging.info("Starting keyboard listener...")
            self.keyboard_listener = keyboard.Listener(
                on_press=self.on_key_press,
                on_release=self.on_key_release,
                suppress=False
            )
            self.keyboard_listener.start()
            self.keyboard_listener_running = True
            logging.info("Keyboard listener started successfully.")
            return True
        except Exception as e:
            logging.error(f"Error starting keyboard listener: {e}", exc_info=True)
            self.keyboard_listener_running = False
            return False

    def stop_keyboard_listener(self):
        if not self.keyboard_listener_running or not self.keyboard_listener:
            logging.info("Keyboard listener is not running or already stopped.")
            return True
        
        try:
            logging.info("Stopping keyboard listener...")
            self.keyboard_listener.stop()
            # self.keyboard_listener.join() # stop() 에서 join 보장 여부 확인 필요, 데드락 가능성
            logging.info("Keyboard listener stop requested.")
            self.keyboard_listener_running = False
            self.keyboard_listener = None # 참조 제거
            return True
        except Exception as e:
             logging.error(f"Error stopping keyboard listener: {e}", exc_info=True)
             self.keyboard_listener_running = False
             self.keyboard_listener = None 
             return False 
    # --- 메소드 추가 끝 --- 

    def on_mouse_move(self, x, y, injected=None):
        """pynput 마우스 이동 콜백 (스로틀링 + 캐싱 적용)"""
        # injected 인자는 사용하지 않음
        current_time = time.time()
        # 스로틀링
        if current_time - self.last_move_time < self.min_move_interval:
            return 
        self.last_move_time = current_time 
        # logging.debug(f"Throttled pynput move to: ({x}, {y})")

        # 캐싱 사용 및 처리 로직
        if not self.is_running or not self.is_recording or not self.start_monitor:
            return
        try:
            current_monitor = self._get_monitor_from_point_cached(x, y) 
            if current_monitor == self.start_monitor:
                rel_x, rel_y = monitor_utils.absolute_to_relative(x, y, current_monitor) 
                if self.on_gesture_moved:
                    self.on_gesture_moved((rel_x, rel_y), current_monitor) 
        except Exception as e:
            logging.error(f"Error processing throttled pynput move: {e}", exc_info=True)