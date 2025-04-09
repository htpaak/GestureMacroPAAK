import json
import os
from gesture_recognizer import GestureRecognizer
from global_gesture_listener import GlobalGestureListener
from gesture_canvas import GestureCanvas
import tkinter as tk
from tkinter import messagebox

class GestureManager:
    def __init__(self, macro_player, storage, recorder=None):
        """제스처 관리자 초기화"""
        self.macro_player = macro_player
        self.storage = storage
        self.recorder = recorder
        
        # 제스처 -> 매크로 매핑
        self.gesture_mappings = {}
        
        # 콜백 함수
        self.on_update_gesture_list = None
        self.on_macro_record_request = None
        self.gui_callback = None  # GUI 참조 추가
        
        # 임시 제스처 저장
        self.temp_gesture = None
        
        # 녹화 상태
        self.recording_mode = False
        
        # 제스처 인식기 초기화
        self.gesture_recognizer = GestureRecognizer()
        
        # 전역 제스처 리스너 초기화
        self.gesture_listener = GlobalGestureListener()
        
        # 콜백 설정
        self.gesture_listener.set_callbacks(
            self.on_gesture_started,
            self.on_gesture_moved,
            self.on_gesture_ended
        )
        print(f"콜백 설정 완료: {self.on_gesture_started}, {self.on_gesture_moved}, {self.on_gesture_ended}")
        
        # 제스처 시각화 캔버스
        self.gesture_canvas = None
        self.canvas_window = None
        
        # 설정 파일 경로
        self.settings_file = "gesture_mappings.json"
        
        # 제스처 매핑 로드
        self.load_mappings()
        
    def start(self):
        """제스처 인식 시작"""
        self.gesture_listener.start()
        
    def stop(self):
        """제스처 인식 중지"""
        self.gesture_listener.stop()
        
    def on_gesture_started(self, point, modifiers):
        """제스처 시작 콜백"""
        self.gesture_recognizer.start_recording(point, modifiers)
        
        # 제스처 시각화 캔버스가 있는 경우 점 추가
        if self.gesture_canvas:
            self.gesture_canvas.create_oval(
                point[0]-3, point[1]-3, point[0]+3, point[1]+3, 
                fill="blue", outline="blue", tags="gesture"
            )
        
    def on_gesture_moved(self, point):
        """제스처 이동 콜백"""
        self.gesture_recognizer.add_point(point)
        
        # 제스처 시각화 캔버스가 있는 경우 선 추가
        if self.gesture_canvas and len(self.gesture_recognizer.points) > 1:
            prev_point = self.gesture_recognizer.points[-2]
            self.gesture_canvas.create_line(
                prev_point[0], prev_point[1], point[0], point[1],
                fill="red", width=2, tags="gesture"
            )
        
    def on_gesture_ended(self):
        """제스처 종료 콜백"""
        # 제스처 인식
        gesture = self.gesture_recognizer.stop_recording()
        print(f"제스처 인식 완료: {gesture}")  # 디버깅 로그 추가
        
        # 캔버스 창 닫기
        if self.canvas_window:
            self.canvas_window.destroy()
            self.canvas_window = None
            self.gesture_canvas = None
        
        # 너무 짧은 제스처이거나 취소된 경우는 저장하지 않음
        if "tooShort" in gesture or "unknown" in gesture:
            print("제스처가 너무 짧거나 취소됨: 저장하지 않음")
            self.recording_mode = False
            return
        
        # 녹화 모드인 경우 제스처 임시 저장
        if self.recording_mode:
            self.temp_gesture = gesture
            print(f"제스처 임시 저장: {self.temp_gesture}")  # 디버깅 로그 추가
            
            # 녹화 종료
            self.recording_mode = False
            
            # GUI에서 편집 모드가 활성화된 경우 편집 완료 콜백 호출
            if self.gui_callback and hasattr(self.gui_callback, 'editing_gesture') and self.gui_callback.editing_gesture:
                print(f"제스처 편집 완료 콜백 호출: {gesture}")
                self.gui_callback.on_gesture_edit_complete(gesture)
                return
            
            # 일반 녹화 모드: 제스처만 저장 (매크로 없이)
            self.save_gesture_only(gesture)
            
            return
        
        # 일반 모드인 경우 매크로 실행
        print(f"제스처 실행 시도: {gesture}")  # 디버깅 로그 추가
        self.execute_gesture_action(gesture)
        
    def start_gesture_recording(self):
        """새 제스처 녹화 시작"""
        self.recording_mode = True
        print("제스처 녹화 모드 시작")  # 디버깅 로그 추가
        
        # 제스처 시각화 창 생성
        self.create_gesture_canvas()
        
    def create_gesture_canvas(self):
        """제스처 시각화를 위한 캔버스 창 생성"""
        # 이미 열려있는 창이 있으면 닫기
        if self.canvas_window:
            self.canvas_window.destroy()
            self.canvas_window = None
            self.gesture_canvas = None
            
        # 새 캔버스 생성 (GestureCanvas 클래스 사용)
        canvas_manager = GestureCanvas(on_cancel=self.cancel_recording)
        self.gesture_canvas = canvas_manager.create()
        self.canvas_window = canvas_manager.window
        
    def cancel_recording(self):
        """제스처 녹화 취소"""
        print("제스처 녹화 취소됨")
        self.recording_mode = False
        self.temp_gesture = None
        
        if self.canvas_window:
            self.canvas_window.destroy()
            self.canvas_window = None
            self.gesture_canvas = None
            
        # 제스처 인식기 초기화
        self.gesture_recognizer.is_recording = False
        self.gesture_recognizer.points = []
        self.gesture_recognizer.modifiers = 0
        
    def save_macro_for_gesture(self, gesture, events):
        """제스처에 매크로 저장"""
        # 매크로 이름 생성 (제스처 기반) - 파일명으로 사용할 수 있게 가공
        safe_gesture = gesture.replace('→', '_RIGHT_').replace('↓', '_DOWN_').replace('←', '_LEFT_').replace('↑', '_UP_')
        macro_name = f"gesture_{safe_gesture}.json"
        
        print(f"매크로 저장: 제스처 '{gesture}' -> 파일명 '{macro_name}'")
        
        # 기존 매핑 확인 및 임시 파일 처리
        if gesture in self.gesture_mappings:
            old_macro_name = self.gesture_mappings[gesture]
            print(f"기존 매핑 발견: {gesture} -> {old_macro_name}")
            
            # 임시 파일인 경우 삭제
            if "_temp.json" in old_macro_name:
                old_path = os.path.join("macros", old_macro_name)
                if os.path.exists(old_path):
                    try:
                        os.remove(old_path)
                        print(f"임시 파일 삭제됨: {old_path}")
                    except Exception as e:
                        print(f"임시 파일 삭제 실패: {e}")
        
        # 매크로 저장
        success = self.storage.save_macro(events, macro_name)
        
        if success:
            # 제스처-매크로 매핑 추가
            self.gesture_mappings[gesture] = macro_name
            self.save_mappings()
            
            # 제스처 목록 업데이트 (콜백)
            if self.on_update_gesture_list:
                self.on_update_gesture_list()
                
            return True
        
        return False
        
    def remove_mapping(self, gesture):
        """제스처 매핑 제거"""
        if gesture in self.gesture_mappings:
            # 매크로 파일도 삭제
            macro_name = self.gesture_mappings[gesture]
            self.storage.delete_macro(macro_name)
            
            # 매핑 삭제
            del self.gesture_mappings[gesture]
            self.save_mappings()
            
            # 제스처 목록 업데이트 (콜백)
            if self.on_update_gesture_list:
                self.on_update_gesture_list()
                
            return True
        return False
    
    def get_mappings(self):
        """현재 제스처-매크로 매핑 반환"""
        return self.gesture_mappings.copy()
        
    def execute_gesture_action(self, gesture):
        """제스처에 해당하는 매크로 실행"""
        if gesture in self.gesture_mappings:
            macro_name = self.gesture_mappings[gesture]
            print(f"Executing macro '{macro_name}' for gesture: {gesture}")
            
            # 임시 매크로인지 미리 확인
            if "_temp.json" in macro_name:
                print(f"임시 매크로는 실행할 수 없습니다: {macro_name}")
                return False
            
            # 매크로 로드
            try:
                # 직접 매크로 파일 읽기
                import os
                import json
                full_path = os.path.join("macros", macro_name)
                
                # 파일이 존재하는지 확인
                if not os.path.exists(full_path):
                    # 대체 경로 시도
                    safe_gesture = gesture.replace('→', '_RIGHT_').replace('↓', '_DOWN_').replace('←', '_LEFT_').replace('↑', '_UP_')
                    alternative_path = os.path.join("macros", f"gesture_{safe_gesture}.json")
                    
                    if os.path.exists(alternative_path):
                        full_path = alternative_path
                    else:
                        print(f"매크로 파일을 찾을 수 없습니다: {macro_name}")
                        return False
                
                # 파일 읽기 - UTF-8 인코딩 사용
                with open(full_path, 'r', encoding='utf-8') as f:
                    events = json.load(f)
                
                # 템플릿 매크로 (빈 매크로)인 경우 실행하지 않음
                if not events or len(events) == 0:
                    print(f"매크로가 비어 있어 실행할 수 없습니다: {macro_name}")
                    return False
                    
                # 이벤트 목록이 유효한지 확인
                if not isinstance(events, list):
                    print(f"매크로 데이터가 유효하지 않음: {type(events)}")
                    return False
                    
                # 매크로 플레이어로 매크로 실행
                print(f"매크로 실행: {len(events)}개 이벤트")
                self.macro_player.play_macro(events, 1)  # 1회 실행
                return True
                
            except Exception as e:
                print(f"매크로 실행 중 오류 발생: {e}")
                return False
        else:
            print(f"No macro mapping for gesture: {gesture}")
            
        return False
        
    def save_mappings(self):
        """제스처-매크로 매핑 저장"""
        try:
            # 매핑을 정렬된 상태로 유지할 필요는 없으므로 그대로 저장
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.gesture_mappings, f, ensure_ascii=False, indent=4)
            print(f"제스처 매핑 저장됨: {len(self.gesture_mappings)}개")
            return True
        except Exception as e:
            print(f"제스처 매핑 저장 중 오류 발생: {e}")
            return False
            
    def load_mappings(self):
        """제스처-매크로 매핑 불러오기"""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    self.gesture_mappings = json.load(f)
                print(f"제스처 매핑 로드 완료: {len(self.gesture_mappings)} 개")
                
                # 구 형식의 제스처 이름 변환 (RDLDR → →↓←↓→)
                self._convert_old_gesture_names()
                
                # 매핑 검증 및 정리
                self._validate_and_clean_mappings()
            else:
                print("제스처 매핑 파일이 없음, 새로 생성됩니다.")
                self.gesture_mappings = {}
        except Exception as e:
            print(f"제스처 매핑 로드 오류: {e}")
            # 오류가 발생하면 기존 파일을 백업하고 새로 시작
            if os.path.exists(self.settings_file):
                try:
                    backup_file = f"{self.settings_file}.backup"
                    import shutil
                    shutil.copy2(self.settings_file, backup_file)
                    print(f"손상된 매핑 파일을 백업했습니다: {backup_file}")
                except Exception as backup_error:
                    print(f"매핑 파일 백업 중 오류: {backup_error}")
            self.gesture_mappings = {}
            
    def _validate_and_clean_mappings(self):
        """매핑 검증 및 정리 - 파일이 존재하지 않는 매핑 제거"""
        invalid_gestures = []
        for gesture, macro_name in self.gesture_mappings.items():
            # 매크로 파일 경로 확인
            full_path = os.path.join("macros", macro_name)
            if not os.path.exists(full_path):
                # 대체 경로 시도
                safe_gesture = gesture.replace('→', '_RIGHT_').replace('↓', '_DOWN_').replace('←', '_LEFT_').replace('↑', '_UP_')
                alternative_path = os.path.join("macros", f"gesture_{safe_gesture}.json")
                
                if not os.path.exists(alternative_path):
                    print(f"매크로 파일이 존재하지 않는 매핑 발견: {gesture} -> {macro_name}")
                    invalid_gestures.append(gesture)
                
        # 유효하지 않은 매핑 제거
        for gesture in invalid_gestures:
            print(f"유효하지 않은 매핑 제거: {gesture}")
            del self.gesture_mappings[gesture]
            
        # 변경된 경우 저장
        if invalid_gestures:
            print(f"{len(invalid_gestures)}개의 유효하지 않은 매핑 제거됨")
            self.save_mappings()
            
    def _convert_old_gesture_names(self):
        """구 형식의 제스처 이름을 새 형식으로 변환"""
        replacements = {
            'R': '→',
            'L': '←',
            'U': '↑',
            'D': '↓'
        }
        
        new_mappings = {}
        for gesture, macro_name in self.gesture_mappings.items():
            new_gesture = gesture
            for old, new in replacements.items():
                new_gesture = new_gesture.replace(old, new)
            new_mappings[new_gesture] = macro_name
            
        self.gesture_mappings = new_mappings
    
    # 콜백 설정
    def set_update_gesture_list_callback(self, callback):
        """제스처 목록 업데이트 콜백 설정"""
        print(f"제스처 목록 업데이트 콜백 설정: {callback}")  # 디버깅 로그 추가
        self.on_update_gesture_list = callback
        
    def set_macro_record_callback(self, callback):
        """매크로 녹화 요청 콜백 설정"""
        self.on_macro_record_request = callback
    
    def set_gui_callback(self, gui_instance):
        """GUI 인스턴스 참조 설정"""
        print(f"GUI 인스턴스 콜백 설정: {gui_instance}")  # 디버깅 로그 추가
        self.gui_callback = gui_instance

    def save_gesture_only(self, gesture):
        """제스처만 저장 (매크로는 나중에 연결)"""
        # 이미 존재하는 제스처인지 확인
        if gesture in self.gesture_mappings:
            # 이미 매크로가 연결된 제스처라면 경고
            messagebox.showwarning("이미 존재하는 제스처", 
                                 f"제스처 '{gesture}'는 이미 매크로와 연결되어 있습니다.\n"
                                 f"기존 제스처를 삭제하거나 다른 제스처를 녹화하세요.")
            return False
        
        # 매크로 없이 제스처만 저장 (임시로 빈 매크로 파일 생성)
        # 파일명으로 사용할 수 있게 가공
        safe_gesture = gesture.replace('→', '_RIGHT_').replace('↓', '_DOWN_').replace('←', '_LEFT_').replace('↑', '_UP_')
        temp_macro_name = f"gesture_{safe_gesture}_temp.json"
        
        print(f"템플릿 매크로 저장: 제스처 '{gesture}' -> 파일명 '{temp_macro_name}'")
        
        # 빈 이벤트 리스트로 임시 저장
        if self.storage.save_macro([], temp_macro_name):
            # 제스처-매크로 매핑 추가 (임시)
            self.gesture_mappings[gesture] = temp_macro_name
            print(f"제스처 매핑 추가: {gesture} -> {temp_macro_name}")  # 디버깅 로그 추가
            
            # 매핑 저장
            if self.save_mappings():
                print("제스처 매핑이 성공적으로 저장되었습니다.")  # 디버깅 로그 추가
            else:
                print("제스처 매핑 저장 실패!")  # 디버깅 로그 추가
            
            # 제스처 목록 업데이트 (콜백)
            if self.on_update_gesture_list:
                print("제스처 목록 업데이트 콜백 호출")  # 디버깅 로그 추가
                self.on_update_gesture_list()
            else:
                print("경고: 제스처 목록 업데이트 콜백이 설정되지 않았습니다.")  # 디버깅 로그 추가

            # 제스처가 저장되었다는 메시지 표시
            messagebox.showinfo("제스처 저장됨", f"제스처 '{gesture}'가 저장되었습니다. 매크로를 녹화하려면 '매크로 녹화 시작' 버튼을 클릭하세요.")
                
            return True
        
        print("제스처 저장 실패!")  # 디버깅 로그 추가
        return False 