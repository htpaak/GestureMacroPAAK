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
            
            # 제스처만 저장 (매크로 없이)
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
        # 매크로 이름 생성 (제스처 기반)
        macro_name = f"gesture_{gesture}.json"
        
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
            
            # 매크로 로드
            events = self.storage.load_macro(macro_name)
            if events:
                # 매크로 플레이어로 매크로 실행
                self.macro_player.play_macro(events, 1)  # 1회 실행
                return True
            else:
                print(f"Failed to load macro: {macro_name}")
        else:
            print(f"No macro mapping for gesture: {gesture}")
            
        return False
        
    def save_mappings(self):
        """제스처 매핑 저장"""
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(self.gesture_mappings, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving gesture mappings: {e}")
            return False
            
    def load_mappings(self):
        """제스처-매크로 매핑 불러오기"""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r') as f:
                    self.gesture_mappings = json.load(f)
                print(f"제스처 매핑 로드 완료: {len(self.gesture_mappings)} 개")
                
                # 구 형식의 제스처 이름 변환 (RDLDR → →↓←↓→)
                self._convert_old_gesture_names()
            else:
                print("제스처 매핑 파일이 없음, 새로 생성됩니다.")
                self.gesture_mappings = {}
        except Exception as e:
            print(f"제스처 매핑 로드 오류: {e}")
            self.gesture_mappings = {}
            
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
        temp_macro_name = f"gesture_{gesture}_temp.json"
        
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
                
            return True
        
        print("제스처 저장 실패!")  # 디버깅 로그 추가
        return False 