import json
import os
from gesture_recognizer import GestureRecognizer
from global_gesture_listener import GlobalGestureListener
from gesture_canvas import GestureCanvas
import tkinter as tk
from tkinter import messagebox
import mouse # mouse 모듈 임포트 추가
import time
import psutil # 메모리 사용량 측정을 위해 psutil 임포트
import logging # 로깅을 위해 logging 임포트

# --- 메모리 로깅 함수 추가 ---
def log_memory_usage(label):
    process = psutil.Process(os.getpid())
    memory_mb = process.memory_info().rss / (1024 * 1024) # RSS를 MB 단위로
    logging.info(f"[Memory Check][{label}] 사용량: {memory_mb:.2f} MB")
# --- 함수 추가 끝 ---

class GestureManager:
    def __init__(self, macro_player, storage, recorder=None, timer_log_callback=None, monitors=None):
        """제스처 관리자 초기화"""
        self.macro_player = macro_player
        self.storage = storage # 이제 MacroStorage는 macros.json을 관리
        self.recorder = recorder
        # self.gesture_start_x = 0 # abs_pos 에서 직접 사용하므로 제거 또는 유지 (디버깅용)
        # self.gesture_start_y = 0 # abs_pos 에서 직접 사용하므로 제거 또는 유지 (디버깅용)
        self.timer_log_callback = timer_log_callback # 콜백 저장
        
        # 콜백 함수
        self.on_update_gesture_list = None
        self.on_macro_record_request = None
        self.gui_callback = None
        
        # 임시 제스처 저장
        self.temp_gesture = None
        
        # 녹화 상태
        self.recording_mode = False
        
        # 제스처 인식기 초기화
        self.gesture_recognizer = GestureRecognizer()
        
        # GlobalGestureListener 초기화 (monitors 전달)
        self.gesture_listener = GlobalGestureListener(monitors)
        
        # 콜백 설정 (변경된 시그니처에 맞게 GestureManager의 메서드들이 호출됨)
        self.gesture_listener.set_callbacks(
            self.on_gesture_started, # 이제 (abs_pos, rel_pos, monitor, modifiers) 형태
            self.on_gesture_moved,   # 이제 (abs_pos, rel_pos, monitor) 형태
            self.on_gesture_ended
        )
        # print(f"콜백 설정 완료: {self.on_gesture_started}, {self.on_gesture_moved}, {self.on_gesture_ended}") # 로그 메시지 유지 또는 수정
        
        # --- 제스처 경로 시각화를 위한 오버레이 캔버스 ---
        self.overlay_canvas = GestureCanvas(parent=None, is_overlay=True, line_color="red") # 오버레이 모드로 생성
        self.overlay_canvas.create() # 캔버스 및 창 생성
        self.overlay_canvas.hide()   # 처음에는 숨김
        # --- 오버레이 캔버스 끝 ---
        
        # 기존 제스처 시각화 캔버스 (녹화용)
        self.gesture_canvas = None # 기존 Canvas 인스턴스 (녹화 시 사용)
        self.canvas_window = None  # 기존 Canvas의 Toplevel 창 (녹화 시 사용)
            
    def start(self):
        """제스처 인식 시작 (키보드 리스너 시작 포함)"""
        # self.gesture_listener.start() # 기존 호출은 키보드 리스너를 시작하지 않음
        logging.info("Starting gesture recognition and keyboard listener...")
        # is_running 플래그 설정 및 키보드 리스너 시작 요청
        if hasattr(self.gesture_listener, 'is_running'): self.gesture_listener.is_running = True 
        success = self.gesture_listener.start_keyboard_listener()
        if success:
             logging.info("Gesture recognition fully started.")
        else:
             logging.error("Failed to start keyboard listener for gesture recognition.")
             # 에러 처리 필요 시 추가
             if hasattr(self.gesture_listener, 'is_running'): self.gesture_listener.is_running = False

    def stop(self):
        """제스처 인식 중지 (키보드 리스너 중지 포함)"""
        # self.gesture_listener.stop() # 기존 stop은 이제 키보드 리스너만 중지하지 않음
        logging.info("Stopping gesture recognition and keyboard listener...")
        # 키보드 리스너 중지 요청
        stopped_kb = self.gesture_listener.stop_keyboard_listener()
        
        # 오버레이 캔버스도 숨김 처리 추가
        if self.overlay_canvas:
            self.overlay_canvas.hide()
            logging.info("Overlay canvas hidden during gesture stop.")

        # is_running 플래그 업데이트 (GlobalGestureListener 내부에서 처리되도록 변경 고려)
        if hasattr(self.gesture_listener, 'is_running'): self.gesture_listener.is_running = False
        
        # stopped_mouse 제거 후 조건 수정
        if stopped_kb:
             logging.info("Gesture recognition fully stopped.")
        else:
             logging.warning("Gesture recognition stopped, but there might have been issues stopping keyboard listener.")

    def on_gesture_started(self, abs_pos, rel_pos, monitor, modifiers):
        """제스처 시작 콜백 - 오버레이 표시 및 절대/상대 좌표 처리"""
        # print(f"GestureManager 시작: Abs{abs_pos} Rel{rel_pos}, Monitor {monitor.name if monitor else 'N/A'}, Modifiers {modifiers}")
        logging.info(f"GestureManager 시작: Abs{abs_pos} Rel{rel_pos}, Monitor {monitor.name if monitor else 'N/A'}, Modifiers {modifiers}")

        try:
            # 전달받은 절대 좌표 사용
            self.gesture_start_x = abs_pos[0]
            self.gesture_start_y = abs_pos[1]
            # print(f"제스처 시작 절대 좌표 저장 (from callback): ({self.gesture_start_x}, {self.gesture_start_y})")
            logging.debug(f"제스처 시작 절대 좌표 저장 (from callback): ({self.gesture_start_x}, {self.gesture_start_y})")

            # 오버레이 캔버스 준비 및 표시
            self.overlay_canvas.clear()
            # self.overlay_canvas.set_line_color("red") # 필요시 색상 변경 (초기화 시 설정됨)
            self.overlay_canvas.show()
            self.overlay_canvas.add_point(abs_pos[0], abs_pos[1]) # 첫 점 추가 (절대 좌표)

        except Exception as e:
             # print(f"Error processing gesture start or starting overlay: {e}")
             logging.error(f"Error processing gesture start or starting overlay: {e}", exc_info=True)
             # 기본값 유지 또는 오류 처리
             self.gesture_start_x = 0 # 오류 시 초기화
             self.gesture_start_y = 0 # 오류 시 초기화
        
        # 제스처 인식기 시작 (상대 좌표 사용)
        self.gesture_recognizer.start_recording(rel_pos, modifiers)
        
        # 기존 녹화용 제스처 시각화 캔버스 (recording_mode일 때만, 상대 좌표 사용)
        if self.gesture_canvas and self.recording_mode:
            self.gesture_canvas.add_point( 
                rel_pos[0], rel_pos[1], color="blue" 
            )
        
    def on_gesture_moved(self, abs_pos, rel_pos, monitor):
        """제스처 이동 콜백 - 오버레이 경로 추가 (절대 좌표), 인식기 (상대 좌표)"""
        # 제스처 인식기에 점 추가 (상대 좌표)
        self.gesture_recognizer.add_point(rel_pos)
        
        try:
            # 오버레이 캔버스에 점 추가 (절대 좌표)
            self.overlay_canvas.add_point(abs_pos[0], abs_pos[1])
        except Exception as e:
            # print(f"Error drawing on overlay: {e}")
            logging.error(f"Error drawing on overlay: {e}", exc_info=True)

        # 기존 녹화용 제스처 시각화 캔버스 (recording_mode일 때만, 상대 좌표 사용)
        if self.gesture_canvas and self.recording_mode and len(self.gesture_recognizer.points) > 1:
            prev_point_rel = self.gesture_recognizer.points[-2] # 상대 좌표
            self.gesture_canvas.add_line(
                prev_point_rel[0], prev_point_rel[1], rel_pos[0], rel_pos[1],
                color="red", width=2
            )
        
    def on_gesture_ended(self):
        log_memory_usage("Gesture Ended - Start Processing") # 메모리 로그 추가
        gesture_end_time = time.time()
        print(f"[TimeLog] Gesture ended at: {gesture_end_time:.3f}")

        # 오버레이 캔버스 숨기기
        if self.overlay_canvas:
            self.overlay_canvas.hide() # 경로 그린 후 숨김

        recognition_start_time = time.time()
        gesture = self.gesture_recognizer.stop_recording()
        recognition_end_time = time.time()
        print(f"[TimeLog] Gesture recognition finished at: {recognition_end_time:.3f} (took {recognition_end_time - recognition_start_time:.3f}s)")
        
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
            print(f"제스처 임시 저장: {self.temp_gesture}")
            
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
        print(f"제스처 실행 시도: {gesture}")
        execution_start_time = time.time()
        log_memory_usage("Before Execute Action") # 메모리 로그 추가
        print(f"[TimeLog] Starting gesture action execution at: {execution_start_time:.3f}")
        self.execute_gesture_action(gesture, self.gesture_start_x, self.gesture_start_y)
        # execution_end_time = time.time() # 이 로그는 execute_gesture_action 내부로 이동
        # print(f"[TimeLog] Called execute_gesture_action at: {execution_end_time:.3f} (call overhead: {execution_end_time - execution_start_time:.3f}s)")
        
    def start_gesture_recording(self):
        """새 제스처 녹화 시작"""
        self.recording_mode = True
        print("제스처 녹화 모드 시작")
        
        # 제스처 시각화 창 생성
        self.create_gesture_canvas()
        
    def create_gesture_canvas(self):
        """제스처 녹화를 위한 캔버스 창 생성 (기존 로직 유지)"""
        if self.canvas_window: # 이미 있으면 파괴
            self.canvas_window.destroy()
            self.canvas_window = None
            self.gesture_canvas = None

        # GestureCanvas를 일반 녹화 모드(오버레이 아님)로 생성
        # parent=None으로 하여 Toplevel로 만듬
        self.gesture_canvas = GestureCanvas(parent=None, on_cancel=self.cancel_recording, is_overlay=False)
        self.canvas_window = self.gesture_canvas.window # GestureCanvas가 생성한 window 참조
        
        # create 메서드를 호출하여 캔버스를 실제로 생성하고 표시
        # create 메서드는 내부적으로 window.deiconify() 등을 호출할 수 있음 (GestureCanvas 구현에 따라 다름)
        if self.gesture_canvas.create(): # create가 성공하면
             print("녹화용 제스처 캔버스 생성됨")
        else:
             print("녹화용 제스처 캔버스 생성 실패")
             self.gesture_canvas = None # 실패 시 참조 제거
             self.canvas_window = None
        # 이전에 여기서 직접 Toplevel 만들던 로직은 GestureCanvas 내부로 이동됨
        
    def cancel_recording(self):
        """제스처 녹화 취소"""
        print("제스처 녹화 취소됨")
        self.recording_mode = False
        self.temp_gesture = None
        
        if self.canvas_window:
            self.canvas_window.destroy()
            self.canvas_window = None
            self.gesture_canvas = None
            
        self.gesture_recognizer.is_recording = False
        self.gesture_recognizer.points = []
        self.gesture_recognizer.modifiers = 0
        
    def save_macro_for_gesture(self, gesture, events):
        """제스처에 매크로 저장 (이제 gesture를 key로 사용) """
        print(f"매크로 저장: 제스처 '{gesture}'")
        
        # 매크로 저장 (storage 가 macros.json 에 저장)
        success = self.storage.save_macro(events, gesture)
        
        if success:
            # 제스처 목록 업데이트 (콜백)
            if self.on_update_gesture_list:
                self.on_update_gesture_list()
            return True
        return False
        
    def remove_mapping(self, gesture):
        """제스처 매핑 제거"""
        # storage를 통해 직접 삭제
        success = self.storage.delete_macro(gesture)
        
        if success:
            # 제스처 목록 업데이트 (콜백)
            if self.on_update_gesture_list:
                self.on_update_gesture_list()
            return True
        return False
    
    def get_mappings(self):
        """현재 제스처-매크로 매핑 반환"""
        # storage 에서 직접 가져옴
        return self.storage.get_all_mappings()
        
    def execute_gesture_action(self, gesture, base_x, base_y):
        load_start_time = time.time()
        events = self.storage.load_macro(gesture)
        load_end_time = time.time()
        print(f"[TimeLog] Loaded macro events at: {load_end_time:.3f} (took {load_end_time - load_start_time:.3f}s)")

        if events is not None:
            print(f"Executing macro for gesture: {gesture} with base ({base_x}, {base_y})")

            if isinstance(events, list):
                 if not events:
                     print(f"매크로가 비어 있어 실행할 수 없습니다: {gesture}")
                     return False

                 try:
                     print(f"매크로 실행: {len(events)}개 이벤트")
                     repeat_count = 1
                     if self.gui_callback:
                         try:
                             is_infinite = getattr(self.gui_callback, 'infinite_repeat', None)
                             count_var = getattr(self.gui_callback, 'repeat_count', None)
                             if is_infinite and isinstance(is_infinite, tk.BooleanVar) and is_infinite.get():
                                 repeat_count = 0
                                 print("무한 반복 설정 감지")
                             elif count_var and isinstance(count_var, tk.StringVar):
                                 repeat_str = count_var.get()
                                 if repeat_str.isdigit():
                                     parsed_count = int(repeat_str)
                                     if parsed_count > 0: repeat_count = parsed_count
                                     else: repeat_count = 1
                                     print(f"반복 횟수 설정 감지: {repeat_count}")
                                 else:
                                     print(f"경고: 반복 횟수 문자열({repeat_str})이 숫자가 아니므로 1회 실행합니다.")
                                     repeat_count = 1
                             else: print("GUI 콜백에서 반복 설정 변수 못 찾음")
                         except Exception as e_gui: print(f"GUI 반복 설정 오류: {e_gui}")
                     else: print("GUI 콜백 없음")

                     play_call_start_time = time.time()
                     print(f"[TimeLog] Calling play_macro at: {play_call_start_time:.3f}")
                     # --- play_macro 호출 시 base_x, base_y 전달 ---
                     play_success = self.macro_player.play_macro(events, repeat_count, base_x=base_x, base_y=base_y)
                     play_call_end_time = time.time()
                     print(f"[TimeLog] Returned from play_macro call at: {play_call_end_time:.3f} (sync part took {play_call_end_time - play_call_start_time:.3f}s - includes thread start request)")

                     # --- 타이머 지연 체크 로그 추가 ---
                     if self.gui_callback and hasattr(self.gui_callback, 'root') and self.timer_log_callback:
                         scheduled_time = time.time()
                         self.gui_callback.root.after(1, lambda: self.timer_log_callback(scheduled_time)) # self.timer_log_callback 사용
                     # --- 로그 추가 끝 ---

                     return play_success
                 except Exception as e:
                     print(f"매크로 실행 중 오류 발생: {e}")
                     import traceback
                     traceback.print_exc() # 상세 오류 출력
                     return False
            else:
                 print(f"매크로 데이터가 유효하지 않음: {type(events)}")
                 return False
        else:
            print(f"No macro mapping for gesture: {gesture}")
            return False
        
    # 콜백 설정
    def set_update_gesture_list_callback(self, callback):
        """제스처 목록 업데이트 콜백 설정"""
        print(f"제스처 목록 업데이트 콜백 설정: {callback}")
        self.on_update_gesture_list = callback
        
    def set_macro_record_callback(self, callback):
        """매크로 녹화 요청 콜백 설정"""
        self.on_macro_record_request = callback
    
    def set_gui_callback(self, gui_instance):
        """GUI 인스턴스 참조 설정"""
        print(f"GUI 인스턴스 콜백 설정: {gui_instance}")
        self.gui_callback = gui_instance

    def set_overlay_line_color(self, color_hex):
        """오버레이 캔버스의 선 색상을 설정합니다."""
        if self.overlay_canvas:
            self.overlay_canvas.set_line_color(color_hex)
            logging.info(f"Overlay canvas line color set to: {color_hex}")
        else:
            logging.warning("Overlay canvas not available to set line color.")

    def save_gesture_only(self, gesture):
        """제스처만 저장 (빈 매크로 이벤트 리스트 저장) """
        # storage에 이미 해당 제스처 키가 있는지 확인
        if self.storage.load_macro(gesture) is not None:
            messagebox.showwarning("이미 존재하는 제스처",
                                 f"제스처 '{gesture}'는 이미 매크로와 연결되어 있습니다.\n"
                                 f"기존 제스처를 삭제하거나 다른 제스처를 녹화하세요.")
            return False

        print(f"빈 매크로 저장: 제스처 '{gesture}'")

        # 빈 이벤트 리스트로 저장
        if self.storage.save_macro([], gesture): # gesture 를 key로 사용
            # 제스처 목록 업데이트 콜백 호출
            if self.on_update_gesture_list:
                print("제스처 목록 업데이트 콜백 호출")
                self.on_update_gesture_list()
            else:
                print("경고: 제스처 목록 업데이트 콜백이 설정되지 않았습니다.")

            messagebox.showinfo("제스처 저장됨", f"제스처 '{gesture}'가 저장되었습니다. 매크로를 녹화하려면 '매크로 녹화 시작' 버튼을 클릭하세요.")
            return True

        print("제스처 저장 실패!")
        return False 