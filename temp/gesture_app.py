from PyQt5.QtWidgets import (QMainWindow, QLabel, QVBoxLayout, QWidget, QPushButton, QHBoxLayout, 
                          QCheckBox, QSystemTrayIcon, QMenu, QTableWidget, QTableWidgetItem, 
                          QHeaderView, QAbstractItemView, QComboBox, QFrame, QTabWidget,
                          QDialog, QFormLayout, QMessageBox)
from PyQt5.QtCore import Qt, QSettings
from PyQt5.QtGui import QIcon, QFont, QColor, QCursor
from gesture_recognizer import GestureRecognizer
from gesture_handler import GestureHandler
from gesture_settings import GestureSettings
from global_gesture_listener import GlobalGestureListener

class AddGestureDialog(QDialog):
    def __init__(self, parent=None, settings=None):
        super().__init__(parent)
        self.settings = settings
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle("Add New Gesture")
        self.setMinimumWidth(400)
        
        layout = QVBoxLayout(self)
        
        # 폼 레이아웃
        form_layout = QFormLayout()
        
        # 제스처 패턴 선택
        self.pattern_combo = QComboBox()
        self.pattern_combo.addItems(self.settings.get_available_gesture_patterns())
        form_layout.addRow("Gesture Pattern:", self.pattern_combo)
        
        # 모디파이어 선택
        self.modifier_combo = QComboBox()
        self.modifier_combo.addItem("None", "")
        for mod_key, mod_name in self.settings.modifiers.items():
            self.modifier_combo.addItem(mod_name, mod_key)
        form_layout.addRow("Modifier Key:", self.modifier_combo)
        
        # 액션 선택
        self.action_combo = QComboBox()
        for action_id, action_name in self.settings.get_all_actions().items():
            self.action_combo.addItem(
                self.settings.get_action_with_shortcut(action_id), 
                action_id
            )
        form_layout.addRow("Action:", self.action_combo)
        
        layout.addLayout(form_layout)
        
        # 버튼 레이아웃
        button_layout = QHBoxLayout()
        
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)
        
        add_button = QPushButton("Add Gesture")
        add_button.clicked.connect(self.accept)
        add_button.setDefault(True)
        button_layout.addWidget(add_button)
        
        layout.addLayout(button_layout)
    
    def get_gesture_data(self):
        pattern = self.pattern_combo.currentText()
        modifier = self.modifier_combo.currentData()
        action = self.action_combo.currentData()
        
        # 제스처 ID 생성 (모디파이어가 있는 경우 추가)
        gesture_id = pattern
        if modifier:
            gesture_id = f"{modifier}+{pattern}"
            
        return gesture_id, action

class GestureApp(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # 키보드 모디파이어 사용 여부
        self.use_modifiers = True
        
        # 전역 동작 여부
        self.global_mode = False
        
        # 제스처 설정 로드
        self.gesture_settings = GestureSettings()
        
        # 프로그램 설정 로드
        self.settings = QSettings("MouseGesture", "App")
        self.load_settings()
        
        # 제스처 콤보박스 사전
        self.gesture_combos = {}
        
        # UI 초기화는 속성 설정 후에 진행
        self.initUI()
        
        # 제스처 인식기와 핸들러 초기화
        self.gesture_recognizer = GestureRecognizer()
        self.gesture_handler = GestureHandler()
        
        # 글로벌 제스처 리스너 초기화
        self.global_listener = GlobalGestureListener()
        
        # 글로벌 리스너의 시그널 연결
        self.global_listener.gesture_started.connect(self.on_global_gesture_started)
        self.global_listener.gesture_moved.connect(self.on_global_gesture_moved)
        self.global_listener.gesture_ended.connect(self.on_global_gesture_ended)
        
        # 초기 모드 설정 적용
        self.toggle_global_mode(self.global_mode)
        
    def initUI(self):
        self.setWindowTitle('Mouse Gesture App')
        self.setGeometry(100, 100, 900, 700)
        
        # 중앙 위젯 설정
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 메인 레이아웃
        main_layout = QVBoxLayout(central_widget)
        
        # 탭 위젯 생성
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)
        
        # 상태 탭
        status_tab = QWidget()
        self.tab_widget.addTab(status_tab, "Status")
        
        # 설정 탭
        settings_tab = QWidget()
        self.tab_widget.addTab(settings_tab, "Gesture Settings")
        
        # 상태 탭 UI 구성
        self.setup_status_tab(status_tab)
        
        # 설정 탭 UI 구성
        self.setup_settings_tab(settings_tab)
        
        # 시스템 트레이 아이콘 설정
        self.setup_tray_icon()

    def setup_status_tab(self, tab):
        # 상태 탭 레이아웃
        layout = QVBoxLayout(tab)
        
        # 상태 레이블 추가
        self.status_label = QLabel('Ready for keyboard gesture...')
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)
        
        # 제스처 경로 표시 레이블
        self.path_label = QLabel('')
        self.path_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.path_label)
        
        # 설명 텍스트 추가
        instruction_label = QLabel('Hold Ctrl, Shift, or Alt keys and move mouse to make gestures\nRelease keys to complete the gesture')
        instruction_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(instruction_label)
        
        # 전역 모드 활성화 체크박스
        global_check = QCheckBox('Enable global mode (works anywhere on screen)')
        global_check.setChecked(self.global_mode)
        global_check.stateChanged.connect(self.toggle_global_mode)
        layout.addWidget(global_check)
        
        # 현재 모디파이어 표시 레이블
        self.modifier_label = QLabel('Active modifiers: None')
        self.modifier_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.modifier_label)
        
        # 모드 표시 레이블
        self.mode_label = QLabel('Mode: Application Only')
        self.mode_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.mode_label)
        
        # 제스처 설정 버튼
        settings_button = QPushButton('Gesture Settings')
        settings_button.clicked.connect(lambda: self.tab_widget.setCurrentIndex(1))
        layout.addWidget(settings_button)
        
        # 간격 추가
        layout.addStretch()
        
        # 키보드 모디파이어 추적을 위한 설정
        self.setFocusPolicy(Qt.StrongFocus)
        
    def setup_settings_tab(self, tab):
        # 설정 탭 레이아웃
        tab_layout = QVBoxLayout(tab)
        
        # 제목 레이블 추가
        title_label = QLabel("Custom Gesture Settings")
        title_label.setAlignment(Qt.AlignCenter)
        font = QFont()
        font.setBold(True)
        font.setPointSize(14)
        title_label.setFont(font)
        tab_layout.addWidget(title_label)
        
        # 설명 레이블 추가
        info_label = QLabel("Add custom gestures and assign actions to them")
        info_label.setAlignment(Qt.AlignCenter)
        tab_layout.addWidget(info_label)
        
        # 버튼 영역 (제스처 추가, 제거 등)
        button_layout = QHBoxLayout()
        
        # 제스처 추가 버튼
        add_gesture_button = QPushButton("Add Gesture")
        add_gesture_button.clicked.connect(self.show_add_gesture_dialog)
        button_layout.addWidget(add_gesture_button)
        
        # 선택한 제스처 제거 버튼
        remove_gesture_button = QPushButton("Remove Selected")
        remove_gesture_button.clicked.connect(self.remove_selected_gesture)
        button_layout.addWidget(remove_gesture_button)
        
        # 모든 제스처 제거 버튼
        clear_all_button = QPushButton("Clear All")
        clear_all_button.clicked.connect(self.clear_all_gestures)
        button_layout.addWidget(clear_all_button)
        
        tab_layout.addLayout(button_layout)
        
        # 표 생성
        self.gesture_table = QTableWidget(0, 2, self)
        self.gesture_table.setHorizontalHeaderLabels(["Gesture", "Action"])
        
        # 테이블 스타일 설정
        self.gesture_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.gesture_table.setAlternatingRowColors(True)
        self.gesture_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.gesture_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.gesture_table.verticalHeader().setVisible(False)
        
        header_font = QFont()
        header_font.setBold(True)
        self.gesture_table.horizontalHeader().setFont(header_font)
        
        # 레이아웃에 테이블 추가
        tab_layout.addWidget(self.gesture_table)
        
        # 테이블 업데이트
        self.update_gesture_table()
        
        # 도움말 레이블 추가
        help_label = QLabel("Select an action for each gesture from the dropdown menu")
        help_label.setWordWrap(True)
        help_label.setAlignment(Qt.AlignCenter)
        tab_layout.addWidget(help_label)
        
        # 버튼 레이아웃
        save_layout = QHBoxLayout()
        
        # 저장 버튼
        save_button = QPushButton("Save Settings", self)
        save_button.clicked.connect(self.save_gesture_settings)
        save_button.setDefault(True)
        save_layout.addWidget(save_button)
        
        tab_layout.addLayout(save_layout)
    
    def show_add_gesture_dialog(self):
        # 제스처 추가 대화상자 표시
        dialog = AddGestureDialog(self, self.gesture_settings)
        if dialog.exec_():
            gesture_id, action = dialog.get_gesture_data()
            
            # 이미 존재하는 제스처인지 확인
            if gesture_id in self.gesture_settings.get_all_gestures():
                QMessageBox.warning(self, "Duplicate Gesture", 
                                   f"The gesture '{gesture_id}' already exists.\nPlease choose a different gesture.")
                return
            
            # 새 제스처 추가
            self.gesture_settings.add_gesture(gesture_id, action)
            self.update_gesture_table()
    
    def remove_selected_gesture(self):
        # 선택된 제스처 삭제
        selected_rows = self.gesture_table.selectedIndexes()
        if not selected_rows:
            return
            
        row = selected_rows[0].row()
        gesture_item = self.gesture_table.item(row, 0)
        if gesture_item:
            gesture_id = gesture_item.data(Qt.UserRole)
            self.gesture_settings.remove_gesture(gesture_id)
            self.update_gesture_table()
    
    def clear_all_gestures(self):
        # 확인 대화상자 표시
        reply = QMessageBox.question(self, "Clear All Gestures", 
                                     "Are you sure you want to remove all gestures?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            # 모든 제스처 제거
            self.gesture_settings.reset_to_defaults()
            self.update_gesture_table()
    
    def update_gesture_table(self):
        # 테이블 초기화
        self.gesture_table.setRowCount(0)
        self.gesture_combos.clear()
        
        # 현재 모든 제스처 가져오기
        gestures = self.gesture_settings.get_all_gestures()
        if not gestures:
            # 제스처가 없는 경우 안내 메시지 표시
            self.gesture_table.setRowCount(1)
            no_gestures_item = QTableWidgetItem("No gestures defined. Click 'Add Gesture' to create one.")
            no_gestures_item.setFlags(Qt.ItemIsEnabled)
            self.gesture_table.setItem(0, 0, no_gestures_item)
            self.gesture_table.setSpan(0, 0, 1, 2)
            return
        
        # 테이블에 제스처 추가
        actions = self.gesture_settings.get_all_actions()
        for row, gesture in enumerate(gestures):
            self.gesture_table.insertRow(row)
            self.add_gesture_row(self.gesture_table, gesture, actions, row)
    
    def add_gesture_row(self, table, gesture, actions, row):
        # 제스처 표시 항목 생성
        if '+' in gesture:
            # 모디파이어+제스처 형식 (CTRL+swipe-right)
            mod, gest = gesture.split('+', 1)
            display_mod = self.gesture_settings.get_modifier_display_name(mod)
            gesture_display = f"{display_mod} + {gest.replace('-', ' ').title()}"
        else:
            # 일반 제스처
            gesture_display = gesture.replace("-", " ").title()
        
        # 제스처 표시 항목
        gesture_item = QTableWidgetItem(gesture_display)
        gesture_item.setFlags(gesture_item.flags() & ~Qt.ItemIsEditable)  # 편집 불가능하게 설정
        gesture_item.setData(Qt.UserRole, gesture)  # 원본 제스처 ID 저장
        
        # 제스처 항목에 폰트 적용
        font = QFont()
        font.setBold(True)
        gesture_item.setFont(font)
        
        table.setItem(row, 0, gesture_item)
        
        # 액션 선택 콤보박스
        action_combo = QComboBox()
        action_combo.setMaxVisibleItems(15)  # 드롭다운 목록 표시 항목 수 제한
        
        # 액션 목록 추가 (단축키 정보 포함)
        for action_id, action_desc in actions.items():
            # 액션 이름과 단축키 함께 표시
            combo_text = self.gesture_settings.get_action_with_shortcut(action_id)
            action_combo.addItem(combo_text, action_id)
        
        # 현재 설정된 액션 선택
        current_action = self.gesture_settings.get_action_for_gesture(gesture)
        if current_action:
            index = action_combo.findData(current_action)
            if index >= 0:
                action_combo.setCurrentIndex(index)
        
        # 콤보박스를 딕셔너리에 저장
        self.gesture_combos[gesture] = action_combo
        
        # 테이블에 콤보박스 추가
        table.setCellWidget(row, 1, action_combo)
        
        # 행 높이 설정
        table.setRowHeight(row, 40)
        
    def setup_tray_icon(self):
        # 시스템 트레이 아이콘 생성
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setToolTip('Mouse Gesture App')
        
        # 시스템 트레이 메뉴 설정
        tray_menu = QMenu()
        
        # 메뉴 항목 추가
        show_action = tray_menu.addAction('Show Window')
        show_action.triggered.connect(self.show)
        
        # 세팅 탭 전환 액션 추가
        settings_action = tray_menu.addAction('Gesture Settings')
        settings_action.triggered.connect(lambda: self.tab_widget.setCurrentIndex(1))
        
        toggle_global_action = tray_menu.addAction('Toggle Global Mode')
        toggle_global_action.triggered.connect(lambda: self.toggle_global_mode(not self.global_mode))
        
        quit_action = tray_menu.addAction('Quit')
        quit_action.triggered.connect(self.close)
        
        # 메뉴 설정
        self.tray_icon.setContextMenu(tray_menu)
        
        # 트레이 아이콘 표시
        self.tray_icon.show()
        
    def closeEvent(self, event):
        # 프로그램 종료 시 설정 저장
        self.save_settings()
        
        # 제스처 설정 저장
        self.save_gesture_settings()
        
        # 글로벌 리스너 정지
        if self.global_listener:
            self.global_listener.stop()
            
        # 이벤트 수락 (프로그램 종료)
        event.accept()
        
    def save_settings(self):
        # 설정 저장
        self.settings.setValue("global_mode", self.global_mode)
        
    def load_settings(self):
        # 설정 로드
        self.global_mode = self.settings.value("global_mode", False, type=bool)
    
    def save_gesture_settings(self):
        # 모든 콤보박스의 선택을 저장
        for gesture, combo in self.gesture_combos.items():
            action = combo.currentData()
            self.gesture_settings.set_action_for_gesture(gesture, action)
        
        # 설정 파일에 저장
        saved = self.gesture_settings.save_settings()
        
        # 저장 완료 메시지
        if saved:
            QMessageBox.information(self, "Settings Saved", "Gesture settings have been saved successfully.")
        
        # 핸들러 재초기화
        self.gesture_handler = GestureHandler()
        
        # 상태 탭으로 전환
        self.tab_widget.setCurrentIndex(0)
    
    def reset_to_defaults(self):
        # 기본 설정으로 콤보박스 초기화
        self.clear_all_gestures()
        
    def toggle_global_mode(self, state=None):
        # 전역 모드 토글
        if state is not None:
            self.global_mode = state if isinstance(state, bool) else (state == Qt.Checked)
        
        if self.global_mode:
            # 전역 모드 활성화
            self.mode_label.setText('Mode: Global (works anywhere)')
            # 글로벌 리스너 시작
            self.global_listener.start()
        else:
            # 앱 모드 활성화
            self.mode_label.setText('Mode: Application Only')
            # 글로벌 리스너 중지
            self.global_listener.stop()
        
        # 설정 저장
        self.save_settings()
    
    def on_global_gesture_started(self, point, modifiers):
        # 글로벌 제스처 시작 처리
        self.gesture_recognizer.start_recording(point, modifiers)
        self._update_modifier_label(modifiers)
        self.status_label.setText('Recording gesture...')
    
    def on_global_gesture_moved(self, point):
        # 글로벌 제스처 이동 처리
        if self.gesture_recognizer.is_recording:
            self.gesture_recognizer.add_point(point)
            self.path_label.setText(f'Path: {self.gesture_recognizer.get_current_path()}')
    
    def on_global_gesture_ended(self):
        # 글로벌 제스처 종료 처리
        if self.gesture_recognizer.is_recording:
            gesture = self.gesture_recognizer.stop_recording()
            self.status_label.setText(f'Recognized: {gesture}')
            
            # 제스처에 해당하는 동작 실행
            action = self.gesture_handler.handle_gesture(gesture)
            if action:
                self.status_label.setText(f'Executed: {action}')
            else:
                self.status_label.setText(f'No action for gesture: {gesture}')
                
            # 모디파이어 레이블 초기화
            self.modifier_label.setText("Active modifiers: None")
    
    def _update_modifier_label(self, modifiers):
        # 모디파이어 레이블 업데이트
        mod_text = []
        if modifiers & Qt.ControlModifier:
            mod_text.append("Ctrl")
        if modifiers & Qt.ShiftModifier:
            mod_text.append("Shift")
        if modifiers & Qt.AltModifier:
            mod_text.append("Alt")
            
        if mod_text:
            self.modifier_label.setText(f"Active modifiers: {'+'.join(mod_text)}")
        else:
            self.modifier_label.setText("Active modifiers: None")
    
    def mousePressEvent(self, event):
        # 앱 내에서는 모디파이어 키를 눌러야만 제스처 인식
        pass
    
    def mouseMoveEvent(self, event):
        # 앱 내에서는 모디파이어 키를 눌러야만 제스처 인식
        pass
    
    def mouseReleaseEvent(self, event):
        # 앱 내에서는 모디파이어 키를 눌러야만 제스처 인식
        pass
        
    def keyPressEvent(self, event):
        # 앱 내에서 키보드 이벤트 처리
        modifiers = event.modifiers()
        
        # 모디파이어 키가 눌렸는지 확인
        if (modifiers & Qt.ControlModifier or 
            modifiers & Qt.ShiftModifier or 
            modifiers & Qt.AltModifier) and not self.gesture_recognizer.is_recording:
            
            # 제스처 시작
            pos = self.mapFromGlobal(QCursor.pos())
            self.gesture_recognizer.start_recording(pos, modifiers)
            self.status_label.setText('Recording gesture...')
            self._update_modifier_label(modifiers)
    
    def keyReleaseEvent(self, event):
        # 키 해제 시 모디파이어 체크
        modifiers = event.modifiers()
        
        # Ctrl, Shift, Alt가 모두 해제되었는지 확인
        if not (modifiers & Qt.ControlModifier or 
                modifiers & Qt.ShiftModifier or 
                modifiers & Qt.AltModifier) and self.gesture_recognizer.is_recording:
            
            # 제스처 종료
            gesture = self.gesture_recognizer.stop_recording()
            self.status_label.setText(f'Recognized: {gesture}')
            
            # 제스처에 해당하는 동작 실행
            action = self.gesture_handler.handle_gesture(gesture)
            if action:
                self.status_label.setText(f'Executed: {action}')
            else:
                self.status_label.setText(f'No action for gesture: {gesture}')
                
            # 모디파이어 레이블 초기화
            self.modifier_label.setText("Active modifiers: None") 