class MacroEditor:
    def __init__(self, storage):
        self.storage = storage
        self.events = []  # 현재 편집 중인 이벤트 목록
        self.modified = False
        self.current_editing_macro = None  # 현재 편집 중인 매크로 이름 추적
        print("MacroEditor 초기화됨, storage:", storage)  # 디버깅 로그
    
    def load_macro_for_editing(self, macro_name):
        """수정을 위해 매크로 로드"""
        print(f"load_macro_for_editing 호출: {macro_name}")  # 디버깅 로그
        events = self.storage.load_macro(macro_name)
        if events:
            import copy
            self.events = copy.deepcopy(events)  # 깊은 복사로 이벤트 로드
            self.modified = False
            self.current_editing_macro = macro_name  # 현재 편집 중인 매크로 이름 설정
            print(f"{len(events)}개 이벤트 로드됨, 현재 편집 중인 매크로: {self.current_editing_macro}")  # 디버깅 로그
            return True
        print("매크로 로드 실패")  # 디버깅 로그
        return False
    
    def get_events(self):
        """현재 이벤트 목록 반환"""
        print(f"get_events 호출됨: events={len(self.events)}개")  # 디버깅 로그
        return self.events
    
    def delete_event(self, index):
        """특정 인덱스의 이벤트 삭제"""
        print(f"delete_event 호출됨: {index}")  # 디버깅 로그
        if 0 <= index < len(self.events):
            del self.events[index]
            self.modified = True
            print(f"이벤트 {index} 삭제됨")  # 디버깅 로그
            return True
        print(f"이벤트 삭제 실패: 인덱스 {index}는 범위를 벗어남")  # 디버깅 로그
        return False
    
    def delete_events(self, indices):
        """여러 인덱스의 이벤트 삭제"""
        print(f"delete_events 호출됨: {indices}")  # 디버깅 로그
        if not indices:
            print("삭제할 인덱스가 없음")  # 디버깅 로그
            return False
            
        # 인덱스 정렬하여 높은 인덱스부터 삭제
        sorted_indices = sorted(indices, reverse=True)
        print(f"정렬된 인덱스: {sorted_indices}")  # 디버깅 로그
        
        # 유효한 인덱스인지 확인
        if max(sorted_indices) >= len(self.events):
            print(f"유효하지 않은 인덱스: 최대 {max(sorted_indices)}, 이벤트 개수: {len(self.events)}")  # 디버깅 로그
            return False
            
        # 높은 인덱스부터 삭제
        for idx in sorted_indices:
            if 0 <= idx < len(self.events):
                del self.events[idx]
                print(f"이벤트 {idx} 삭제됨")  # 디버깅 로그
        
        self.modified = True
        return True
    
    def add_delay_event(self, index, delay_seconds):
        """특정 인덱스 이후에 딜레이 이벤트 추가"""
        if 0 <= index < len(self.events):
            # 현재 이벤트의 시간 가져오기
            current_time = self.events[index]['time']
            
            # 딜레이 이벤트 생성
            delay_event = {
                'type': 'delay',
                'time': current_time + 0.001,  # 약간의 시간 추가하여 순서 보장
                'delay': delay_seconds
            }
            
            # 이벤트 목록에 삽입
            self.events.insert(index + 1, delay_event)
            
            # 이후 모든 이벤트 시간 조정
            for i in range(index + 2, len(self.events)):
                self.events[i]['time'] += delay_seconds
            
            self.modified = True
            return True
        return False
    
    def add_delay(self, index, delay_seconds):
        """이전 방식의 딜레이 추가 (호환성을 위해 유지)"""
        if 0 <= index < len(self.events):
            # 현재 이벤트의 시간 가져오기
            current_time = self.events[index]['time']
            
            # 이후 모든 이벤트 시간 조정
            for i in range(index + 1, len(self.events)):
                self.events[i]['time'] += delay_seconds
            
            self.modified = True
            return True
        return False
    
    def modify_event_time(self, index, new_time):
        """이벤트 타이밍 수정"""
        if 0 <= index < len(self.events):
            old_time = self.events[index]['time']
            time_diff = new_time - old_time
            
            # 현재 이벤트 및 이후 이벤트 시간 조정
            for i in range(index, len(self.events)):
                self.events[i]['time'] += time_diff
            
            self.modified = True
            return True
        return False
    
    def swap_events(self, index1, index2):
        """두 이벤트 위치 교환"""
        if (0 <= index1 < len(self.events) and 
            0 <= index2 < len(self.events)):
            
            # 이벤트 교환
            self.events[index1], self.events[index2] = (
                self.events[index2], self.events[index1]
            )
            
            self.modified = True
            return True
        return False
    
    def set_current_macro(self, macro_name):
        """현재 편집 중인 매크로 이름 설정"""
        print(f"현재 편집 중인 매크로 설정: {macro_name}")  # 디버깅 로그
        self.current_editing_macro = macro_name
        
        # 매크로가 변경되면 기존 이벤트 초기화
        if macro_name != self.current_editing_macro:
            self.events = []
    
    def save_edited_macro(self, name=None):
        """수정된 매크로 저장"""
        if not self.events:
            return False
        
        # 현재 매크로 이름 사용 또는 새 이름 사용
        if name is None:
            if self.current_editing_macro:  # 먼저 현재 편집 중인 매크로 이름 사용
                name = self.current_editing_macro
            elif self.storage.current_macro_name:  # 두 번째로 저장소의 현재 매크로 이름 사용
                name = self.storage.current_macro_name
        
        if name:
            print(f"매크로 저장: {name} (이벤트 {len(self.events)}개)")  # 디버깅 로그
            result = self.storage.update_macro(self.events, name)
            if result:
                self.modified = False
            return result
        
        return False
    
    def is_modified(self):
        """매크로가 수정되었는지 확인"""
        return self.modified
    
    def insert_event(self, index, event):
        """특정 인덱스에 이벤트 삽입 또는 맨 끝에 추가"""
        # 인덱스가 음수이면 리스트 끝을 의미하도록 처리
        if index < 0:
            index = len(self.events)
            print(f"insert_event: Negative index provided, inserting at the end (index {index}).") # 디버깅 로그

        # 유효한 인덱스 범위 검사 (0 <= index <= len(self.events))
        if 0 <= index <= len(self.events):
            print(f"insert_event: Inserting event at index {index}.") # 디버깅 로그
            # 이벤트에 시간 정보가 없으면 적절한 시간 계산 (기존 로직 유지)
            if 'time' not in event or event['time'] == 0:
                if index > 0 and index < len(self.events):
                    prev_time = self.events[index-1]['time']
                    next_time = self.events[index]['time']
                    event['time'] = prev_time + (next_time - prev_time) / 2
                elif index > 0:
                    event['time'] = self.events[index-1]['time'] + 0.1
                elif len(self.events) > 0:
                     event['time'] = max(0, self.events[0]['time'] - 0.1) # 음수 시간 방지
                else:
                    event['time'] = 0
                print(f"insert_event: Calculated time for event: {event['time']:.3f}s") # 디버깅 로그

            # --- is_relative 플래그 처리 추가 ---
            # event 딕셔너리에 is_relative 키가 있으면 그대로 사용, 없으면 기본값 False 추가
            if 'is_relative' not in event and event.get('type') == 'mouse' and event.get('event_type') == 'move':
                event['is_relative'] = False # 마우스 이동 이벤트의 기본값은 절대 좌표
                print("insert_event: Added default 'is_relative': False to mouse move event.") # 디버깅 로그
            elif 'is_relative' in event:
                 print(f"insert_event: Event has 'is_relative': {event['is_relative']}") # 디버깅 로그
            # --- is_relative 플래그 처리 끝 ---

            # 이벤트 삽입
            self.events.insert(index, event)
            self.modified = True
            print(f"insert_event: Event successfully inserted at index {index}.") # 디버깅 로그
            return index # 성공 시 삽입된 인덱스 반환
        else:
             print(f"insert_event: Failed to insert event. Invalid index {index} (list length: {len(self.events)}).") # 디버깅 로그
             return -1 # 실패 시 -1 반환
        
    def duplicate_events(self, indices):
        """선택된 이벤트들을 복제"""
        if not indices or not self.events:
            return False
        
        # 실제 이벤트 목록의 길이 확인
        if max(indices) >= len(self.events):
            return False
            
        # 복제할 이벤트들 수집
        events_to_duplicate = []
        for idx in indices:
            events_to_duplicate.append(self.events[idx].copy())
        
        if not events_to_duplicate:
            return False
            
        # 가장 마지막 이벤트의 시간 찾기
        last_time = 0
        for event in self.events:
            last_time = max(last_time, event['time'])
            
        # 시간 간격 계산 (첫 번째와 마지막 이벤트 사이의 시간)
        first_time = events_to_duplicate[0]['time']
        time_span = events_to_duplicate[-1]['time'] - first_time
        
        # 이벤트 복제 및 시간 조정
        for event in events_to_duplicate:
            new_event = event.copy()
            # 마지막 이벤트 시간 + 1초 + 이벤트 상대 시간
            new_event['time'] = last_time + 1.0 + (event['time'] - first_time)
            self.events.append(new_event)
        
        self.modified = True
        return True
        
    def modify_all_delays(self, multiplier):
        """모든 딜레이 이벤트의 딜레이 시간을 주어진 배수로 조정"""
        if not self.events:
            return False
            
        # 딜레이 이벤트가 있는지 확인
        has_delay_event = False
        for event in self.events:
            if event['type'] == 'delay':
                has_delay_event = True
                break
                
        if not has_delay_event:
            return False
            
        # 모든 딜레이 이벤트의 딜레이 시간 수정
        for event in self.events:
            if event['type'] == 'delay':
                event['delay'] *= multiplier
                
        self.modified = True
        return True
        
    def set_delay_time(self, index, new_delay_time):
        """특정 인덱스의 딜레이 이벤트 시간을 직접 설정"""
        if not self.events:
            return False
            
        if index < 0 or index >= len(self.events):
            return False
            
        event = self.events[index]
        if event['type'] != 'delay':
            return False
            
        # 딜레이 시간 직접 설정
        event['delay'] = new_delay_time
        self.modified = True
        return True
        
    def set_selected_delays_time(self, indices, new_delay_time):
        """여러 선택된 딜레이 이벤트의 시간을 직접 설정"""
        if not self.events or not indices:
            return False
            
        # 유효한 인덱스와 딜레이 이벤트인지 확인
        valid_delay_indices = []
        for idx in indices:
            if 0 <= idx < len(self.events):
                if self.events[idx]['type'] == 'delay':
                    valid_delay_indices.append(idx)
        
        if not valid_delay_indices:
            return False
            
        # 선택된 모든 딜레이 이벤트 시간 설정
        for idx in valid_delay_indices:
            self.events[idx]['delay'] = new_delay_time
            
        self.modified = True
        return True
        
    def move_event_up(self, index):
        """선택한 이벤트를 위로 이동"""
        if index <= 0 or index >= len(self.events):
            return False
            
        # 이벤트 교환
        self.events[index], self.events[index-1] = (
            self.events[index-1], self.events[index]
        )
        
        self.modified = True
        return True
        
    def move_event_down(self, index):
        """선택한 이벤트를 아래로 이동"""
        if index < 0 or index >= len(self.events) - 1:
            return False
            
        # 이벤트 교환
        self.events[index], self.events[index+1] = (
            self.events[index+1], self.events[index]
        )
        
        self.modified = True
        return True 