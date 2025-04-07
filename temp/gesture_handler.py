import os
import webbrowser
import pyautogui
import subprocess
from gesture_settings import GestureSettings

class GestureHandler:
    def __init__(self):
        # 설정 로드
        self.settings = GestureSettings()
        
    def handle_gesture(self, gesture):
        """제스처를 인식하고 해당 액션을 실행"""
        action_id = self.settings.get_action_for_gesture(gesture)
        
        if not action_id:
            return None
            
        # 액션 실행 및 결과 반환
        action_name = self.settings.get_action_display_name(action_id)
        self._execute_action(action_id)
        return action_name
    
    def _execute_action(self, action_id):
        """액션 ID에 따라 해당 동작 실행"""
        # 내장 액션 함수 매핑
        action_map = {
            "action_maximize": self._maximize_window,
            "action_minimize": self._minimize_window,
            "action_close": self._close_window,
            "action_next_tab": self._next_tab,
            "action_prev_tab": self._prev_tab,
            "action_new_tab": self._new_tab,
            "action_refresh": self._refresh,
            "action_forward": self._forward,
            "action_back": self._back,
            "action_copy": self._copy,
            "action_paste": self._paste,
            "action_cut": self._cut,
            "action_undo": self._undo,
            "action_redo": self._redo,
            "action_select_all": self._select_all,
            "action_find": self._find,
            "action_save": self._save,
            "action_save_as": self._save_as,
            "action_print": self._print,
            "action_exit": self._exit_app,
            "action_switch_window": self._switch_window,
            "action_desktop": self._show_desktop,
            "action_explorer": self._open_explorer,
            "action_task_view": self._task_view,
            "action_screen_snip": self._screen_snip,
            "action_volume_up": self._volume_up,
            "action_volume_down": self._volume_down,
            "action_mute": self._mute,
            "action_play_pause": self._play_pause,
            "action_zoom_in": self._zoom_in,
            "action_zoom_out": self._zoom_out,
        }
        
        # 액션 실행
        if action_id in action_map:
            action_map[action_id]()
    
    # 여러 기본 동작 구현
    def _maximize_window(self):
        # 현재 창 최대화
        pyautogui.hotkey('alt', 'space')
        pyautogui.press('x')
    
    def _minimize_window(self):
        # 현재 창 최소화
        pyautogui.hotkey('alt', 'space')
        pyautogui.press('n')
    
    def _close_window(self):
        # 현재 창 닫기
        pyautogui.hotkey('alt', 'f4')
    
    def _next_tab(self):
        # 다음 탭으로 이동
        pyautogui.hotkey('ctrl', 'tab')
    
    def _prev_tab(self):
        # 이전 탭으로 이동
        pyautogui.hotkey('ctrl', 'shift', 'tab')
    
    def _new_tab(self):
        # 새 탭 열기
        pyautogui.hotkey('ctrl', 't')
    
    def _refresh(self):
        # 새로고침
        pyautogui.press('f5')
    
    def _forward(self):
        # 앞으로 가기
        pyautogui.hotkey('alt', 'right')
    
    def _back(self):
        # 뒤로 가기
        pyautogui.hotkey('alt', 'left')
    
    def _copy(self):
        # 복사
        pyautogui.hotkey('ctrl', 'c')
    
    def _paste(self):
        # 붙여넣기
        pyautogui.hotkey('ctrl', 'v')
    
    def _cut(self):
        # 잘라내기
        pyautogui.hotkey('ctrl', 'x')
    
    def _undo(self):
        # 실행 취소
        pyautogui.hotkey('ctrl', 'z')
    
    def _redo(self):
        # 다시 실행
        pyautogui.hotkey('ctrl', 'y')
    
    def _select_all(self):
        # 모두 선택
        pyautogui.hotkey('ctrl', 'a')
    
    def _find(self):
        # 찾기
        pyautogui.hotkey('ctrl', 'f')
    
    def _save(self):
        # 저장
        pyautogui.hotkey('ctrl', 's')
    
    def _save_as(self):
        # 다른 이름으로 저장
        pyautogui.hotkey('ctrl', 'shift', 's')
    
    def _print(self):
        # 인쇄
        pyautogui.hotkey('ctrl', 'p')
    
    def _exit_app(self):
        # 현재 응용 프로그램 종료
        pyautogui.hotkey('alt', 'f4')
    
    def _switch_window(self):
        # 창 전환 (Alt+Tab)
        pyautogui.hotkey('alt', 'tab')
    
    def _show_desktop(self):
        # 바탕화면 표시
        pyautogui.hotkey('win', 'd')
    
    def _open_explorer(self):
        # 파일 탐색기 열기
        pyautogui.hotkey('win', 'e')
    
    def _task_view(self):
        # 작업 보기
        pyautogui.hotkey('win', 'tab')
    
    def _screen_snip(self):
        # 화면 캡처 도구
        pyautogui.hotkey('win', 'shift', 's')
    
    def _volume_up(self):
        # 볼륨 증가
        for _ in range(2):  # 두 번 증가
            pyautogui.press('volumeup')
    
    def _volume_down(self):
        # 볼륨 감소
        for _ in range(2):  # 두 번 감소
            pyautogui.press('volumedown')
    
    def _mute(self):
        # 음소거 전환
        pyautogui.press('volumemute')
    
    def _play_pause(self):
        # 미디어 재생/일시정지
        pyautogui.press('playpause')
    
    def _zoom_in(self):
        # 확대
        pyautogui.hotkey('ctrl', '+')
    
    def _zoom_out(self):
        # 축소
        pyautogui.hotkey('ctrl', '-') 