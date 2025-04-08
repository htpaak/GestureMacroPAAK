import keyboard
import mouse
import time
import threading
import random

class MacroPlayer:
    def __init__(self):
        self.playing = False
        self.stop_requested = False
        self.play_thread = None
        
        # 상대 좌표 재생 시 기준점
        self.base_x = 0
        self.base_y = 0
    
    def play_macro(self, events, repeat_count=1):
        """매크로 실행"""
        if self.playing:
            print("이미 매크로가 실행 중입니다.")
            return False
        
        # 매크로 실행 스레드 시작
        self.stop_requested = False
        self.play_thread = threading.Thread(target=self._play_events, args=(events, repeat_count))
        self.play_thread.daemon = True
        self.play_thread.start()
        
        # 상대 좌표 사용 시 시작 위치 저장
        pos = mouse.get_position()
        self.base_x, self.base_y = pos
        
        return True
    
    def stop_playing(self):
        """매크로 실행 중지"""
        if not self.playing:
            return False
        
        self.stop_requested = True
        # 스레드가 종료될 때까지 잠시 대기
        if self.play_thread and self.play_thread.is_alive():
            self.play_thread.join(timeout=1.0)
            
        print("매크로 실행이 중지되었습니다.")
        return True
    
    def _play_events(self, events, repeat_count):
        """실제 이벤트 실행 (내부 메소드)"""
        self.playing = True
        print(f"매크로 실행 시작 (반복 횟수: {repeat_count if repeat_count > 0 else '무한'})")
        
        try:
            # 시간순으로 이벤트 정렬
            sorted_events = sorted(events, key=lambda x: x['time'])
            
            # 반복 실행
            current_repeat = 0
            
            while (repeat_count == 0 or current_repeat < repeat_count) and not self.stop_requested:
                current_repeat += 1
                print(f"반복 {current_repeat}{' / ' + str(repeat_count) if repeat_count > 0 else ''}")
                
                # 시작 시간
                start_time = time.time()
                last_event_time = start_time
                
                for event in sorted_events:
                    if self.stop_requested:
                        break
                    
                    # 이벤트 타입에 따라 처리
                    event_type = event['type']
                    
                    # 딜레이 이벤트인 경우
                    if event_type == 'delay':
                        base_delay = event['delay']
                        
                        # 랜덤 범위가 있는 경우
                        if 'random_range' in event:
                            range_value = event['random_range']
                            min_delay = max(0, base_delay - range_value)  # 음수 딜레이 방지
                            max_delay = base_delay + range_value
                            actual_delay = random.uniform(min_delay, max_delay)
                            print(f"랜덤 딜레이: {base_delay:.2f}초 ±{range_value:.2f}초 → {actual_delay:.2f}초")
                            time.sleep(actual_delay)
                        else:
                            # 기존 고정 딜레이 처리
                            print(f"딜레이: {base_delay:.2f}초")
                            time.sleep(base_delay)
                        
                        last_event_time = time.time()
                        continue
                    
                    # 이벤트 간 시간 차이만큼 대기 (딜레이 이벤트가 아닌 경우)
                    event_time = event['time']
                    if event != sorted_events[0]:  # 첫 이벤트가 아닌 경우
                        prev_event_time = sorted_events[sorted_events.index(event) - 1]['time']
                        time_diff = event_time - prev_event_time
                        
                        # 이전 이벤트가 딜레이 이벤트였다면 대기하지 않음
                        prev_event = sorted_events[sorted_events.index(event) - 1]
                        if prev_event['type'] != 'delay' and time_diff > 0:
                            time.sleep(time_diff)
                    
                    # 키보드 이벤트 처리
                    if event_type == 'keyboard':
                        self._play_keyboard_event(event)
                        
                    # 마우스 이벤트 처리
                    elif event_type == 'mouse':
                        self._play_mouse_event(event)
                
                # 반복 사이에 약간의 딜레이 추가
                if not self.stop_requested and (repeat_count == 0 or current_repeat < repeat_count):
                    time.sleep(0.5)
            
            print("매크로 실행 완료")
        except Exception as e:
            print(f"매크로 실행 중 오류 발생: {e}")
        finally:
            self.playing = False
    
    def _play_keyboard_event(self, event):
        """키보드 이벤트 실행"""
        try:
            key = event['key']
            event_type = event['event_type']
            
            if event_type == 'down':
                keyboard.press(key)
                print(f"키보드 누름: {key}")
            elif event_type == 'up':
                keyboard.release(key)
                print(f"키보드 떼기: {key}")
        except Exception as e:
            print(f"키보드 이벤트 실행 중 오류: {e}")
    
    def _play_mouse_event(self, event):
        """마우스 이벤트 실행"""
        try:
            event_type = event['event_type']
            position = event['position']
            
            # 랜덤 좌표 범위가 있는 경우
            if 'position_range' in event:
                # 기존 좌표
                original_x, original_y = position
                range_px = event['position_range']
                
                # 범위 내에서 무작위 좌표 생성
                random_x = random.randint(original_x - range_px, original_x + range_px)
                random_y = random.randint(original_y - range_px, original_y + range_px)
                
                # 무작위 좌표로 변경
                position = (random_x, random_y)
                print(f"랜덤 좌표: ({original_x}, {original_y}) ±{range_px}px → ({random_x}, {random_y})")
            
            # 상대좌표 처리
            if event.get('is_relative', False):
                position = (position[0] + self.base_x, position[1] + self.base_y)
            
            # 마우스 이동
            if event_type == 'move':
                mouse.move(position[0], position[1])
                print(f"마우스 이동: {position}")
            
            # 마우스 클릭 (누르기)
            elif event_type == 'down':
                button = event['button']
                mouse.move(position[0], position[1])
                mouse.press(button=button)
                print(f"마우스 {button} 누름: {position}")
                
            # 마우스 클릭 (떼기)
            elif event_type == 'up':
                button = event['button']
                mouse.move(position[0], position[1])
                mouse.release(button=button)
                print(f"마우스 {button} 떼기: {position}")
                
            # 마우스 더블 클릭
            elif event_type == 'double':
                button = event['button']
                mouse.move(position[0], position[1])
                mouse.double_click(button=button)
                print(f"마우스 {button} 더블 클릭: {position}")
                
            # 마우스 스크롤
            elif event_type == 'scroll':
                delta = event['delta']
                mouse.move(position[0], position[1])
                mouse.wheel(delta=delta)
                print(f"마우스 스크롤: {delta}, 위치: {position}")
        except Exception as e:
            print(f"마우스 이벤트 실행 중 오류: {e}")
            import traceback
            traceback.print_exc()
            
    def is_playing(self):
        """매크로 실행 중인지 확인"""
        return self.playing 