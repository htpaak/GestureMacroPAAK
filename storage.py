import json
import os
import time
from datetime import datetime

class MacroStorage:
    def __init__(self, storage_dir="macros"):
        self.storage_dir = storage_dir
        self.ensure_storage_dir()
        self.current_macro = None
        self.current_macro_name = None
    
    def ensure_storage_dir(self):
        """저장 디렉토리 확인 및 생성"""
        if not os.path.exists(self.storage_dir):
            os.makedirs(self.storage_dir)
    
    def save_macro(self, events, name=None):
        """매크로 저장"""
        if not events:
            return False
        
        # 이름이 지정되지 않은 경우 타임스탬프 사용
        if name is None:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            name = f"macro_{timestamp}"
        
        # 파일 확장자 추가
        if not name.endswith(".json"):
            name += ".json"
        
        file_path = os.path.join(self.storage_dir, name)
        
        # 매크로 데이터 구성
        macro_data = {
            "name": name,
            "created_at": datetime.now().isoformat(),
            "events": events
        }
        
        # JSON 파일로 저장
        try:
            with open(file_path, 'w') as f:
                json.dump(macro_data, f, indent=2)
            
            self.current_macro = macro_data
            self.current_macro_name = name
            return True
        except Exception as e:
            print(f"매크로 저장 중 오류 발생: {e}")
            return False
    
    def load_macro(self, name):
        """매크로 불러오기"""
        # 파일 확장자 확인
        if not name.endswith(".json"):
            name += ".json"
        
        file_path = os.path.join(self.storage_dir, name)
        
        if not os.path.exists(file_path):
            print(f"매크로 파일을 찾을 수 없습니다: {name}")
            return None
        
        try:
            with open(file_path, 'r') as f:
                macro_data = json.load(f)
            
            self.current_macro = macro_data
            self.current_macro_name = name
            return macro_data["events"]
        except Exception as e:
            print(f"매크로 로드 중 오류 발생: {e}")
            return None
    
    def list_macros(self):
        """저장된 매크로 목록 반환"""
        self.ensure_storage_dir()
        macro_files = [f for f in os.listdir(self.storage_dir) if f.endswith(".json")]
        return macro_files
    
    def delete_macro(self, name):
        """매크로 삭제"""
        if not name.endswith(".json"):
            name += ".json"
        
        file_path = os.path.join(self.storage_dir, name)
        
        if not os.path.exists(file_path):
            print(f"매크로 파일을 찾을 수 없습니다: {name}")
            return False
        
        try:
            os.remove(file_path)
            if self.current_macro_name == name:
                self.current_macro = None
                self.current_macro_name = None
            return True
        except Exception as e:
            print(f"매크로 삭제 중 오류 발생: {e}")
            return False
    
    def update_macro(self, events, name):
        """매크로 업데이트"""
        if not name.endswith(".json"):
            name += ".json"
            
        return self.save_macro(events, name) 