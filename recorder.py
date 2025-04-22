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
        self.use_relative_coords = False # <<< 이 속성은 더 이상 사용되지 않음
        self.record_keyboard = True
        self.record_delay = True  # 딜레이 녹화 설정 기본값을 True로 변경
        self.recording_coord_mode = "absolute" # <<< 추가: 현재 녹화 좌표 모드
        self.last_mouse_pos = None # <<< 추가: Mouse Relative 모드용 마지막 위치
        
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
            
            # --- 좌표 모드에 따른 초기 설정 --- 
            current_pos = mouse.get_position()
            if self.recording_coord_mode == 'gesture_relative':
                # 기존 'relative' 모드와 동일하게 동작
                self.base_x, self.base_y = current_pos
                self.last_mouse_pos = None # 사용 안 함
                print(f"Gesture Relative 모드 시작. 기준 좌표: ({self.base_x}, {self.base_y})")
            elif self.recording_coord_mode == 'playback_relative':
                # Mouse Relative 모드: 현재 위치를 마지막 위치로 저장
                self.last_mouse_pos = current_pos
                self.base_x, self.base_y = None, None # 사용 안 함
                print(f"Mouse Relative 모드 시작. 첫 위치: {self.last_mouse_pos}")
            else: # 'absolute' 모드 (기본값)
                self.base_x, self.base_y = None, None # 사용 안 함
                self.last_mouse_pos = None # 사용 안 함
                print("Absolute 모드 시작.")
            # --- 초기 설정 끝 --- 
            
            # 녹화 설정 정보 출력
            settings = [f"좌표모드({self.recording_coord_mode})"] # 좌표 모드 표시 추가
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
        """마우스 이벤트 콜백 함수 (3가지 좌표 모드 지원)"""
        # <<< 디버그 로그 제거 1 >>>
        # print(f"[DEBUG] _mouse_callback called with event: {type(event)}")

        if not self.recording:
            # <<< 디버그 로그 제거 >>>
            # print("[DEBUG] Not recording, ignoring event.")
            return

        current_time = time.time() # 이벤트 발생 시간 기록
        event_time_relative = current_time - self.start_time # 녹화 시작 기준 시간

        event_data = None
        current_pos = None # 현재 위치 저장용
        
        # --- 이벤트 타입별 처리 ---
        if isinstance(event, mouse.ButtonEvent):
            # 버튼/휠 이벤트는 딜레이 체크 먼저
            self._add_delay_event_if_needed(event_time_relative) 
            current_pos = mouse.get_position() # 버튼/휠 이벤트 발생 시 위치 가져오기
            # print(f"Mouse Button: {event.event_type} {event.button} at {current_pos}") # 디버깅

            # 좌표 계산
            position_to_save, coord_mode_to_save = self._calculate_coordinates(current_pos)

            event_data = {
                'type': 'mouse',
                'event_type': event.event_type,
                'button': event.button,
                'position': position_to_save, # 계산된 좌표
                'coord_mode': coord_mode_to_save, # 저장된 모드
                'time': event_time_relative
            }

        elif isinstance(event, mouse.MoveEvent):
            if not self.record_mouse_move or (current_time - getattr(self, 'last_move_time', 0) < self.mouse_move_interval):
                 return # 이동 녹화 비활성화 또는 너무 짧은 간격이면 무시

            # Move 이벤트는 딜레이 추가 안 함
            current_pos = (event.x, event.y)
            # print(f"Mouse Move to {current_pos}") # 디버깅

            # 좌표 계산
            position_to_save, coord_mode_to_save = self._calculate_coordinates(current_pos)

            event_data = {
                'type': 'mouse',
                'event_type': 'move',
                'button': 'move', # 구분용
                'position': position_to_save,
                'coord_mode': coord_mode_to_save,
                'time': event_time_relative
            }
            self.last_move_time = current_time # 마지막 *이동* 시간 업데이트

        elif isinstance(event, mouse.WheelEvent):
            # <<< 디버그 로그 제거 2 >>>
            # print(f"[DEBUG] WheelEvent detected: delta={event.delta}")

            # 버튼/휠 이벤트는 딜레이 체크 먼저
            self._add_delay_event_if_needed(event_time_relative) 
            current_pos = mouse.get_position()
            # print(f"Mouse Wheel: Delta {event.delta} at {current_pos}") # 기존 디버깅 주석 유지

            # 좌표 계산
            position_to_save, coord_mode_to_save = self._calculate_coordinates(current_pos)

            event_data = {
                'type': 'mouse',
                'event_type': 'wheel',
                'delta': event.delta,
                'position': position_to_save, # 계산된 좌표
                'coord_mode': coord_mode_to_save, # 저장된 모드
                'time': event_time_relative
            }
            # <<< 디버그 로그 제거 3 >>>
            # print(f"[DEBUG] Created wheel event_data: {event_data}")

        # 이벤트 기록 및 상태 업데이트
        if event_data:
            # <<< 디버그 로그 제거 4 >>>
            # if event_data.get('event_type') == 'wheel':
            #     print(f"[DEBUG] Appending wheel event_data to self.events")
            # else: # 다른 이벤트 타입 로그 (필요시 주석 해제)
            #    print(f"[DEBUG] Appending {event_data.get('event_type')} event_data to self.events")

            self.events.append(event_data)
            # 마지막 이벤트 시간 업데이트 (다음 Button/Wheel/Keyboard 딜레이 계산용)
            self.last_event_time = event_time_relative
            
            # 현재 마우스 위치 업데이트 (Mouse Relative 다음 계산 및 다른 모드 시작 시 사용 위함)
            if current_pos:
                 self.last_mouse_pos = current_pos # 모든 마우스 이벤트 후 업데이트
        # <<< 디버그 로그 제거 5 >>>
        # else:
        #     if not isinstance(event, mouse.MoveEvent) or self.record_mouse_move: # 이동 이벤트가 아니거나 이동 녹화가 켜져 있을 때만 로그
        #         print(f"[DEBUG] No event_data created for event: {type(event)}")

    def _calculate_coordinates(self, current_pos):
        """현재 위치와 녹화 모드에 따라 저장할 좌표와 모드를 계산하여 반환"""
        position_to_save = [0, 0]
        # 현재 설정된 녹화 모드를 가져옴 (이 함수 내에서 변경될 수 있음)
        coord_mode_to_save = self.recording_coord_mode 

        if coord_mode_to_save == 'absolute':
            position_to_save = list(current_pos)
        elif coord_mode_to_save == 'gesture_relative':
            if self.base_x is not None and self.base_y is not None:
                 position_to_save = [current_pos[0] - self.base_x, current_pos[1] - self.base_y]
            else:
                # 기준점 없으면 경고 후 절대 좌표로 저장
                print("Warning: Gesture relative mode selected but base coords not set. Recording absolute for this event.")
                position_to_save = list(current_pos)
                coord_mode_to_save = 'absolute' # 이 이벤트만 모드 변경
        elif coord_mode_to_save == 'playback_relative':
            if self.last_mouse_pos:
                # 이전 위치와의 차이 계산
                delta_x = current_pos[0] - self.last_mouse_pos[0]
                delta_y = current_pos[1] - self.last_mouse_pos[1]
                position_to_save = [delta_x, delta_y]
            else:
                # 첫 이벤트면 이동량 (0,0) 또는 절대 좌표 기록 (여기선 절대 좌표 선택)
                print("Warning: Mouse relative mode - first event? Recording absolute for this event.")
                position_to_save = list(current_pos)
                coord_mode_to_save = 'absolute' # 이 이벤트만 모드 변경
        else: # 알 수 없는 모드
            print(f"Warning: Unknown recording coord mode '{coord_mode_to_save}'. Recording absolute.")
            position_to_save = list(current_pos)
            coord_mode_to_save = 'absolute' # 폴백

        # 계산된 좌표와 실제 저장될 모드 반환
        return position_to_save, coord_mode_to_save

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