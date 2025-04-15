import keyboard
import mouse
import time
from datetime import datetime

class MacroRecorder:
    def __init__(self, parent=None):
        self.recording = False
        self.events = []
        self.start_time = 0
        self.last_event_time = 0
        
        # 부모 객체 참조 저장 (GUI 등)
        self.parent = parent
        
        # 녹화 설정
        self.record_mouse_move = False
        self.use_relative_coords = False
        self.record_keyboard = True
        self.record_delay = True  # 딜레이 녹화 설정 기본값을 True로 변경
        
        # 좌표 기준점 (상대좌표 사용 시)
        self.base_x = 0
        self.base_y = 0
        
        # 딜레이 자동 생성을 위한 최소 시간 (초)
        self.min_delay_time = 0.01
        
        # 현재 눌려있는 키를 추적하기 위한 딕셔너리 추가
        self.pressed_keys = {}
    
    def start_recording(self):
        """매크로 녹화 시작"""
        if not self.recording:
            self.recording = True
            self.events = []
            self.start_time = time.time()
            self.last_event_time = 0  # 첫 이벤트를 위해 0으로 초기화
            
            # 눌려있는 키 초기화
            self.pressed_keys = {}
            
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
                print(f"Relative coordinate base set to: ({self.base_x}, {self.base_y})")
            else:
                self.base_x, self.base_y = 0, 0 # 절대 좌표 모드 시 초기화
            
            # 녹화 설정 정보 출력
            settings = []
            if self.record_delay:
                settings.append("딜레이")
            if self.record_mouse_move:
                settings.append("마우스 이동")
            if self.record_keyboard:
                settings.append("키보드")
                
            settings_str = ", ".join(settings) if settings else "없음"
            print(f"매크로 녹화가 시작되었습니다. 녹화 설정: {settings_str}")
    
    def stop_recording(self):
        """매크로 녹화 중지 및 이벤트 시간 재조정"""
        if self.recording:
            # 특정 콜백만 해제
            try:
                # 키보드 콜백 해제
                if self.record_keyboard: # 녹화 설정에 따라 해제 시도
                    keyboard.unhook(self._keyboard_callback)
                    print("키보드 녹화 콜백 해제")
            except Exception as e:
                print(f"키보드 콜백 해제 오류: {e}")
                try: # 최후의 수단
                    keyboard.unhook_all()
                    print("모든 키보드 훅 해제 (예외 발생)")
                except Exception as e_all:
                    print(f"모든 키보드 훅 해제 오류: {e_all}")

            # 마우스 훅 해제
            try:
                mouse.unhook_all()
                print("마우스 녹화 콜백 해제")
            except Exception as e:
                print(f"마우스 콜백 해제 오류: {e}")

            # 상태 업데이트
            self.recording = False
            print("매크로 녹화가 중지되었습니다.")

            # --- 이벤트 시간 재조정 로직 추가 ---
            if self.events:
                # 첫 이벤트 시간 가져오기
                first_event_time = self.events[0]['time']
                print(f"첫 이벤트 시간(조정 전): {first_event_time:.3f}s")

                # 모든 이벤트 시간에서 첫 이벤트 시간 빼기
                if first_event_time > 0: # 첫 이벤트 시간이 0보다 클 때만 조정
                    for event in self.events:
                        event['time'] -= first_event_time
                        # 혹시 모를 음수 시간 방지 (거의 발생 안 함)
                        if event['time'] < 0:
                             event['time'] = 0
                    print("모든 이벤트 시간 재조정 완료 (첫 이벤트 기준 0초 시작)")

                # 조정된 첫 이벤트 시간 확인 (디버깅용)
                if self.events:
                    print(f"조정된 첫 이벤트 시간: {self.events[0]['time']:.3f}s")
            else:
                 print("녹화된 이벤트가 없어 시간 재조정을 건너니다.")
            # --- 로직 추가 끝 ---

            # 녹화 중지 후 단축키 다시 설정 (기존 로직 유지)
            if hasattr(self, 'parent') and hasattr(self.parent, 'setup_keyboard_shortcuts'):
                try:
                    self.parent.setup_keyboard_shortcuts()
                    print("녹화 중지 후 단축키 재설정 시도")
                except Exception as e:
                    print(f"단축키 재설정 오류: {e}")

            # 최종 이벤트 목록 반환
            return self.events
        return None
    
    def _add_delay_event_if_needed(self, current_time):
        """필요한 경우 딜레이 이벤트 추가"""
        # record_delay가 False이면 딜레이 이벤트를 추가하지 않음
        if not self.record_delay:
            self.last_event_time = current_time
            return
            
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
            # F9와 F10 키는 무시 (단축키로 사용되기 때문에 녹화되지 않아야 함)
            if event.name in ['f9', 'f10']:
                print(f"{event.name} 키는 단축키로 사용되므로 녹화하지 않음")
                return
                
            current_time = time.time() - self.start_time
            
            # 키다운 이벤트 처리
            if event.event_type == 'down':
                # 이미 누른 상태로 기록된 키는 중복 키다운 이벤트를 무시
                if event.name in self.pressed_keys:
                    print(f"{event.name} 키가 이미 눌려있음 - 중복 키다운 무시")
                    return
                
                # 딜레이 체크 및 필요 시 딜레이 이벤트 추가
                self._add_delay_event_if_needed(current_time)
                
                # 키가 눌린 시간 기록
                self.pressed_keys[event.name] = current_time
                print(f"{event.name} 키다운 이벤트 기록 (첫 입력)")
                
                # 키다운 이벤트 추가
                event_data = {
                    'type': 'keyboard',
                    'event_type': 'down',
                    'key': event.name,
                    'time': current_time
                }
                self.events.append(event_data)
            
            # 키업 이벤트 처리
            elif event.event_type == 'up':
                # 해당 키가 눌려있는 상태로 기록되어 있는지 확인
                if event.name in self.pressed_keys:
                    press_time = self.pressed_keys[event.name]
                    key_hold_duration = current_time - press_time
                    
                    print(f"{event.name} 키업 이벤트 기록 (키 홀드 시간: {key_hold_duration:.3f}초)")
                    
                    # 키 홀드 시간만큼의 딜레이 추가 (키 홀드 효과)
                    delay_event = {
                        'type': 'delay',
                        'time': current_time - 0.001,  # 약간 시간을 당겨서 순서 보장
                        'delay': key_hold_duration
                    }
                    self.events.append(delay_event)
                    print(f"키 홀드 딜레이 추가: {int(key_hold_duration * 1000)}ms")
                    
                    # 키업 이벤트 추가
                    event_data = {
                        'type': 'keyboard',
                        'event_type': 'up',
                        'key': event.name,
                        'time': current_time
                    }
                    self.events.append(event_data)
                    
                    # 마지막 이벤트 시간 업데이트 (이 다음 이벤트부터는 딜레이가 측정되도록)
                    self.last_event_time = current_time
                    
                    # 눌려있는 키 목록에서 제거
                    del self.pressed_keys[event.name]
                else:
                    # 키다운 없이 키업만 감지된 경우 (예: 녹화 시작 전에 키를 누른 상태)
                    print(f"{event.name} 키업 이벤트 기록 (키다운 없이 감지됨)")
                    
                    # 딜레이 체크 및 필요 시 딜레이 이벤트 추가
                    self._add_delay_event_if_needed(current_time)
                    
                    # 키업 이벤트만 추가
                    event_data = {
                        'type': 'keyboard',
                        'event_type': 'up',
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