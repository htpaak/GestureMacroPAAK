import keyboard
import mouse
import time
from datetime import datetime

class MacroRecorder:
    def __init__(self):
        self.recording = False
        self.events = []
        self.start_time = 0
        self.last_event_time = 0
        
        # 녹화 설정
        self.record_mouse_move = False
        self.use_relative_coords = False
        self.record_keyboard = True
        
        # 좌표 기준점 (상대좌표 사용 시)
        self.base_x = 0
        self.base_y = 0
        
        # 딜레이 자동 생성을 위한 최소 시간 (초)
        self.min_delay_time = 0.01
    
    def start_recording(self):
        """매크로 녹화 시작"""
        if not self.recording:
            self.recording = True
            self.events = []
            self.start_time = time.time()
            self.last_event_time = 0  # 첫 이벤트를 위해 0으로 초기화
            
            # 키보드 이벤트 후크
            if self.record_keyboard:
                keyboard.hook(self._keyboard_callback)
                
            # 마우스 이벤트 후크 (모든 마우스 이벤트를 후크하고 콜백 함수에서 필터링)
            # 이렇게 하지 않으면 녹화 중에 마우스 이동 설정을 변경할 수 없음
            mouse.hook(self._mouse_callback)
            
            # 상대좌표 사용 시 시작 위치 기록
            if self.use_relative_coords:
                pos = mouse.get_position()
                self.base_x, self.base_y = pos
            
            print(f"매크로 녹화가 시작되었습니다. 마우스 이동 녹화: {'켜짐' if self.record_mouse_move else '꺼짐'}")
    
    def stop_recording(self):
        """매크로 녹화 중지"""
        if self.recording:
            # 후크 해제
            keyboard.unhook_all()
            mouse.unhook_all()
            
            self.recording = False
            print("매크로 녹화가 중지되었습니다.")
            return self.events
        return None
    
    def _add_delay_event_if_needed(self, current_time):
        """필요한 경우 딜레이 이벤트 추가"""
        elapsed = current_time - self.last_event_time
        
        # 지정된 최소 시간보다 대기 시간이 길면 딜레이 이벤트 추가
        if elapsed >= self.min_delay_time and self.last_event_time > 0:
            delay_event = {
                'type': 'delay',
                'time': current_time - 0.001,  # 약간 시간을 당겨서 순서 보장
                'delay': elapsed
            }
            self.events.append(delay_event)
            # 초 단위를 밀리초 단위로 변환하여 출력
            elapsed_ms = int(elapsed * 1000)
            print(f"딜레이 감지: {elapsed_ms}ms")
        
        # 마지막 이벤트 시간 업데이트
        self.last_event_time = current_time
    
    def _keyboard_callback(self, event):
        """키보드 이벤트 콜백"""
        if self.recording and self.record_keyboard:
            current_time = time.time() - self.start_time
            
            # 딜레이 체크 및 필요 시 딜레이 이벤트 추가
            self._add_delay_event_if_needed(current_time)
            
            event_data = {
                'type': 'keyboard',
                'event_type': event.event_type,  # 'down' or 'up'
                'key': event.name,
                'time': current_time
            }
            self.events.append(event_data)
    
    def _mouse_callback(self, event):
        """마우스 이벤트 콜백"""
        if not self.recording:
            return
            
        current_time = time.time() - self.start_time
        
        # 이벤트 타입에 따라 다르게 처리
        if isinstance(event, mouse.MoveEvent):
            # 마우스 이동 이벤트는 설정에 따라 필터링
            if not self.record_mouse_move:
                return
            
            # 딜레이 체크 및 필요 시 딜레이 이벤트 추가
            self._add_delay_event_if_needed(current_time)
                
            event_data = {
                'type': 'mouse',
                'event_type': 'move',
                'time': current_time
            }
            
            # 상대좌표 또는 절대좌표
            if self.use_relative_coords:
                rel_x = event.x - self.base_x
                rel_y = event.y - self.base_y
                event_data['position'] = (rel_x, rel_y)
                event_data['is_relative'] = True
            else:
                event_data['position'] = (event.x, event.y)
                event_data['is_relative'] = False
            
            self.events.append(event_data)
                
        elif isinstance(event, mouse.ButtonEvent):
            # 딜레이 체크 및 필요 시 딜레이 이벤트 추가
            self._add_delay_event_if_needed(current_time)
            
            event_data = {
                'type': 'mouse',
                'event_type': event.event_type,  # 'up', 'down', 'double'
                'button': event.button,
                'time': current_time
            }
            
            # 상대좌표 또는 절대좌표
            pos = mouse.get_position()
            if self.use_relative_coords:
                rel_x = pos[0] - self.base_x
                rel_y = pos[1] - self.base_y
                event_data['position'] = (rel_x, rel_y)
                event_data['is_relative'] = True
            else:
                event_data['position'] = pos
                event_data['is_relative'] = False
            
            self.events.append(event_data)
                
        elif isinstance(event, mouse.WheelEvent):
            # 딜레이 체크 및 필요 시 딜레이 이벤트 추가
            self._add_delay_event_if_needed(current_time)
            
            event_data = {
                'type': 'mouse',
                'event_type': 'scroll',
                'delta': event.delta,
                'time': current_time
            }
            
            # 상대좌표 또는 절대좌표
            pos = mouse.get_position()
            if self.use_relative_coords:
                rel_x = pos[0] - self.base_x
                rel_y = pos[1] - self.base_y
                event_data['position'] = (rel_x, rel_y)
                event_data['is_relative'] = True
            else:
                event_data['position'] = pos
                event_data['is_relative'] = False
            
            self.events.append(event_data)
    
    def get_recorded_events(self):
        """녹화된 이벤트 반환"""
        return self.events
        
    def add_delay_event(self, delay_seconds):
        """수동으로 딜레이 이벤트 추가"""
        if self.recording:
            current_time = time.time() - self.start_time
            
            delay_event = {
                'type': 'delay',
                'time': current_time,
                'delay': delay_seconds
            }
            
            self.events.append(delay_event)
            self.last_event_time = current_time
            
            return True
        return False 