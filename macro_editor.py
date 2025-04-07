import copy

class MacroEditor:
    def __init__(self):
        """매크로 에디터 초기화"""
        self.events = []
        
    def get_events(self):
        """현재 매크로 이벤트 리스트 반환"""
        return self.events
        
    def load_events(self, events):
        """이벤트 리스트 로드"""
        # 디버깅 로그 추가
        print(f"에디터에 이벤트 로드 시도: {len(events)}개, 타입: {type(events)}")
            
        try:
            # 이벤트 리스트 복사 (원본 변경 방지)
            self.events = []
            
            # 이벤트가 리스트인지 확인
            if isinstance(events, list):
                # 각 이벤트 복사
                for event in events:
                    if isinstance(event, dict):
                        self.events.append(event.copy())
                    else:
                        print(f"경고: 이벤트가 딕셔너리가 아님 - {type(event)}")
            else:
                print(f"경고: 이벤트 데이터가 리스트가 아님 - {type(events)}")
                
            print(f"에디터에 {len(self.events)}개 이벤트 로드 완료")
            return True
        except Exception as e:
            print(f"이벤트 로드 중 오류 발생: {e}")
            self.events = []
            return False
            
    def delete_events(self, indices):
        """이벤트 삭제"""
        if not indices or not self.events:
            return False
            
        # 인덱스를 내림차순으로 정렬 (삭제 순서 중요)
        sorted_indices = sorted(indices, reverse=True)
        
        # 유효한 인덱스만 처리
        try:
            for idx in sorted_indices:
                if 0 <= idx < len(self.events):
                    del self.events[idx]
            return True
        except Exception as e:
            print(f"이벤트 삭제 중 오류 발생: {e}")
            return False
            
    def insert_event(self, index, event):
        """특정 위치에 이벤트 삽입"""
        if not event:
            return False
            
        try:
            # 인덱스가 범위를 벗어나면 조정
            if index < 0:
                index = 0
            elif index > len(self.events):
                index = len(self.events)
                
            self.events.insert(index, event)
            return True
        except Exception as e:
            print(f"이벤트 삽입 중 오류 발생: {e}")
            return False
            
    def move_event_up(self, index):
        """이벤트를 위로 이동"""
        if not self.events or index <= 0 or index >= len(self.events):
            return False
            
        try:
            # 현재 위치의 이벤트와 한 단계 위의 이벤트 교환
            self.events[index], self.events[index-1] = self.events[index-1], self.events[index]
            return True
        except Exception as e:
            print(f"이벤트 이동 중 오류 발생: {e}")
            return False
            
    def move_event_down(self, index):
        """이벤트를 아래로 이동"""
        if not self.events or index < 0 or index >= len(self.events) - 1:
            return False
            
        try:
            # 현재 위치의 이벤트와, 한 단계 아래 이벤트 교환
            self.events[index], self.events[index+1] = self.events[index+1], self.events[index]
            return True
        except Exception as e:
            print(f"이벤트 이동 중 오류 발생: {e}")
            return False
            
    def modify_all_delays(self, multiplier):
        """모든 딜레이 시간 수정"""
        if not self.events:
            return False
            
        modified = False
        try:
            for event in self.events:
                if event.get('type') == 'delay' and 'delay' in event:
                    event['delay'] *= multiplier
                    modified = True
            return modified
        except Exception as e:
            print(f"딜레이 수정 중 오류 발생: {e}")
            return False
            
    def set_selected_delays_time(self, indices, delay_time):
        """선택된 딜레이 이벤트의 시간 설정"""
        if not indices or not self.events:
            return False
            
        modified = False
        try:
            for idx in indices:
                if 0 <= idx < len(self.events):
                    event = self.events[idx]
                    if event.get('type') == 'delay':
                        event['delay'] = delay_time
                        modified = True
            return modified
        except Exception as e:
            print(f"딜레이 시간 설정 중 오류 발생: {e}")
            return False 