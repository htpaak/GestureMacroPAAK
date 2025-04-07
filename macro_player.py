import copy

class MacroPlayer:
    def __init__(self):
        """매크로 플레이어 초기화"""
        self.events = []
        self.playing = False
        self.stop_requested = False
        
    def load_events(self, events):
        """이벤트 리스트 로드"""
        # 디버깅 로그 추가
        print(f"플레이어에 이벤트 로드 시도: {len(events)}개, 타입: {type(events)}")
        
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
                
            print(f"플레이어에 {len(self.events)}개 이벤트 로드 완료")
            return True
        except Exception as e:
            print(f"이벤트 로드 중 오류 발생: {e}")
            self.events = []
            return False
    
    def play_macro(self, events=None, repeat_count=1):
        """매크로 실행"""
        # 이벤트가 전달되면 해당 이벤트 로드
        if events is not None:
            self.load_events(events)
            
        if not self.events:
            print("실행할 이벤트가 없습니다.")
            return False
            
        # 이미 실행 중이면 중지
        if self.playing:
            self.stop_macro()
            
        # 실행 상태 설정
        self.playing = True
        self.stop_requested = False
            
        # 이벤트 실행 로직
        print(f"매크로 실행 시작 (반복: {repeat_count})")
        
        # 여기에 실제 매크로 실행 코드 추가
        
        return True
        
    def stop_macro(self):
        """매크로 실행 중지"""
        if not self.playing:
            return
            
        self.stop_requested = True
        self.playing = False
        print("매크로 실행 중지 요청")
        
        # 여기에 매크로 중지 관련 코드 추가 