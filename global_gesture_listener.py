import tkinter as tk
import pyautogui
import time
from pynput import keyboard, mouse

class GlobalGestureListener:
    def __init__(self):
        # 상태 플래그
        self.is_running = False
        self.is_recording = False
        
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
        
        # 콜백 함수
        self.on_gesture_started = None
        self.on_gesture_moved = None
        self.on_gesture_ended = None
        
        # 키보드/마우스 리스너
        self.keyboard_listener = None
        self.mouse_listener = None
    
    def set_callbacks(self, started_cb, moved_cb, ended_cb):
        """콜백 함수 설정"""
        self.on_gesture_started = started_cb
        self.on_gesture_moved = moved_cb
        self.on_gesture_ended = ended_cb
        print(f"콜백 설정 완료: {started_cb}, {moved_cb}, {ended_cb}")
    
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
            if self.on_gesture_ended:
                print("제스처 종료 콜백 호출")
                self.on_gesture_ended()
        
        # 키보드/마우스 리스너 중지
        try:
            if self.keyboard_listener:
                self.keyboard_listener.stop()
                
            if self.mouse_listener:
                self.mouse_listener.stop()
                
            print("Global gesture listener stopped successfully")
        except Exception as e:
            print(f"Error stopping listeners: {e}")
    
    def on_key_press(self, key):
        """키보드 키 누름 이벤트 처리"""
        try:
            print(f"키 눌림: {key}")  # 디버깅을 위한 출력
            
            # ESC 키 처리
            if key == keyboard.Key.esc:
                print("ESC 키 눌림 - 제스처 취소")
                # 현재 진행 중인 제스처가 있으면 종료
                if self.is_recording:
                    self.is_recording = False
                    print("제스처 취소됨 (ESC로 인해)")
                    self.reset_modifiers()
                    if self.on_gesture_ended:
                        self.on_gesture_ended()
                return
                
            # 모디파이어 키 확인 및 업데이트
            if key == keyboard.Key.ctrl or key == keyboard.Key.ctrl_l or key == keyboard.Key.ctrl_r:
                self.ctrl_pressed = True
                self._update_modifiers()
                print("Ctrl 키 눌림")
            elif key == keyboard.Key.shift or key == keyboard.Key.shift_l or key == keyboard.Key.shift_r:
                self.shift_pressed = True
                self._update_modifiers()
                print("Shift 키 눌림")
            elif key == keyboard.Key.alt or key == keyboard.Key.alt_l or key == keyboard.Key.alt_r:
                self.alt_pressed = True
                self._update_modifiers()
                print("Alt 키 눌림")
                
            # 모디파이어 키가 하나라도 눌린 상태에서 제스처 시작
            if not self.is_recording and self._any_modifier_pressed():
                self.is_recording = True
                print(f"제스처 시작: ({pyautogui.position()}), 모디파이어: {self.current_modifiers}")
                if self.on_gesture_started:
                    self.on_gesture_started(pyautogui.position(), self.current_modifiers)
                else:
                    print("제스처 시작 콜백이 설정되지 않음")
        except Exception as e:
            print(f"키 누름 처리 오류: {e}")
    
    def on_key_release(self, key):
        """키보드 키 해제 이벤트 처리"""
        try:
            print(f"키 해제: {key}")  # 디버깅을 위한 출력
            
            # ESC 키 처리
            if key == keyboard.Key.esc:
                print("ESC 키 해제")
                return
                
            # 모디파이어 키 확인 및 업데이트
            if key == keyboard.Key.ctrl or key == keyboard.Key.ctrl_l or key == keyboard.Key.ctrl_r:
                self.ctrl_pressed = False
                self._update_modifiers()
                print("Ctrl 키 해제")
            elif key == keyboard.Key.shift or key == keyboard.Key.shift_l or key == keyboard.Key.shift_r:
                self.shift_pressed = False
                self._update_modifiers()
                print("Shift 키 해제")
            elif key == keyboard.Key.alt or key == keyboard.Key.alt_l or key == keyboard.Key.alt_r:
                self.alt_pressed = False
                self._update_modifiers()
                print("Alt 키 해제")
                
            print(f"모디파이어 업데이트: {self.current_modifiers}")
            
            # 모든 모디파이어 키가 해제된 경우 제스처 종료
            if not self._any_modifier_pressed() and self.is_recording:
                self.is_recording = False
                print("제스처 종료 - 모든 모디파이어 키 해제됨")
                if self.on_gesture_ended:
                    self.on_gesture_ended()
                else:
                    print("제스처 종료 콜백이 설정되지 않음")
        except Exception as e:
            print(f"키 해제 처리 오류: {e}")
    
    def on_mouse_move(self, x, y):
        """마우스 이동 이벤트 처리"""
        if not self.is_running or not self.is_recording:
            return
            
        try:
            # 좌표값 간소화 (디버깅 출력 감소를 위해)
            if hasattr(self, 'last_logged_pos'):
                last_x, last_y = self.last_logged_pos
                # 일정 거리 이상 이동했을 때만 로그 출력
                dist_sq = (x - last_x)**2 + (y - last_y)**2
                if dist_sq > 1000:  # 약 30픽셀 이상 이동했을 때
                    print(f"마우스 이동: ({x}, {y})")
                    self.last_logged_pos = (x, y)
            else:
                print(f"마우스 이동: ({x}, {y})")
                self.last_logged_pos = (x, y)
            
            # 제스처 이동 시그널 발생
            if self.on_gesture_moved:
                self.on_gesture_moved((x, y))
            else:
                # 이 메시지는 한 번만 출력 (스팸 방지)
                if not hasattr(self, 'logged_no_move_callback'):
                    print("제스처 이동 콜백이 설정되지 않음")
                    self.logged_no_move_callback = True
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
            
        if prev_modifiers != self.current_modifiers:
            print(f"모디파이어 업데이트: {self.current_modifiers}")
    
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