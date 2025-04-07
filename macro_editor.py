import copy

class MacroEditor:
    def __init__(self):
        """매크로 에디터 초기화"""
        self.events = []
        print("MacroEditor 초기화됨")  # 디버깅 로그 추가
        
    def get_events(self):
        """현재 매크로 이벤트 리스트 반환"""
        print(f"get_events 호출됨: {len(self.events)}개 이벤트")  # 디버깅 로그 추가
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
        print(f"delete_events 호출됨: {indices}")  # 디버깅 로그 추가
        if not indices or not self.events:
            print("삭제할 이벤트가 없음")  # 디버깅 로그 추가
            return False
            
        # 인덱스를 내림차순으로 정렬 (삭제 순서 중요)
        sorted_indices = sorted(indices, reverse=True)
        print(f"정렬된 인덱스: {sorted_indices}")  # 디버깅 로그 추가
        
        # 유효한 인덱스만 처리
        try:
            for idx in sorted_indices:
                if 0 <= idx < len(self.events):
                    print(f"이벤트 {idx} 삭제")  # 디버깅 로그 추가
                    del self.events[idx]
                else:
                    print(f"인덱스 {idx}는 범위를 벗어남 (총 {len(self.events)}개)")  # 디버깅 로그 추가
            return True
        except Exception as e:
            print(f"이벤트 삭제 중 오류 발생: {e}")
            return False
            
    def insert_event(self, index, event):
        """특정 위치에 이벤트 삽입"""
        print(f"insert_event 호출됨: 인덱스 {index}")  # 디버깅 로그 추가
        if not event:
            print("이벤트가 비어있음")  # 디버깅 로그 추가
            return False
            
        try:
            # 인덱스가 범위를 벗어나면 조정
            if index < 0:
                index = 0
                print("인덱스를 0으로 조정")  # 디버깅 로그 추가
            elif index > len(self.events):
                index = len(self.events)
                print(f"인덱스를 {index}로 조정 (마지막)")  # 디버깅 로그 추가
                
            self.events.insert(index, event)
            print(f"이벤트 삽입 성공: 현재 {len(self.events)}개 이벤트")  # 디버깅 로그 추가
            return True
        except Exception as e:
            print(f"이벤트 삽입 중 오류 발생: {e}")
            return False
            
    def move_event_up(self, index):
        """이벤트를 위로 이동"""
        print(f"move_event_up 호출됨: 인덱스 {index}")  # 디버깅 로그 추가
        if not self.events or index <= 0 or index >= len(self.events):
            print("이동 불가: 이벤트 없음 또는 범위 초과")  # 디버깅 로그 추가
            return False
            
        try:
            # 현재 위치의 이벤트와 한 단계 위의 이벤트 교환
            self.events[index], self.events[index-1] = self.events[index-1], self.events[index]
            print(f"이벤트 위로 이동 성공: {index} -> {index-1}")  # 디버깅 로그 추가
            return True
        except Exception as e:
            print(f"이벤트 이동 중 오류 발생: {e}")
            return False
            
    def move_event_down(self, index):
        """이벤트를 아래로 이동"""
        print(f"move_event_down 호출됨: 인덱스 {index}")  # 디버깅 로그 추가
        if not self.events or index < 0 or index >= len(self.events) - 1:
            print("이동 불가: 이벤트 없음 또는 범위 초과")  # 디버깅 로그 추가
            return False
            
        try:
            # 현재 위치의 이벤트와, 한 단계 아래 이벤트 교환
            self.events[index], self.events[index+1] = self.events[index+1], self.events[index]
            print(f"이벤트 아래로 이동 성공: {index} -> {index+1}")  # 디버깅 로그 추가
            return True
        except Exception as e:
            print(f"이벤트 이동 중 오류 발생: {e}")
            return False
            
    def modify_all_delays(self, multiplier):
        """모든 딜레이 시간 수정"""
        print(f"modify_all_delays 호출됨: 배수 {multiplier}")  # 디버깅 로그 추가
        if not self.events:
            print("수정 불가: 이벤트 없음")  # 디버깅 로그 추가
            return False
            
        modified = False
        try:
            for event in self.events:
                if event.get('type') == 'delay' and 'delay' in event:
                    event['delay'] *= multiplier
                    modified = True
                    print(f"딜레이 수정: {event['delay']}")  # 디버깅 로그 추가
            print(f"딜레이 수정 결과: {modified}")  # 디버깅 로그 추가
            return modified
        except Exception as e:
            print(f"딜레이 수정 중 오류 발생: {e}")
            return False
            
    def set_selected_delays_time(self, indices, delay_time):
        """선택된 딜레이 이벤트의 시간 설정"""
        print(f"set_selected_delays_time 호출됨: 인덱스 {indices}, 시간 {delay_time}")  # 디버깅 로그 추가
        if not indices or not self.events:
            print("수정 불가: 인덱스 또는 이벤트 없음")  # 디버깅 로그 추가
            return False
            
        modified = False
        try:
            valid_indices = 0
            for idx in indices:
                if 0 <= idx < len(self.events):
                    event = self.events[idx]
                    if event.get('type') == 'delay':
                        event['delay'] = delay_time
                        modified = True
                        valid_indices += 1
                        print(f"딜레이 시간 설정: 인덱스 {idx}, 값 {delay_time}")  # 디버깅 로그 추가
            print(f"딜레이 시간 설정 결과: {valid_indices}개 수정됨")  # 디버깅 로그 추가
            return modified
        except Exception as e:
            print(f"딜레이 시간 설정 중 오류 발생: {e}")
            return False 