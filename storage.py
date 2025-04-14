import json
import os
import shutil
from datetime import datetime
import copy # deepcopy를 위해 추가

APP_NAME = "MacroCraft" # 프로그램 이름 정의

class MacroStorage:
    def __init__(self, base_dir_name=APP_NAME, order_file="gesture_order.json"):
        """매크로 스토리지 초기화 (개별 파일 + 순서 파일 방식)"""
        # 저장 경로 설정: %LOCALAPPDATA%/MacroCraft
        local_appdata = os.getenv('LOCALAPPDATA')
        if not local_appdata:
            print("경고: LOCALAPPDATA 환경 변수를 찾을 수 없습니다. 현재 디렉토리에 저장합니다.")
            self.app_data_dir = os.path.abspath(base_dir_name) # Fallback
        else:
            self.app_data_dir = os.path.join(local_appdata, base_dir_name)

        self.order_file_path = os.path.join(self.app_data_dir, order_file)
        print(f"매크로 저장 디렉토리: {self.app_data_dir}")
        print(f"제스처 순서 파일: {self.order_file_path}")

        # 앱 데이터 디렉토리 생성
        try:
            os.makedirs(self.app_data_dir, exist_ok=True)
        except OSError as e:
            print(f"오류: 앱 데이터 디렉토리 생성 실패 ({self.app_data_dir}): {e}")
            # 생성 실패 시 추가 처리 필요? (예: 예외 발생)

        # 단일 파일 관련 로직 제거됨 (self.macros, 마이그레이션 등)

    def get_macro_filepath(self, gesture_key):
        """제스처 키에 해당하는 .json 파일의 전체 경로 반환"""
        base_name = os.path.splitext(str(gesture_key))[0] # Ensure key is string
        filename = f"{base_name}.json"
        return os.path.join(self.app_data_dir, filename)

    def save_macro(self, events, gesture_key):
        """특정 제스처 키에 대한 매크로 이벤트를 개별 .json 파일에 저장"""
        gesture_key_str = str(gesture_key) # Ensure key is string
        if not isinstance(events, list):
            print(f"저장하려는 이벤트 데이터가 리스트가 아닙니다 (키: {gesture_key_str}, 타입: {type(events)}). 저장하지 않습니다.")
            return False

        filepath = self.get_macro_filepath(gesture_key_str)
        print(f"매크로 저장 시도: 키='{gesture_key_str}', 이벤트 수={len(events)}, 파일='{filepath}'")

        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(events, f, ensure_ascii=False, indent=4)

            # 저장 성공 시 순서 파일에도 추가 (기존 순서 유지하면서)
            current_order = self.load_gesture_order()
            if gesture_key_str not in current_order:
                current_order.append(gesture_key_str)
                self.save_gesture_order(current_order)
            print(f"매크로 저장 성공: {filepath}")
            return True
        except Exception as e:
            print(f"매크로 저장 오류 ({filepath}): {e}")
            return False

    def load_macro(self, gesture_key):
        """특정 제스처 키에 해당하는 .json 파일에서 매크로 이벤트 로드"""
        gesture_key_str = str(gesture_key) # Ensure key is string
        filepath = self.get_macro_filepath(gesture_key_str)
        if not os.path.exists(filepath):
            # print(f"매크로 파일 없음: {filepath}") # 로그 레벨 조절 필요
            return None # 파일 없으면 None 반환

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            if not isinstance(data, list):
                 print(f"경고: 매크로 데이터 형식이 잘못됨 ({filepath}): {type(data)}")
                 return None # 잘못된 형식은 None 반환
            # print(f"매크로 로드 성공: {filepath}") # 성공 로그 필요 시 활성화
            return data
        except json.JSONDecodeError as e:
            print(f"오류: JSON 파싱 오류 ({filepath}): {e}")
            return None
        except Exception as e:
            print(f"매크로 로드 중 오류 발생 ({filepath}): {e}")
            return None

    def delete_macro(self, gesture_key):
        """특정 제스처 키의 .json 파일 삭제 및 순서 파일 업데이트"""
        gesture_key_str = str(gesture_key) # Ensure key is string
        filepath = self.get_macro_filepath(gesture_key_str)
        deleted = False
        if os.path.exists(filepath):
            try:
                os.remove(filepath)
                print(f"매크로 파일 삭제 성공: {filepath}")
                deleted = True
            except Exception as e:
                 print(f"매크로 파일 삭제 오류 ({filepath}): {e}")
                 # 파일 삭제 실패해도 순서에서는 제거 시도? -> 일단 실패 시 순서 유지

        # 순서 파일 업데이트 (파일 삭제 성공 여부와 관계없이 시도 가능, 혹은 성공 시에만?)
        # -> 파일 삭제 성공 시에만 순서에서 제거하는 것이 안전
        if deleted:
            current_order = self.load_gesture_order()
            if gesture_key_str in current_order:
                current_order.remove(gesture_key_str)
                if not self.save_gesture_order(current_order):
                    print(f"경고: 매크로 삭제 후 순서 파일 업데이트 실패 ({gesture_key_str})" )
                    # 순서 저장 실패 시 복구 로직 필요?

        return deleted # 파일 삭제 성공 여부 반환

    def load_gesture_order(self):
        """저장된 제스처 순서를 파일에서 로드"""
        if not os.path.exists(self.order_file_path):
            return [] # 파일 없으면 빈 리스트

        try:
            with open(self.order_file_path, 'r', encoding='utf-8') as f:
                ordered_keys = json.load(f)
            if isinstance(ordered_keys, list):
                # Ensure all keys are strings
                return [str(key) for key in ordered_keys]
            else:
                print(f"경고: 제스처 순서 파일 형식이 잘못됨 ({self.order_file_path}). 리스트가 아님.")
                return []
        except json.JSONDecodeError:
            print(f"오류: 제스처 순서 파일 JSON 파싱 실패 ({self.order_file_path}).")
            return []
        except Exception as e:
            print(f"제스처 순서 로드 중 오류 발생: {e}")
            return []

    def save_gesture_order(self, ordered_keys):
        """현재 제스처 순서를 파일에 저장"""
        if not isinstance(ordered_keys, list):
             print(f"오류: 저장하려는 순서 데이터가 리스트가 아님 ({type(ordered_keys)})" )
             return False
        # Ensure all keys are strings before saving
        keys_to_save = [str(key) for key in ordered_keys]
        try:
            with open(self.order_file_path, 'w', encoding='utf-8') as f:
                json.dump(keys_to_save, f, ensure_ascii=False, indent=4)
            # print(f"제스처 순서 저장 완료: {self.order_file_path}") # 성공 로그 필요 시 활성화
            return True
        except Exception as e:
            print(f"제스처 순서 저장 중 오류 발생 ({self.order_file_path}): {e}")
            return False

    def get_macro_keys(self):
        """저장 디렉토리에서 실제 매크로 파일(.json)들의 키 목록 반환"""
        try:
            if not os.path.exists(self.app_data_dir):
                return []
            # .json 확장자를 가진 파일들의 이름(확장자 제외)만 리스트로 반환
            # gesture_order.json 파일과 이전 방식의 macros.json 파일은 제외
            order_file_basename = os.path.basename(self.order_file_path)
            macro_keys = [
                str(os.path.splitext(f)[0]) for f in os.listdir(self.app_data_dir) # Ensure keys are strings
                if f.lower().endswith('.json')
                   and f != order_file_basename # 순서 파일 제외
                   and f.lower() != 'macros.json' # 이전 단일 파일 제외
                   and os.path.isfile(os.path.join(self.app_data_dir, f))
            ]
            print(f"[DEBUG storage.get_macro_keys] Found keys: {macro_keys}") # DEBUG
            return macro_keys
        except Exception as e:
            print(f"매크로 키 목록 가져오기 중 오류 발생: {e}")
            return []

    def get_all_mappings(self):
        """저장된 순서를 반영하여 모든 제스처 키 목록 반환 (값은 키 자체인 딕셔너리)"""
        ordered_keys_from_file = self.load_gesture_order()
        actual_macro_keys = self.get_macro_keys()
        actual_macro_set = set(actual_macro_keys)
        print(f"[DEBUG storage.get_all_mappings] Loaded order: {ordered_keys_from_file}") # DEBUG
        print(f"[DEBUG storage.get_all_mappings] Actual keys: {actual_macro_keys}") # DEBUG

        final_ordered_keys = []
        keys_processed = set()
        needs_resave = False

        # 1. 순서 파일 기준으로 실제 존재하는 키 추가
        for key in ordered_keys_from_file:
            key_str = str(key) # Ensure string
            if key_str in actual_macro_set:
                if key_str not in keys_processed:
                    final_ordered_keys.append(key_str)
                    keys_processed.add(key_str)
            else:
                # 순서 파일에는 있지만 실제 파일은 없는 경우 -> 순서 파일 업데이트 필요
                print(f"경고: 순서 파일의 제스처 '{key_str}' 매크로 파일이 없어 제외합니다.")
                needs_resave = True

        # 2. 순서 파일에는 없지만 실제 파일이 있는 키 추가 (정렬하여 추가)
        missing_keys = sorted([key for key in actual_macro_keys if key not in keys_processed])
        if missing_keys:
            print(f"경고: 순서 파일에 없는 제스처들을 목록 끝에 추가합니다: {missing_keys}")
            final_ordered_keys.extend(missing_keys)
            needs_resave = True # 추가된 키가 있으므로 순서 파일 업데이트 필요

        # 3. 최종 순서가 로드된 순서와 다르거나, 재저장 필요 플래그가 설정된 경우 순서 파일 업데이트
        # Ensure comparison uses string keys
        if needs_resave or final_ordered_keys != [str(k) for k in ordered_keys_from_file]:
             print(f"순서 파일 업데이트 필요. 새 순서 저장: {final_ordered_keys}")
             self.save_gesture_order(final_ordered_keys)

        # 값으로 키 자체를 사용하는 매핑 반환
        final_mapping = {key: key for key in final_ordered_keys}
        print(f"[DEBUG storage.get_all_mappings] Returning mapping keys: {list(final_mapping.keys())}") # DEBUG
        return final_mapping

    def list_macros(self):
        """저장된 모든 제스처 키(매크로 이름) 목록 반환"""
        return list(self.macros.keys())

    def get_full_path(self, macro_name):
        """매크로 파일의 전체 경로 반환"""
        # 파일 확장자가 없으면 .json 추가
        if not macro_name.lower().endswith('.json'):
            macro_name = f"{macro_name}.json"

        return os.path.join(self.app_data_dir, macro_name)

    def get_macro_list(self):
        """저장된 매크로 목록(파일 이름에서 확장자 제외한 키) 가져오기 (순서 정보 미반영)"""
        try:
            if not os.path.exists(self.app_data_dir):
                return []
            # 디렉토리 내의 .json 파일 이름만 추출 (.json 제외)
            macro_keys = [os.path.splitext(f)[0] for f in os.listdir(self.app_data_dir)
                         if f.lower().endswith('.json') and os.path.isfile(os.path.join(self.app_data_dir, f))]
            return macro_keys
        except Exception as e:
            print(f"매크로 목록(파일) 가져오기 중 오류 발생: {e}")
            return []

    # _make_safe_filename 메서드는 더 이상 필요 없음
    # update_macro 메서드는 save_macro 와 동일하게 동작하므로 별도 구현 불필요 