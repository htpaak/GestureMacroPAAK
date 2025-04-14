import json
import os
import shutil
from datetime import datetime

APP_NAME = "MacroCraft" # 프로그램 이름 정의

class MacroStorage:
    def __init__(self, filename="macros.json"):
        # 저장 경로 설정: %LOCALAPPDATA%/MacroCraft/macros.json
        local_appdata = os.getenv('LOCALAPPDATA')
        if not local_appdata:
            # 환경 변수가 없는 경우 현재 디렉토리에 저장 (Fallback)
            print("경고: LOCALAPPDATA 환경 변수를 찾을 수 없습니다. 현재 디렉토리에 저장합니다.")
            self.app_data_dir = os.path.abspath(".") # 현재 디렉토리
        else:
            self.app_data_dir = os.path.join(local_appdata, APP_NAME)

        self.storage_file = os.path.join(self.app_data_dir, filename)
        print(f"매크로 저장 경로: {self.storage_file}") # 경로 확인 로그

        # 앱 데이터 디렉토리 생성
        try:
            os.makedirs(self.app_data_dir, exist_ok=True)
        except OSError as e:
            print(f"오류: 앱 데이터 디렉토리 생성 실패 ({self.app_data_dir}): {e}")
            # 생성 실패 시 현재 디렉토리에 저장하도록 경로 재설정 (Fallback)
            self.app_data_dir = os.path.abspath(".")
            self.storage_file = os.path.join(self.app_data_dir, filename)
            print(f"Fallback: 현재 디렉토리에 저장합니다: {self.storage_file}")


        self.macros = {}  # 모든 매크로 데이터를 메모리에 로드하여 관리
        self.ensure_storage_file_and_migrate() # 파일 확인 및 마이그레이션
        self.load_all_macros() # 메모리로 로드

    def ensure_storage_file_and_migrate(self):
        """저장 파일 확인 및 마이그레이션 로직 실행"""
        # 저장 파일은 app_data_dir 아래에 있는지 확인
        if not os.path.exists(self.storage_file):
            print(f"'{self.storage_file}' 파일이 없습니다. 기존 데이터 마이그레이션을 시도합니다.")
            # 마이그레이션은 현재 작업 디렉토리 기준의 기존 데이터를 사용
            migrated = self._migrate_old_format()
            if not migrated:
                # 마이그레이션 실패 또는 기존 데이터 없음 -> 새 경로에 빈 파일 생성
                print(f"기존 데이터가 없거나 마이그레이션 실패. '{self.storage_file}'에 빈 파일을 생성합니다.")
                try:
                    with open(self.storage_file, 'w', encoding='utf-8') as f:
                        json.dump({}, f, ensure_ascii=False, indent=4)
                except Exception as e:
                    print(f"오류: '{self.storage_file}' 생성 실패: {e}")


    def _migrate_old_format(self):
        """기존 macros 폴더 및 gesture_mappings.json 에서 데이터 마이그레이션"""
        # 기존 데이터는 현재 작업 디렉토리에서 찾음
        current_working_dir = os.path.abspath(".")
        old_mapping_file = os.path.join(current_working_dir, "gesture_mappings.json")
        old_macros_dir = os.path.join(current_working_dir, "macros")
        new_macros_data = {}
        migrated_something = False

        print(f"마이그레이션: 현재 작업 디렉토리({current_working_dir})에서 기존 데이터 확인 중...")

        if not os.path.exists(old_mapping_file) or not os.path.isdir(old_macros_dir):
            print("현재 작업 디렉토리에서 기존 매핑 파일 또는 매크로 폴더를 찾을 수 없어 마이그레이션을 건너니다.")
            return False

        try:
            print(f"'{old_mapping_file}' 파일 읽기 시도...")
            with open(old_mapping_file, 'r', encoding='utf-8') as f:
                old_mappings = json.load(f)

            print(f"기존 매핑 {len(old_mappings)}개 발견. '{old_macros_dir}'에서 개별 매크로 파일 로드 시도...")
            for gesture, macro_filename in old_mappings.items():
                if "_temp.json" in macro_filename:
                    print(f"  - 임시 제스처 건너 ({gesture} -> {macro_filename})")
                    continue

                macro_filepath = os.path.join(old_macros_dir, macro_filename)
                if os.path.exists(macro_filepath):
                    try:
                        with open(macro_filepath, 'r', encoding='utf-8') as mf:
                            events = json.load(mf)
                        if isinstance(events, list):
                            new_macros_data[gesture] = events
                            print(f"  - 성공: {gesture} -> {macro_filename} ({len(events)}개 이벤트)")
                            migrated_something = True
                        else:
                             print(f"  - 실패 (유효하지 않은 데이터): {gesture} -> {macro_filename}")
                    except Exception as e:
                        print(f"  - 실패 (파일 읽기 오류: {e}): {gesture} -> {macro_filename}")
                else:
                    print(f"  - 실패 (파일 없음): {gesture} -> {macro_filename}")

            # 마이그레이션된 데이터 저장 (새로운 AppData 경로에 저장)
            if migrated_something:
                print(f"총 {len(new_macros_data)}개의 매크로 마이그레이션 완료. '{self.storage_file}'에 저장합니다.")
                try:
                    with open(self.storage_file, 'w', encoding='utf-8') as f:
                        json.dump(new_macros_data, f, ensure_ascii=False, indent=4)
                except Exception as e:
                     print(f"오류: 마이그레이션된 데이터 저장 실패 ({self.storage_file}): {e}")
                     return False # 저장 실패 시 마이그레이션 실패 처리

                # 마이그레이션 후 기존 파일/폴더 백업 (현재 작업 디렉토리 대상)
                backup_dir_name = "macros_backup_" + datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_dir_path = os.path.join(current_working_dir, backup_dir_name)
                backup_mapping_path = os.path.join(current_working_dir, f"{os.path.basename(old_mapping_file)}.bak")
                print(f"현재 작업 디렉토리의 기존 매크로 데이터 백업 중 -> '{backup_dir_path}', '{backup_mapping_path}'")
                try:
                    # os.rename은 다른 드라이브 간 이동이 안될 수 있으므로 shutil.move 사용 고려
                    if os.path.exists(old_macros_dir):
                         shutil.move(old_macros_dir, backup_dir_path) # 폴더 이동
                    if os.path.exists(old_mapping_file):
                         os.rename(old_mapping_file, backup_mapping_path) # 파일 이름 변경
                    print("백업 완료.")
                except Exception as e:
                    print(f"백업 중 오류 발생: {e}")

                return True
            else:
                print("마이그레이션할 유효한 데이터가 없습니다.")
                return False

        except Exception as e:
            print(f"마이그레이션 중 심각한 오류 발생: {e}")
            return False

    def load_all_macros(self):
        """파일에서 모든 매크로 데이터를 메모리로 로드"""
        try:
            with open(self.storage_file, 'r', encoding='utf-8') as f:
                self.macros = json.load(f)
            print(f"'{self.storage_file}'에서 매크로 {len(self.macros)}개 로드 완료.")
        except FileNotFoundError:
            print(f"'{self.storage_file}' 파일 없음. 빈 매크로 데이터 사용.")
            self.macros = {}
        except json.JSONDecodeError:
            print(f"'{self.storage_file}' 파일 JSON 파싱 오류. 빈 매크로 데이터 사용.")
            self.macros = {}
        except Exception as e:
            print(f"매크로 로드 중 예상치 못한 오류: {e}")
            self.macros = {}

    def _save_all_macros_to_file(self):
        """메모리의 모든 매크로 데이터를 파일에 저장"""
        try:
            with open(self.storage_file, 'w', encoding='utf-8') as f:
                json.dump(self.macros, f, ensure_ascii=False, indent=4)
            return True
        except Exception as e:
            print(f"매크로 저장 오류 ({self.storage_file}): {e}")
            return False

    def save_macro(self, events, gesture_key):
        """특정 제스처 키에 대한 매크로 이벤트 리스트를 저장"""
        if not isinstance(events, list):
             print(f"저장하려는 이벤트 데이터가 리스트가 아닙니다 (타입: {type(events)}). 저장하지 않습니다.")
             return False
        print(f"매크로 저장 요청: 제스처='{gesture_key}', 이벤트 수={len(events)}")
        self.macros[gesture_key] = events
        return self._save_all_macros_to_file()

    def load_macro(self, gesture_key):
        """특정 제스처 키에 대한 매크로 이벤트 리스트를 반환"""
        return self.macros.get(gesture_key, None)

    def list_macros(self):
        """저장된 모든 제스처 키(매크로 이름) 목록 반환"""
        return list(self.macros.keys())

    def delete_macro(self, gesture_key):
        """특정 제스처 키의 매크로 삭제"""
        if gesture_key in self.macros:
            del self.macros[gesture_key]
            print(f"매크로 삭제 완료: {gesture_key}")
            return self._save_all_macros_to_file()
        else:
            print(f"삭제할 매크로를 찾을 수 없습니다: {gesture_key}")
            return False

    def get_all_mappings(self):
        """모든 제스처와 매크로 이벤트 데이터를 담은 딕셔너리 반환"""
        import copy
        return copy.deepcopy(self.macros)

    # _make_safe_filename 메서드는 더 이상 필요 없음
    # update_macro 메서드는 save_macro 와 동일하게 동작하므로 별도 구현 불필요 