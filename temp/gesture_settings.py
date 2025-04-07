import json
import os

class GestureSettings:
    def __init__(self):
        # 모디파이어 키 매핑
        self.modifiers = {
            "CTRL": "Ctrl",
            "SHIFT": "Shift",
            "ALT": "Alt"
        }
        
        # 기본 제스처-액션 매핑 (이제 빈 딕셔너리로 시작)
        self.default_gesture_actions = {}
        
        # 액션 목록
        self.actions = {
            "action_maximize": "Maximize Window",
            "action_minimize": "Minimize Window",
            "action_close": "Close Window",
            "action_next_tab": "Next Tab",
            "action_prev_tab": "Previous Tab",
            "action_new_tab": "New Tab",
            "action_refresh": "Refresh",
            "action_forward": "Navigate Forward",
            "action_back": "Navigate Back",
            "action_copy": "Copy",
            "action_paste": "Paste",
            "action_cut": "Cut",
            "action_undo": "Undo",
            "action_redo": "Redo",
            "action_select_all": "Select All",
            "action_find": "Find",
            "action_save": "Save",
            "action_save_as": "Save As",
            "action_print": "Print",
            "action_exit": "Exit Application",
            "action_switch_window": "Switch Window",
            "action_desktop": "Show Desktop",
            "action_explorer": "Open File Explorer",
            "action_task_view": "Task View",
            "action_screen_snip": "Screen Snip",
            "action_volume_up": "Volume Up",
            "action_volume_down": "Volume Down",
            "action_mute": "Mute",
            "action_play_pause": "Play/Pause Media",
            "action_zoom_in": "Zoom In",
            "action_zoom_out": "Zoom Out"
        }
        
        # 액션 단축키 (옵션)
        self.action_shortcuts = {
            "action_maximize": "Alt+Space, X",
            "action_minimize": "Alt+Space, N",
            "action_close": "Alt+F4",
            "action_next_tab": "Ctrl+Tab",
            "action_prev_tab": "Ctrl+Shift+Tab",
            "action_new_tab": "Ctrl+T",
            "action_refresh": "F5",
            "action_forward": "Alt+Right",
            "action_back": "Alt+Left",
            "action_copy": "Ctrl+C",
            "action_paste": "Ctrl+V",
            "action_cut": "Ctrl+X",
            "action_undo": "Ctrl+Z",
            "action_redo": "Ctrl+Y",
            "action_select_all": "Ctrl+A",
            "action_find": "Ctrl+F",
            "action_save": "Ctrl+S",
            "action_save_as": "Ctrl+Shift+S",
            "action_print": "Ctrl+P",
            "action_exit": "Alt+F4",
            "action_task_view": "Win+Tab",
            "action_screen_snip": "Win+Shift+S",
            "action_zoom_in": "Ctrl++",
            "action_zoom_out": "Ctrl+-"
        }
        
        # 사용 가능한 제스처 패턴 목록
        self.available_gesture_patterns = [
            "swipe-up",
            "swipe-down",
            "swipe-left",
            "swipe-right",
            "swipe-up-right",
            "swipe-up-left",
            "swipe-down-right",
            "swipe-down-left",
            "circle-clockwise",
            "circle-counterclockwise",
            "zigzag",
            "N-shape",
            "Z-shape",
            "V-shape",
            "caret-up",
            "caret-down",
            "caret-left",
            "caret-right"
        ]
        
        # 사용자 설정
        self.user_gesture_actions = {}
        
        # 설정 로드
        self.load_settings()
    
    def get_available_gesture_patterns(self):
        # 사용 가능한 모든 제스처 패턴 반환
        return self.available_gesture_patterns
        
    def add_gesture(self, gesture_id, action_id):
        """사용자 정의 제스처 추가"""
        self.user_gesture_actions[gesture_id] = action_id
        
    def remove_gesture(self, gesture_id):
        """사용자 정의 제스처 제거"""
        if gesture_id in self.user_gesture_actions:
            del self.user_gesture_actions[gesture_id]
            
    def get_all_gestures(self):
        """현재 설정된 모든 제스처 목록 반환"""
        # 이제 default_gesture_actions는 비어있으므로 user_gesture_actions만 반환
        return list(self.user_gesture_actions.keys())
    
    def get_all_actions(self):
        """사용 가능한 모든 액션 목록 반환"""
        return self.actions
    
    def get_action_for_gesture(self, gesture):
        """특정 제스처에 매핑된 액션 ID 반환"""
        # 사용자 설정에서 먼저 확인
        if gesture in self.user_gesture_actions:
            return self.user_gesture_actions[gesture]
        # 기본 설정에서 확인 (이제 비어 있음)
        return self.default_gesture_actions.get(gesture)
    
    def set_action_for_gesture(self, gesture, action):
        """제스처에 액션 설정"""
        if gesture and action:
            self.user_gesture_actions[gesture] = action
    
    def get_action_display_name(self, action_id):
        """액션 ID에 해당하는 표시 이름 반환"""
        return self.actions.get(action_id, "Unknown Action")
    
    def get_action_with_shortcut(self, action_id):
        """액션 ID에 대한 이름과 단축키 함께 반환"""
        action_name = self.actions.get(action_id, "Unknown Action")
        shortcut = self.action_shortcuts.get(action_id, "")
        
        if shortcut:
            return f"{action_name} ({shortcut})"
        return action_name
    
    def get_modifier_display_name(self, modifier):
        """모디파이어 키에 대한 표시 이름 반환"""
        return self.modifiers.get(modifier, modifier)
    
    def reset_to_defaults(self):
        """모든 제스처를 기본값으로 초기화 (이제는 모두 제거)"""
        self.user_gesture_actions = {}
        
    def load_settings(self):
        """파일에서 설정 로드"""
        # 설정 파일 경로
        settings_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'gesture_settings.json')
        
        # 파일이 존재하면 로드
        if os.path.exists(settings_path):
            try:
                with open(settings_path, 'r') as f:
                    settings = json.load(f)
                    # 저장된 사용자 제스처 설정 로드
                    self.user_gesture_actions = settings.get('user_gesture_actions', {})
            except (json.JSONDecodeError, IOError) as e:
                print(f"설정 로드 중 오류 발생: {e}")
                # 로드 실패 시 기본값으로 빈 딕셔너리 설정
                self.user_gesture_actions = {}
        else:
            # 파일이 없으면 기본값으로 빈 딕셔너리 설정
            self.user_gesture_actions = {}
    
    def save_settings(self):
        """파일에 설정 저장"""
        # 설정 파일 경로
        settings_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'gesture_settings.json')
        
        # 저장할 설정 데이터
        settings_data = {
            'user_gesture_actions': self.user_gesture_actions
        }
        
        try:
            # JSON 파일로 저장
            with open(settings_path, 'w') as f:
                json.dump(settings_data, f, indent=4)
            return True
        except IOError as e:
            print(f"설정 저장 중 오류 발생: {e}")
            return False 