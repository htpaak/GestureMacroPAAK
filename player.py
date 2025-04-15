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
        self.base_x = 0 # 상대 이동 기준 X
        self.base_y = 0 # 상대 이동 기준 Y
    
    def play_macro(self, events, repeat_count=1, base_x=None, base_y=None):
        """매크로 실행 (선택적 기준 좌표 포함)"""
        if self.playing:
            print("이미 매크로가 실행 중입니다.")
            return False
        
        # 상대 이동 기준 좌표 설정
        if base_x is not None and base_y is not None:
            self.base_x, self.base_y = base_x, base_y
            print(f"제공된 기준 좌표 사용: ({self.base_x}, {self.base_y})")
        else:
            # 기준 좌표가 없으면 현재 마우스 위치 사용
            current_pos = mouse.get_position()
            self.base_x, self.base_y = current_pos
            print(f"현재 마우스 위치를 기준 좌표로 사용: ({self.base_x}, {self.base_y})")
        
        # 매크로 실행 스레드 시작
        self.stop_requested = False
        thread_start_req_time = time.time()
        print(f"[TimeLog] Requesting thread start at: {thread_start_req_time:.3f}")
        # 스레드에 이벤트와 반복 횟수 전달
        self.play_thread = threading.Thread(target=self._play_events, args=(events, repeat_count))
        self.play_thread.daemon = True
        self.play_thread.start()
        thread_started_time = time.time() # 스레드 start() 호출 직후
        print(f"[TimeLog] Thread start method returned at: {thread_started_time:.3f} (overhead: {thread_started_time - thread_start_req_time:.3f}s)")
        
        return True
    
    def stop_playing(self):
        """매크로 실행 중지"""
        if not self.playing:
            return False
        
        self.stop_requested = True
        if self.play_thread and self.play_thread.is_alive():
            self.play_thread.join(timeout=1.0)
            
        print("매크로 실행이 중지되었습니다.")
        self.playing = False # 상태 명시적 업데이트
        return True
    
    def _play_events(self, events, repeat_count):
        """실제 이벤트 실행 (내부 메소드)"""
        thread_actual_start_time = time.time()
        self.playing = True
        print(f"[TimeLog] Play thread actually started execution at: {thread_actual_start_time:.3f}")
        print(f"매크로 실행 시작 (반복 횟수: {repeat_count if repeat_count > 0 else '무한'})")
        # 스레드 시작 시 사용될 기준 좌표 로깅
        print(f"상대 이동 기준 좌표: ({self.base_x}, {self.base_y})")
        
        try:
            sort_start_time = time.time()
            sorted_events = sorted(events, key=lambda x: x['time'])
            sort_end_time = time.time()
            print(f"[TimeLog] Sorted events at: {sort_end_time:.3f} (took {sort_end_time - sort_start_time:.3f}s)")
            
            current_repeat = 0
            while (repeat_count == 0 or current_repeat < repeat_count) and not self.stop_requested:
                current_repeat += 1
                print(f"반복 {current_repeat}{' / ' + str(repeat_count) if repeat_count > 0 else ''}")
                
                loop_start_time = time.time() # 루프 시작 시간 (매 반복마다)
                print(f"[TimeLog] Repeat {current_repeat} started at: {loop_start_time:.3f}")
                
                for i, event in enumerate(sorted_events):
                    if self.stop_requested:
                        break
                    
                    event_type = event['type']
                    event_exec_start_time = time.time() # 이벤트 처리 시작
                    
                    # 딜레이 이벤트 처리
                    if event_type == 'delay':
                        # --- 디버깅 로그 추가 ---
                        print(f"--- Processing Delay Event ---")
                        print(f"Event Data: {event}") # 이벤트 객체 전체 출력
                        # --- 디버깅 로그 끝 ---

                        base_delay = event.get('delay', 0)
                        actual_delay = base_delay
                        if 'random_range' in event:
                             range_value = event.get('random_range', 0) # .get() 사용 권장
                             # range_value 타입 확인 및 변환 (안정성 강화)
                             try:
                                 range_value_float = float(range_value)
                             except (ValueError, TypeError):
                                 range_value_float = 0
                                 print(f"Warning: Invalid random_range '{range_value}', using 0.")

                             min_delay = max(0, base_delay - range_value_float)
                             max_delay = base_delay + range_value_float
                             actual_delay = random.uniform(min_delay, max_delay)
                             print(f"랜덤 딜레이: {base_delay:.3f}s ±{range_value_float:.3f}s → {actual_delay:.3f}s")
                        else:
                             print(f"일반 딜레이 값 (사용 전): {actual_delay:.3f}s")

                        # --- 디버깅 로그 추가 ---
                        print(f"Actual delay value for time.sleep(): {actual_delay:.3f}s (Type: {type(actual_delay)})")
                        # --- 디버깅 로그 끝 ---

                        sleep_start = time.time()
                        # *** 오직 딜레이 이벤트의 delay 값 만큼만 sleep ***
                        time.sleep(actual_delay)
                        delay_end_time = time.time()
                        print(f"[TimeLog] Finished delay event {i+1} at {delay_end_time:.3f} (slept {delay_end_time - sleep_start:.3f}s)")
                        continue
                    
                    # 딜레이가 아닌 이벤트는 바로 실행
                    if event_type == 'keyboard':
                        self._play_keyboard_event(event)
                    elif event_type == 'mouse':
                        # 기준 좌표 전달
                        self._play_mouse_event(event, self.base_x, self.base_y)
                
                    event_exec_end_time = time.time()
                    print(f"[TimeLog] Finished event {i+1} ({event_type}) execution at {event_exec_end_time:.3f} (took {event_exec_end_time - event_exec_start_time:.3f}s)")
                
                if not self.stop_requested and (repeat_count == 0 or current_repeat < repeat_count):
                    time.sleep(0.1) # 반복 사이 짧은 대기
            
            print("매크로 실행 완료/중단됨")
        except Exception as e:
            print(f"매크로 실행 중 오류 발생: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self.playing = False # 종료 시 상태 확실히 변경
    
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
    
    def _play_mouse_event(self, event, base_x, base_y):
        """마우스 이벤트 실행 (기준 좌표 사용)"""
        try:
            event_type = event['event_type']
            target_pos_orig = list(event['position']) # 원본 좌표 (튜플을 리스트로)
            target_pos = list(target_pos_orig) # 수정될 좌표
            
            # 상대 좌표 처리 먼저 수행하여 기준 위치 결정
            is_relative = event.get('is_relative', False)
            base_target_x, base_target_y = 0, 0
            
            if is_relative:
                # 기준 좌표에 상대 좌표 더하기
                base_target_x = base_x + target_pos[0]
                base_target_y = base_y + target_pos[1]
                print(f"마우스 상대 이동 처리: Base({base_x}, {base_y}) + Rel({target_pos[0]}, {target_pos[1]}) -> BaseTarget({base_target_x}, {base_target_y})")
            else:
                # 절대 좌표 사용
                base_target_x, base_target_y = target_pos[0], target_pos[1]
                print(f"마우스 절대 이동 처리: BaseTarget({base_target_x}, {base_target_y})")
            
            # 랜덤 좌표 범위 처리 (결정된 기준 위치에 적용)
            final_x, final_y = base_target_x, base_target_y
            if 'random_range' in event and event_type != 'scroll': # 스크롤에는 랜덤 좌표 무의미
                range_px = event['random_range']
                # 정수로 변환 보장
                range_px_int = int(range_px) if isinstance(range_px, (int, float)) else 0
                if range_px_int > 0:
                    random_x = random.randint(base_target_x - range_px_int, base_target_x + range_px_int)
                    random_y = random.randint(base_target_y - range_px_int, base_target_y + range_px_int)
                    final_x, final_y = random_x, random_y # 최종 좌표 업데이트
                    print(f"랜덤 좌표 적용: BaseTarget({base_target_x}, {base_target_y}) ±{range_px_int}px → Final({final_x}, {final_y})")
            
            # 마우스 액션 수행 (계산된 final_x, final_y 사용)
            if event_type == 'move':
                mouse.move(final_x, final_y)
                # print(f"마우스 이동: ({final_x}, {final_y})") # 로그는 위에서 출력
            elif event_type == 'down':
                button = event['button']
                mouse.move(final_x, final_y) # 이동 후 클릭
                mouse.press(button=button)
                print(f"마우스 {button} 누름: ({final_x}, {final_y})")
            elif event_type == 'up':
                button = event['button']
                mouse.move(final_x, final_y) # 이동 후 떼기
                mouse.release(button=button)
                print(f"마우스 {button} 떼기: ({final_x}, {final_y})")
            elif event_type == 'double':
                button = event['button']
                mouse.move(final_x, final_y) # 이동 후 더블클릭
                mouse.double_click(button=button)
                print(f"마우스 {button} 더블 클릭: ({final_x}, {final_y})")
            elif event_type == 'scroll':
                delta = event['delta']
                # 스크롤은 특정 위치에서 발생해야 하는 경우가 많음
                mouse.move(final_x, final_y)
                mouse.wheel(delta=delta)
                print(f"마우스 스크롤: Delta {delta} at ({final_x}, {final_y})")
            
        except Exception as e:
            print(f"마우스 이벤트 실행 중 오류: {e}")
            import traceback
            traceback.print_exc()
    
    def is_playing(self):
        """매크로 실행 중인지 확인"""
        return self.playing 