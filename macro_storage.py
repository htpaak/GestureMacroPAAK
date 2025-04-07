import os
import json

class MacroStorage:
    def __init__(self, base_path="macros"):
        """매크로 스토리지 초기화"""
        self.base_path = base_path
        
        # 디렉토리가 없으면 생성
        if not os.path.exists(self.base_path):
            os.makedirs(self.base_path)
            
    def get_full_path(self, macro_name):
        """매크로 파일의 전체 경로 반환"""
        # 파일 확장자가 없으면 .json 추가
        if not macro_name.lower().endswith('.json'):
            macro_name = f"{macro_name}.json"
            
        return os.path.join(self.base_path, macro_name)
        
    def save_macro(self, events, macro_name):
        """매크로 이벤트 저장"""
        try:
            # 파일 경로 설정
            full_path = self.get_full_path(macro_name)
            
            # 디렉토리 확인 및 생성
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            
            # 파일에 이벤트 저장
            with open(full_path, 'w') as f:
                json.dump(events, f, indent=2)
                
            print(f"매크로 파일 저장 성공: {full_path}")
            return True
        except Exception as e:
            print(f"매크로 저장 중 오류 발생: {e}")
            return False
            
    def load_macro(self, macro_name):
        """매크로 이벤트 로드"""
        try:
            # 파일 경로 설정
            full_path = self.get_full_path(macro_name)
            
            # 매크로 파일이 존재하는지 확인
            if not os.path.exists(full_path):
                print(f"매크로 파일을 찾을 수 없음: {full_path}")
                return []
                
            # 파일 읽기
            with open(full_path, 'r') as f:
                try:
                    # JSON 파일 읽기
                    data = json.load(f)
                    print(f"매크로 파일 불러오기 성공: {full_path}")
                    
                    # 데이터 유효성 검사
                    if not isinstance(data, list):
                        print(f"매크로 데이터가 리스트 형식이 아님: {type(data)}")
                        if isinstance(data, dict) and 'events' in data:
                            print("이벤트 키에서 매크로 데이터 시도")
                            return data['events']
                        return []
                    
                    return data
                except json.JSONDecodeError as e:
                    print(f"JSON 파싱 오류: {e}")
                    return []
        except Exception as e:
            print(f"매크로 로드 중 오류 발생: {e}")
            return []
            
    def delete_macro(self, macro_name):
        """매크로 파일 삭제"""
        try:
            # 파일 경로 설정
            full_path = self.get_full_path(macro_name)
            
            # 파일이 존재하면 삭제
            if os.path.exists(full_path):
                os.remove(full_path)
                print(f"매크로 파일 삭제 성공: {full_path}")
                return True
                
            print(f"삭제할 매크로 파일을 찾을 수 없음: {full_path}")
            return False
        except Exception as e:
            print(f"매크로 삭제 중 오류 발생: {e}")
            return False
    
    def get_macro_list(self):
        """저장된 매크로 목록 가져오기"""
        try:
            # 디렉토리가 없으면 빈 목록 반환
            if not os.path.exists(self.base_path):
                return []
                
            # 디렉토리에서 JSON 파일만 필터링
            macro_files = [f for f in os.listdir(self.base_path) 
                         if f.lower().endswith('.json')]
                         
            return macro_files
        except Exception as e:
            print(f"매크로 목록 가져오기 중 오류 발생: {e}")
            return [] 