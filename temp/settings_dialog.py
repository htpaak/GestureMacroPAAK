from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QComboBox,
                             QLabel, QPushButton, QGridLayout, QTableWidget, QTableWidgetItem,
                             QHeaderView, QAbstractItemView, QFrame)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor, QIcon
from gesture_settings import GestureSettings

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.settings = GestureSettings()
        self.gesture_combos = {}  # 제스처-콤보박스 매핑을 저장
        self.initUI()
        
    def initUI(self):
        # 대화상자 제목 및 크기 설정
        self.setWindowTitle('Gesture Settings')
        self.setMinimumWidth(800)
        self.setMinimumHeight(700)
        
        # 메인 레이아웃
        main_layout = QVBoxLayout(self)
        
        # 제목 레이블 추가
        title_label = QLabel("Mouse Gesture Shortcuts")
        title_label.setAlignment(Qt.AlignCenter)
        font = QFont()
        font.setBold(True)
        font.setPointSize(14)
        title_label.setFont(font)
        main_layout.addWidget(title_label)
        
        # 설명 레이블 추가
        info_label = QLabel("Configure mouse gestures and keyboard+mouse combinations")
        info_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(info_label)
        
        # 모든 제스처 가져오기
        gestures = self.settings.get_all_gestures()
        actions = self.settings.get_all_actions()
        
        # 기본 제스처와 모디파이어 제스처 분리
        standard_gestures = []
        modifier_gestures = []
        
        for gesture in gestures:
            if '+' in gesture:
                modifier_gestures.append(gesture)
            else:
                standard_gestures.append(gesture)
        
        # 표 생성 - 모든 제스처를 하나의 테이블에 표시
        table = QTableWidget(len(gestures), 2, self)
        table.setHorizontalHeaderLabels(["Gesture", "Action"])
        
        # 테이블 스타일 설정
        table.setSelectionBehavior(QAbstractItemView.SelectRows)
        table.setAlternatingRowColors(True)
        table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        table.verticalHeader().setVisible(False)
        
        header_font = QFont()
        header_font.setBold(True)
        table.horizontalHeader().setFont(header_font)
        
        # 현재 행 위치 추적
        current_row = 0
        
        # 먼저 섹션 레이블 추가 (표준 제스처)
        if standard_gestures:
            section_item = QTableWidgetItem("STANDARD MOUSE GESTURES")
            section_item.setFlags(Qt.ItemIsEnabled)  # 선택 불가능하게 설정
            section_item.setBackground(QColor(230, 230, 230))
            section_font = QFont()
            section_font.setBold(True)
            section_item.setFont(section_font)
            
            # 섹션 행을 테이블에 추가
            table.setItem(current_row, 0, section_item)
            span_item = QTableWidgetItem()
            span_item.setFlags(Qt.ItemIsEnabled)  
            span_item.setBackground(QColor(230, 230, 230))
            table.setItem(current_row, 1, span_item)
            
            # 섹션 행 높이 설정
            table.setRowHeight(current_row, 30)
            current_row += 1
            
            # 표준 제스처 항목들 추가
            for gesture in standard_gestures:
                self.add_gesture_row(table, gesture, actions, current_row)
                current_row += 1
        
        # 구분선 추가
        if standard_gestures and modifier_gestures:
            # 빈 행 추가
            for col in range(2):
                empty_item = QTableWidgetItem("")
                empty_item.setFlags(Qt.ItemIsEnabled)
                table.setItem(current_row, col, empty_item)
            table.setRowHeight(current_row, 15)
            current_row += 1
        
        # 모디파이어 제스처 섹션 추가
        if modifier_gestures:
            section_item = QTableWidgetItem("KEYBOARD + MOUSE GESTURES")
            section_item.setFlags(Qt.ItemIsEnabled)  
            section_item.setBackground(QColor(230, 230, 230))
            section_font = QFont()
            section_font.setBold(True)
            section_item.setFont(section_font)
            
            # 섹션 행을 테이블에 추가
            table.setItem(current_row, 0, section_item)
            span_item = QTableWidgetItem()
            span_item.setFlags(Qt.ItemIsEnabled)  
            span_item.setBackground(QColor(230, 230, 230))
            table.setItem(current_row, 1, span_item)
            
            # 섹션 행 높이 설정
            table.setRowHeight(current_row, 30)
            current_row += 1
            
            # 모디파이어 제스처 항목들 추가
            for gesture in modifier_gestures:
                self.add_gesture_row(table, gesture, actions, current_row)
                current_row += 1
        
        # 레이아웃에 테이블 추가
        main_layout.addWidget(table)
        
        # 도움말 레이블 추가
        help_label = QLabel("Select an action for each gesture from the dropdown menu")
        help_label.setWordWrap(True)
        help_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(help_label)
        
        # 버튼 레이아웃
        button_layout = QHBoxLayout()
        
        # 기본값으로 초기화 버튼
        reset_button = QPushButton("Reset to Defaults", self)
        reset_button.clicked.connect(self.reset_to_defaults)
        button_layout.addWidget(reset_button)
        
        # 간격 추가
        button_layout.addStretch()
        
        # 취소 및 저장 버튼
        cancel_button = QPushButton("Cancel", self)
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)
        
        save_button = QPushButton("Save", self)
        save_button.clicked.connect(self.save_settings)
        save_button.setDefault(True)
        button_layout.addWidget(save_button)
        
        main_layout.addLayout(button_layout)
    
    def add_gesture_row(self, table, gesture, actions, row):
        # 제스처 표시 항목 생성
        if '+' in gesture:
            # 모디파이어+제스처 형식 (CTRL+swipe-right)
            mod, gest = gesture.split('+', 1)
            display_mod = self.settings.get_modifier_display_name(mod)
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
            combo_text = self.settings.get_action_with_shortcut(action_id)
            action_combo.addItem(combo_text, action_id)
        
        # 현재 설정된 액션 선택
        current_action = self.settings.get_action_for_gesture(gesture)
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
    
    def save_settings(self):
        # 모든 콤보박스의 선택을 저장
        for gesture, combo in self.gesture_combos.items():
            action = combo.currentData()
            self.settings.set_action_for_gesture(gesture, action)
        
        # 설정 파일에 저장
        if self.settings.save_settings():
            self.accept()  # 성공적으로 저장되면 대화상자 닫기
    
    def reset_to_defaults(self):
        # 기본 설정으로 콤보박스 초기화
        for gesture, combo in self.gesture_combos.items():
            default_action = self.settings.default_gesture_actions.get(gesture)
            if default_action:
                index = combo.findData(default_action)
                if index >= 0:
                    combo.setCurrentIndex(index) 