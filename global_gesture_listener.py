import tkinter as tk
import pyautogui
import time
from pynput import keyboard, mouse
import monitor_utils  # monitor_utils 모듈 임포트

class GlobalGestureListener:
    def __init__(self):
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
        
        # 키보드/마우스 리스너
        self.keyboard_listener = None
        self.mouse_listener = None
    
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
        print("제스처 리스너 시작")
        
        try:
            # 키보드 리스너 설정
            self.keyboard_listener = keyboard.Listener(
                on_press=self.on_key_press,
                on_release=self.on_key_release
            )
            
            # 마우스 리스너 설정 - 이벤트 필터링 없이 모든 마우스 이벤트 수신
            self.mouse_listener = mouse.Listener(
                on_move=self.on_mouse_move,
                on_click=lambda x, y, button, pressed: None,  # 클릭 이벤트 무시
                on_scroll=lambda x, y, dx, dy: None  # 스크롤 이벤트 무시
            )
            
            # 리스너 시작
            self.keyboard_listener.start()
            self.mouse_listener.start()
            
            print("Global gesture listener started successfully")
        except Exception as e:
            print(f"Error starting listeners: {e}")
            self.is_running = False
    
    def stop(self):
        """글로벌 제스처 리스너 중지"""
        if not self.is_running:
            print("이미 중지됨")
            return
            
        self.is_running = False
        print("제스처 리스너 중지 중")
        
        # 진행 중인 제스처 종료
        if self.is_recording:
            self.is_recording = False
            self.start_monitor = None # 시작 모니터 초기화
            if self.on_gesture_ended:
                print("제스처 종료 콜백 호출")
                self.on_gesture_ended()
        
        # 키보드/마우스 리스너 중지
        try:
            if self.keyboard_listener:
                self.keyboard_listener.stop()
                # 키보드 리스너 스레드가 종료될 때까지 대기
                self.keyboard_listener.join()
                print("Keyboard listener stopped and joined.")
                
            if self.mouse_listener:
                self.mouse_listener.stop()
                # 마우스 리스너 스레드가 종료될 때까지 대기
                self.mouse_listener.join()
                print("Mouse listener stopped and joined.")
                
            print("Global gesture listener stopped successfully")
        except Exception as e:
            print(f"Error stopping listeners: {e}")
    
    def on_key_press(self, key):
        """키보드 키 누름 이벤트 처리"""
        try:
            # print(f"키 눌림: {key}") # 디버깅 출력 줄임
            
            # ESC 키 처리
            if key == keyboard.Key.esc:
                print("ESC 키 눌림 - 제스처 취소")
                if self.is_recording:
                    self.is_recording = False
                    self.start_monitor = None # 시작 모니터 초기화
                    print("제스처 취소됨 (ESC로 인해)")
                    self.reset_modifiers()
                    if self.on_gesture_ended:
                        self.on_gesture_ended()
                return
                
            # 모디파이어 키 확인 및 업데이트
            modifier_pressed = False
            if key == keyboard.Key.ctrl or key == keyboard.Key.ctrl_l or key == keyboard.Key.ctrl_r:
                if not self.ctrl_pressed: modifier_pressed = True
                self.ctrl_pressed = True
                print("Ctrl 키 눌림")
            elif key == keyboard.Key.shift or key == keyboard.Key.shift_l or key == keyboard.Key.shift_r:
                if not self.shift_pressed: modifier_pressed = True
                self.shift_pressed = True
                print("Shift 키 눌림")
            elif key == keyboard.Key.alt or key == keyboard.Key.alt_l or key == keyboard.Key.alt_r:
                if not self.alt_pressed: modifier_pressed = True
                self.alt_pressed = True
                print("Alt 키 눌림")
                
            if modifier_pressed:
                self._update_modifiers()
                
                # 모디파이어 키가 처음 눌렸고, 아직 제스처 기록 중이 아닐 때 제스처 시작
                if not self.is_recording:
                    abs_x, abs_y = pyautogui.position()
                    current_monitor = monitor_utils.get_monitor_from_point(abs_x, abs_y)

                    if current_monitor:
                        self.is_recording = True
                        self.start_monitor = current_monitor # 시작 모니터 저장
                        rel_x, rel_y = monitor_utils.absolute_to_relative(abs_x, abs_y, current_monitor)
                        print(f"제스처 시작: 모니터 {monitor_utils.get_monitors().index(current_monitor)} 상대좌표 ({rel_x}, {rel_y}), 절대좌표 ({abs_x}, {abs_y}), 모디파이어: {self.current_modifiers}")
                        if self.on_gesture_started:
                            self.on_gesture_started((rel_x, rel_y), current_monitor, self.current_modifiers)
                        else:
                            print("제스처 시작 콜백이 설정되지 않음")
                    else:
                        print(f"마우스 ({abs_x}, {abs_y})가 인식된 모니터 외부에 있어 제스처를 시작할 수 없습니다.")
        except Exception as e:
            print(f"키 누름 처리 오류: {e}")
    
    def on_key_release(self, key):
        """키보드 키 해제 이벤트 처리"""
        try:
            # print(f"키 해제: {key}") # 디버깅 출력 줄임
            
            # ESC 키 처리
            if key == keyboard.Key.esc:
                print("ESC 키 해제")
                return
                
            # 모디파이어 키 확인 및 업데이트
            modifier_released = False
            if key == keyboard.Key.ctrl or key == keyboard.Key.ctrl_l or key == keyboard.Key.ctrl_r:
                self.ctrl_pressed = False
                modifier_released = True
                print("Ctrl 키 해제")
            elif key == keyboard.Key.shift or key == keyboard.Key.shift_l or key == keyboard.Key.shift_r:
                self.shift_pressed = False
                modifier_released = True
                print("Shift 키 해제")
            elif key == keyboard.Key.alt or key == keyboard.Key.alt_l or key == keyboard.Key.alt_r:
                self.alt_pressed = False
                modifier_released = True
                print("Alt 키 해제")
                
            if modifier_released:
                self._update_modifiers()
                # print(f"모디파이어 업데이트: {self.current_modifiers}") # 디버깅 출력 줄임
                
                # 모든 모디파이어 키가 해제된 경우 제스처 종료
                if not self._any_modifier_pressed() and self.is_recording:
                    self.is_recording = False
                    self.start_monitor = None # 시작 모니터 초기화
                    print("제스처 종료 - 모든 모디파이어 키 해제됨")
                    if self.on_gesture_ended:
                        self.on_gesture_ended()
                    else:
                        print("제스처 종료 콜백이 설정되지 않음")
        except Exception as e:
            print(f"키 해제 처리 오류: {e}")
    
    def on_mouse_move(self, x, y):
        """마우스 이동 이벤트 처리"""
        if not self.is_running or not self.is_recording or not self.start_monitor:
            return
            
        try:
            # 현재 마우스 위치가 속한 모니터 확인
            current_monitor = monitor_utils.get_monitor_from_point(x, y)

            # 제스처가 시작된 모니터와 동일한 모니터 내에서만 이동 처리
            if current_monitor == self.start_monitor:
                rel_x, rel_y = monitor_utils.absolute_to_relative(x, y, current_monitor)

                # 제스처 이동 콜백 호출 (상대 좌표와 모니터 객체 전달)
                if self.on_gesture_moved:
                    self.on_gesture_moved((rel_x, rel_y), current_monitor)
                else:
                    # 이 메시지는 한 번만 출력 (스팸 방지)
                    if not hasattr(self, 'logged_no_move_callback'):
                        print("제스처 이동 콜백이 설정되지 않음")
                        self.logged_no_move_callback = True
            # else:
                # print(f"마우스가 다른 모니터로 이동 ({x}, {y}). 제스처는 시작 모니터({self.start_monitor.name})에서만 유효합니다.") # 디버깅용

        except Exception as e:
            print(f"Error on mouse move: {e}")
    
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
            
        # if prev_modifiers != self.current_modifiers: # 상태 변경 시에만 출력
            # print(f"모디파이어 업데이트: {self.current_modifiers}") # 디버깅 출력 줄임
    
    def _any_modifier_pressed(self):
        """현재 모디파이어 키가 눌려있는지 확인"""
        return self.ctrl_pressed or self.shift_pressed or self.alt_pressed 

    def reset_modifiers(self):
        """모디파이어 상태 초기화"""
        self.current_modifiers = 0
        self.ctrl_pressed = False
        self.shift_pressed = False
        self.alt_pressed = False
        print("모디파이어 상태 초기화됨") 