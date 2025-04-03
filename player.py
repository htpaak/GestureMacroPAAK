import keyboard
import mouse
import time
import threading

class MacroPlayer:
    def __init__(self):
        self.playing = False
        self.events = []
        self.play_thread = None
        
        # 상대 좌표 재생 시 기준점
        self.base_x = 0
        self.base_y = 0
    
    def play_macro(self, events, repeat_count=1):
        """매크로 실행"""
        if self.playing:
            return False
        
        self.events = events
        self.playing = True
        
        # 상대 좌표 사용 시 시작 위치 저장
        pos = mouse.get_position()
        self.base_x, self.base_y = pos
        
        # 새로운 스레드에서 매크로 실행
        self.play_thread = threading.Thread(target=self._play_events, args=(repeat_count,))
        self.play_thread.daemon = True
        self.play_thread.start()
        
        return True
    
    def stop_playing(self):
        """매크로 재생 중지"""
        self.playing = False
        if self.play_thread and self.play_thread.is_alive():
            self.play_thread.join(timeout=1)
        return True
    
    def _play_events(self, repeat_count):
        """이벤트 재생"""
        try:
            for _ in range(repeat_count):
                if not self.playing:
                    break
                
                # 타임라인 상에서 각 이벤트를 정렬된 순서로 실행
                events_sorted = sorted(self.events, key=lambda e: e['time'])
                
                for i, event in enumerate(events_sorted):
                    if not self.playing:
                        break
                    
                    # 첫 번째 이벤트가 아니면서 이전 이벤트와 시간 차이가 있는 경우,
                    # 이벤트 시간 차이만큼 대기 (딜레이 이벤트가 아닌 경우)
                    if i > 0 and event['type'] != 'delay':
                        time_diff = event['time'] - events_sorted[i-1]['time']
                        if time_diff > 0:
                            time.sleep(time_diff)
                    
                    # 이벤트 유형에 따라 실행
                    if event['type'] == 'keyboard':
                        self._play_keyboard_event(event)
                    elif event['type'] == 'mouse':
                        self._play_mouse_event(event)
                    elif event['type'] == 'delay':
                        # 딜레이 이벤트는 지정된 시간만큼 대기
                        time.sleep(event['delay'])
                        print(f"딜레이 {event['delay']}초 실행")
        finally:
            self.playing = False
            print("매크로 재생이 완료되었습니다.")
    
    def _play_keyboard_event(self, event):
        """키보드 이벤트 실행"""
        key = event['key']
        
        if event['event_type'] == 'down':
            keyboard.press(key)
        elif event['event_type'] == 'up':
            keyboard.release(key)
    
    def _play_mouse_event(self, event):
        """마우스 이벤트 실행"""
        event_type = event['event_type']
        
        # 상대좌표 처리
        if 'position' in event:
            x, y = event['position']
            
            # 상대좌표인 경우 기준점 기준으로 조정
            if event.get('is_relative', False):
                x += self.base_x
                y += self.base_y
        
        if event_type == 'move':
            # 마우스 이동
            if 'position' in event:
                mouse.move(x, y)
        elif event_type == 'down':
            # 마우스 버튼 누르기
            if 'button' in event:
                mouse.move(x, y)  # 먼저 해당 위치로 이동
                mouse.press(button=event['button'])
        elif event_type == 'up':
            # 마우스 버튼 떼기
            if 'button' in event:
                mouse.move(x, y)  # 먼저 해당 위치로 이동
                mouse.release(button=event['button'])
        elif event_type == 'double':
            # 마우스 더블 클릭
            if 'button' in event:
                mouse.move(x, y)  # 먼저 해당 위치로 이동
                mouse.double_click(button=event['button'])
        elif event_type == 'scroll':
            # 마우스 스크롤
            if 'delta' in event:
                mouse.move(x, y)  # 먼저 해당 위치로 이동
                mouse.wheel(delta=event['delta'])
    
    def is_playing(self):
        """매크로 재생 중인지 확인"""
        return self.playing 