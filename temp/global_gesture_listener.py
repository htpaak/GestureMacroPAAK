from PyQt5.QtCore import QObject, pyqtSignal, QThread, Qt
import pyautogui
import pythoncom
import time
import win32api
import win32con
import win32gui
from pynput import keyboard, mouse

class GlobalGestureListener(QObject):
    # 제스처 이벤트 시그널
    gesture_started = pyqtSignal(object, object)  # point, modifiers
    gesture_moved = pyqtSignal(object)  # point
    gesture_ended = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        
        # 상태 플래그
        self.is_running = False
        self.is_recording = False
        
        # 현재 눌린 모디파이어 키 추적
        self.current_modifiers = Qt.NoModifier
        self.modifiers_map = {
            'Key.ctrl': Qt.ControlModifier,
            'Key.shift': Qt.ShiftModifier,
            'Key.alt': Qt.AltModifier
        }
        
        # 모디파이어 키가 눌렸는지 상태
        self.ctrl_pressed = False
        self.shift_pressed = False
        self.alt_pressed = False
        
        # 리스너 스레드
        self.listener_thread = None
        
        # 키보드/마우스 리스너
        self.keyboard_listener = None
        self.mouse_listener = None
    
    def start(self):
        """글로벌 제스처 리스너 시작"""
        if self.is_running:
            return
            
        self.is_running = True
        
        # 키보드 리스너 설정
        self.keyboard_listener = keyboard.Listener(
            on_press=self.on_key_press,
            on_release=self.on_key_release
        )
        
        # 마우스 리스너 설정
        self.mouse_listener = mouse.Listener(
            on_move=self.on_mouse_move
        )
        
        # 리스너 시작
        self.keyboard_listener.start()
        self.mouse_listener.start()
        
        print("Global gesture listener started")
    
    def stop(self):
        """글로벌 제스처 리스너 중지"""
        if not self.is_running:
            return
            
        self.is_running = False
        
        # 진행 중인 제스처 종료
        if self.is_recording:
            self.is_recording = False
            self.gesture_ended.emit()
        
        # 키보드/마우스 리스너 중지
        if self.keyboard_listener:
            self.keyboard_listener.stop()
            
        if self.mouse_listener:
            self.mouse_listener.stop()
            
        print("Global gesture listener stopped")
    
    def on_key_press(self, key):
        """키 눌림 이벤트 처리"""
        if not self.is_running:
            return
            
        try:
            # 키 이름 가져오기
            key_name = str(key)
            
            # 모디파이어 키 체크
            if key_name == 'Key.ctrl':
                self.ctrl_pressed = True
                self._update_modifiers()
            elif key_name == 'Key.shift':
                self.shift_pressed = True
                self._update_modifiers()
            elif key_name == 'Key.alt':
                self.alt_pressed = True
                self._update_modifiers()
                
            # 모디파이어 키가 눌려있고 제스처가 시작되지 않았으면 시작
            if self._any_modifier_pressed() and not self.is_recording:
                # 현재 마우스 위치
                x, y = pyautogui.position()
                
                # 제스처 시작 시그널 발생
                self.is_recording = True
                self.gesture_started.emit((x, y), self.current_modifiers)
        except Exception as e:
            print(f"Error on key press: {e}")
    
    def on_key_release(self, key):
        """키 해제 이벤트 처리"""
        if not self.is_running:
            return
            
        try:
            # 키 이름 가져오기
            key_name = str(key)
            
            # 모디파이어 키 체크
            if key_name == 'Key.ctrl':
                self.ctrl_pressed = False
                self._update_modifiers()
            elif key_name == 'Key.shift':
                self.shift_pressed = False
                self._update_modifiers()
            elif key_name == 'Key.alt':
                self.alt_pressed = False
                self._update_modifiers()
                
            # 모든 모디파이어 키가 떼어지면 제스처 종료
            if not self._any_modifier_pressed() and self.is_recording:
                self.is_recording = False
                self.gesture_ended.emit()
        except Exception as e:
            print(f"Error on key release: {e}")
    
    def on_mouse_move(self, x, y):
        """마우스 이동 이벤트 처리"""
        if not self.is_running or not self.is_recording:
            return
            
        try:
            # 제스처 이동 시그널 발생
            self.gesture_moved.emit((x, y))
        except Exception as e:
            print(f"Error on mouse move: {e}")
    
    def _update_modifiers(self):
        """현재 모디파이어 상태 업데이트"""
        self.current_modifiers = Qt.NoModifier
        
        if self.ctrl_pressed:
            self.current_modifiers |= Qt.ControlModifier
            
        if self.shift_pressed:
            self.current_modifiers |= Qt.ShiftModifier
            
        if self.alt_pressed:
            self.current_modifiers |= Qt.AltModifier
    
    def _any_modifier_pressed(self):
        """현재 모디파이어 키가 눌려있는지 확인"""
        return self.ctrl_pressed or self.shift_pressed or self.alt_pressed 