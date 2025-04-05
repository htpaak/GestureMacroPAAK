class MacroEditor:
    def __init__(self, storage):
        self.storage = storage
        self.current_events = []
        self.modified = False
    
    def load_macro_for_editing(self, macro_name):
        """수정을 위해 매크로 로드"""
        events = self.storage.load_macro(macro_name)
        if events:
            self.current_events = events
            self.modified = False
            return True
        return False
    
    def get_events(self):
        """현재 이벤트 목록 반환"""
        return self.current_events
    
    def delete_event(self, index):
        """특정 인덱스의 이벤트 삭제"""
        if 0 <= index < len(self.current_events):
            del self.current_events[index]
            self.modified = True
            return True
        return False
    
    def delete_events(self, indices):
        """여러 인덱스의 이벤트 삭제"""
        if not indices:
            return False
            
        # 인덱스 정렬하여 높은 인덱스부터 삭제
        sorted_indices = sorted(indices, reverse=True)
        
        # 유효한 인덱스인지 확인
        if max(sorted_indices) >= len(self.current_events):
            return False
            
        # 높은 인덱스부터 삭제
        for idx in sorted_indices:
            if 0 <= idx < len(self.current_events):
                del self.current_events[idx]
        
        self.modified = True
        return True
    
    def add_delay_event(self, index, delay_seconds):
        """특정 인덱스 이후에 딜레이 이벤트 추가"""
        if 0 <= index < len(self.current_events):
            # 현재 이벤트의 시간 가져오기
            current_time = self.current_events[index]['time']
            
            # 딜레이 이벤트 생성
            delay_event = {
                'type': 'delay',
                'time': current_time + 0.001,  # 약간의 시간 추가하여 순서 보장
                'delay': delay_seconds
            }
            
            # 이벤트 목록에 삽입
            self.current_events.insert(index + 1, delay_event)
            
            # 이후 모든 이벤트 시간 조정
            for i in range(index + 2, len(self.current_events)):
                self.current_events[i]['time'] += delay_seconds
            
            self.modified = True
            return True
        return False
    
    def add_delay(self, index, delay_seconds):
        """이전 방식의 딜레이 추가 (호환성을 위해 유지)"""
        if 0 <= index < len(self.current_events):
            # 현재 이벤트의 시간 가져오기
            current_time = self.current_events[index]['time']
            
            # 이후 모든 이벤트 시간 조정
            for i in range(index + 1, len(self.current_events)):
                self.current_events[i]['time'] += delay_seconds
            
            self.modified = True
            return True
        return False
    
    def modify_event_time(self, index, new_time):
        """이벤트 타이밍 수정"""
        if 0 <= index < len(self.current_events):
            old_time = self.current_events[index]['time']
            time_diff = new_time - old_time
            
            # 현재 이벤트 및 이후 이벤트 시간 조정
            for i in range(index, len(self.current_events)):
                self.current_events[i]['time'] += time_diff
            
            self.modified = True
            return True
        return False
    
    def swap_events(self, index1, index2):
        """두 이벤트 위치 교환"""
        if (0 <= index1 < len(self.current_events) and 
            0 <= index2 < len(self.current_events)):
            
            # 이벤트 교환
            self.current_events[index1], self.current_events[index2] = (
                self.current_events[index2], self.current_events[index1]
            )
            
            self.modified = True
            return True
        return False
    
    def save_edited_macro(self, name=None):
        """수정된 매크로 저장"""
        if not self.current_events:
            return False
        
        # 현재 매크로 이름 사용 또는 새 이름 사용
        if name is None and self.storage.current_macro_name:
            name = self.storage.current_macro_name
        
        if name:
            result = self.storage.update_macro(self.current_events, name)
            if result:
                self.modified = False
            return result
        
        return False
    
    def is_modified(self):
        """매크로가 수정되었는지 확인"""
        return self.modified
    
    def insert_event(self, index, event):
        """특정 인덱스에 이벤트 삽입"""
        if 0 <= index <= len(self.current_events):
            # 이벤트에 시간 정보가 없으면 적절한 시간 계산
            if 'time' not in event or event['time'] == 0:
                # 삽입 위치 앞뒤 이벤트의 시간 정보 사용
                if index > 0 and index < len(self.current_events):
                    # 앞뒤 이벤트 시간의 중간 값으로 설정
                    prev_time = self.current_events[index-1]['time']
                    next_time = self.current_events[index]['time']
                    event['time'] = prev_time + (next_time - prev_time) / 2
                elif index > 0:
                    # 마지막에 추가하는 경우 마지막 이벤트 시간 + 0.1초
                    event['time'] = self.current_events[index-1]['time'] + 0.1
                elif len(self.current_events) > 0:
                    # 맨 앞에 추가하는 경우 첫 이벤트 시간 - 0.1초
                    event['time'] = self.current_events[0]['time'] - 0.1
                else:
                    # 첫 이벤트인 경우 0으로 설정
                    event['time'] = 0
                    
            # 이벤트 삽입
            self.current_events.insert(index, event)
            self.modified = True
            return True
        return False
        
    def duplicate_events(self, indices):
        """선택된 이벤트들을 복제"""
        if not indices or not self.current_events:
            return False
        
        # 실제 이벤트 목록의 길이 확인
        if max(indices) >= len(self.current_events):
            return False
            
        # 복제할 이벤트들 수집
        events_to_duplicate = []
        for idx in indices:
            events_to_duplicate.append(self.current_events[idx].copy())
        
        if not events_to_duplicate:
            return False
            
        # 가장 마지막 이벤트의 시간 찾기
        last_time = 0
        for event in self.current_events:
            last_time = max(last_time, event['time'])
            
        # 시간 간격 계산 (첫 번째와 마지막 이벤트 사이의 시간)
        first_time = events_to_duplicate[0]['time']
        time_span = events_to_duplicate[-1]['time'] - first_time
        
        # 이벤트 복제 및 시간 조정
        for event in events_to_duplicate:
            new_event = event.copy()
            # 마지막 이벤트 시간 + 1초 + 이벤트 상대 시간
            new_event['time'] = last_time + 1.0 + (event['time'] - first_time)
            self.current_events.append(new_event)
        
        self.modified = True
        return True 