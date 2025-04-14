import os
import json

class MacroStorage:
    def __init__(self, base_path="macros", order_file="gesture_order.json"):
        """매크로 스토리지 초기화"""
        self.base_path = base_path
        # 순서 파일 경로 추가 (base_path와 동일한 디렉토리 사용)
        order_dir = os.path.dirname(self.base_path) if os.path.splitext(self.base_path)[1] else self.base_path
        self.order_file_path = os.path.join(order_dir, order_file)
        
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
                # print(f"매크로 파일을 찾을 수 없음: {full_path}") # 너무 빈번한 로그일 수 있어 주석 처리
                return None # 파일을 찾을 수 없으면 None 반환 (빈 리스트와 구분)
                
            # 파일 읽기
            with open(full_path, 'r') as f:
                try:
                    # JSON 파일 읽기
                    data = json.load(f)
                    # print(f"매크로 파일 불러오기 성공: {full_path}") # 성공 로그는 필요 시 활성화
                    
                    # 데이터 유효성 검사
                    if not isinstance(data, list):
                        print(f"경고: 매크로 데이터가 리스트 형식이 아님 ({full_path}): {type(data)}")
                        # 이전 버전 호환성 시도 (딕셔너리 안에 events 키)
                        if isinstance(data, dict) and 'events' in data and isinstance(data['events'], list):
                            print("이벤트 키에서 매크로 데이터 사용 시도")
                            return data['events']
                        return None # 유효하지 않은 데이터는 None 반환
                    
                    return data
                except json.JSONDecodeError as e:
                    print(f"오류: JSON 파싱 오류 ({full_path}): {e}")
                    return None # 파싱 실패 시 None 반환
        except Exception as e:
            print(f"매크로 로드 중 오류 발생 ({macro_name}): {e}")
            return None # 로드 중 오류 발생 시 None 반환
            
    def delete_macro(self, macro_name):
        """매크로 파일 삭제"""
        try:
            # 파일 경로 설정
            full_path = self.get_full_path(macro_name)
            
            # 파일이 존재하면 삭제
            if os.path.exists(full_path):
                os.remove(full_path)
                print(f"매크로 파일 삭제 성공: {full_path}")
                # 순서 파일에서도 해당 키 제거
                current_order = self.load_gesture_order()
                if macro_name in current_order:
                    current_order.remove(macro_name)
                    self.save_gesture_order(current_order)
                return True
                
            print(f"삭제할 매크로 파일을 찾을 수 없음: {full_path}")
            return False
        except Exception as e:
            print(f"매크로 삭제 중 오류 발생: {e}")
            return False
    
    def get_macro_list(self):
        """저장된 매크로 목록(파일 이름에서 확장자 제외한 키) 가져오기 (순서 정보 미반영)"""
        try:
            if not os.path.exists(self.base_path):
                return []
            # 디렉토리 내의 .json 파일 이름만 추출 (.json 제외)
            macro_keys = [os.path.splitext(f)[0] for f in os.listdir(self.base_path)
                         if f.lower().endswith('.json') and os.path.isfile(os.path.join(self.base_path, f))]
            return macro_keys
        except Exception as e:
            print(f"매크로 목록(파일) 가져오기 중 오류 발생: {e}")
            return []

    def load_gesture_order(self):
        """저장된 제스처 순서를 파일에서 로드"""
        try:
            if os.path.exists(self.order_file_path):
                with open(self.order_file_path, 'r') as f:
                    ordered_keys = json.load(f)
                    if isinstance(ordered_keys, list):
                        # print(f"제스처 순서 로드 완료: {self.order_file_path}") # 성공 로그는 필요 시 활성화
                        return ordered_keys
                    else:
                        print(f"경고: 제스처 순서 파일 형식이 잘못되었습니다 (리스트가 아님). {self.order_file_path}")
                        return []
            else:
                # print(f"제스처 순서 파일 없음: {self.order_file_path}") # 파일 없는 것은 일반적일 수 있음
                return [] # 파일 없으면 빈 리스트
        except json.JSONDecodeError:
            print(f"오류: 제스처 순서 파일 JSON 파싱 실패. {self.order_file_path}")
            return [] # 파싱 실패 시 빈 리스트
        except Exception as e:
            print(f"제스처 순서 로드 중 오류 발생: {e}")
            return []

    def save_gesture_order(self, ordered_keys):
        """현재 제스처 순서를 파일에 저장"""
        try:
            # 순서 파일 저장
            with open(self.order_file_path, 'w') as f:
                json.dump(ordered_keys, f, indent=2)
            # print(f"제스처 순서 저장 완료: {self.order_file_path}") # 성공 로그는 필요 시 활성화
            return True
        except Exception as e:
            print(f"제스처 순서 저장 중 오류 발생: {e}")
            return False

    def get_all_mappings(self):
        """저장된 순서를 반영하여 모든 제스처-매크로 파일 이름 매핑 딕셔너리 반환"""
        ordered_keys = self.load_gesture_order()
        all_macro_keys = self.get_macro_list() # 실제 존재하는 매크로 키 목록
        existing_macro_set = set(all_macro_keys)

        final_ordered_mappings = {}
        needs_resave = False

        # 1. 저장된 순서에 있는 키 중 실제 매크로 파일이 존재하는 것만 추가
        valid_ordered_keys_in_file = []
        for key in ordered_keys:
            if key in existing_macro_set:
                final_ordered_mappings[key] = f"{key}.json" # 값은 파일 이름
                valid_ordered_keys_in_file.append(key)
            else:
                print(f"경고: 저장된 순서의 제스처 '{key}'에 해당하는 매크로 파일이 없어 제외합니다.")
                needs_resave = True # 누락된 키가 있었으므로 순서 파일 재저장 필요

        # 2. 순서 파일에는 없지만 실제 매크로 파일이 존재하는 키들을 뒤에 추가 (파일 시스템 순서대로)
        missing_keys = [key for key in all_macro_keys if key not in final_ordered_mappings]
        if missing_keys:
            print(f"경고: 순서 파일에 없는 제스처들을 목록 끝에 추가합니다: {missing_keys}")
            for key in missing_keys:
                final_ordered_mappings[key] = f"{key}.json"
            needs_resave = True # 추가된 키가 있으므로 순서 파일 재저장 필요

        # 3. 순서 변경이 감지되었으면 재저장
        # (ordered_keys와 valid_ordered_keys_in_file의 길이가 다른 경우 포함)
        if needs_resave:
            final_ordered_keys = list(final_ordered_mappings.keys())
            print(f"순서 파일 업데이트 필요. 새 순서 저장: {final_ordered_keys}")
            self.save_gesture_order(final_ordered_keys)

        # print(f"최종 매핑 순서 ({len(final_ordered_mappings)}개): {list(final_ordered_mappings.keys())}) # 디버깅 시 활성화
        return final_ordered_mappings 