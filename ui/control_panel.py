"""
Control Panel Widget - Left side panel with data display and coffee roasting buttons
"""
from PyQt5.QtWidgets import (QGroupBox, QVBoxLayout, QLabel, QPushButton,
                             QWidget, QFrame)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont
from core.models import EventType


class ControlPanel(QGroupBox):
    """Left panel widget for displaying live data and controls"""

    # ============================
    # BASIC ROAST EVENT SIGNALS
    # ============================
    dry_end_clicked = pyqtSignal()

    # ============================
    # COFFEE ROASTING SIGNALS
    # ============================
    charge_clicked = pyqtSignal()
    fc_start_clicked = pyqtSignal()
    fc_finish_clicked = pyqtSignal()
    sc_start_clicked = pyqtSignal()
    drop_clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__('Roast Data', parent)
        self.init_ui()

    def init_ui(self):
        """Initialize the control panel UI"""
        # Main layout
        layout = QVBoxLayout()
        self.setLayout(layout)
        layout.setSpacing(15)
        layout.setContentsMargins(10, 15, 10, 15)

        # Start with all event buttons disabled
        self.buttons_disabled = True

        # ============================
        # LIVE DATA SECTION
        # ============================
        live_section = self.create_live_data_section()
        layout.addWidget(live_section)

        # Add separator line
        layout.addWidget(self.create_separator())

        # ============================
        # REFERENCE SECTION
        # ============================
        ref_section = self.create_reference_section()
        layout.addWidget(ref_section)

        # Add separator line
        layout.addWidget(self.create_separator())

        # ============================
        # EVENT BUTTONS SECTION (Basic + Coffee)
        # ============================
        event_section = self.create_event_buttons_section()
        layout.addWidget(event_section)

        # Add stretch to push everything to the top
        layout.addStretch()

        # Initialize buttons in disabled state
        self.set_buttons_enabled(False)

    def create_live_data_section(self) -> QFrame:
        """Create the live data display section"""
        frame = QFrame()
        frame_layout = QVBoxLayout()
        frame.setLayout(frame_layout)
        frame_layout.setSpacing(10)

        # Section title
        title_label = QLabel('LIVE DATA')
        title_label.setStyleSheet('font-size: 14px; font-weight: bold; color: #333;')
        frame_layout.addWidget(title_label)

        # BT Label - Bean Temperature (Red)
        self.bt_label = QLabel('BT: --.- °C')
        self.bt_label.setStyleSheet('''
            font-size: 28px;
            font-weight: bold;
            color: #e74c3c;
            background-color: #fde8e8;
            padding: 10px;
            border-radius: 5px;
            border: 2px solid #e74c3c;
        ''')
        self.bt_label.setAlignment(Qt.AlignCenter)
        frame_layout.addWidget(self.bt_label)

        # ET Label - Environmental Temperature (Blue)
        self.et_label = QLabel('ET: --.- °C')
        self.et_label.setStyleSheet('''
            font-size: 28px;
            font-weight: bold;
            color: #3498db;
            background-color: #d4e6f1;
            padding: 10px;
            border-radius: 5px;
            border: 2px solid #3498db;
        ''')
        self.et_label.setAlignment(Qt.AlignCenter)
        frame_layout.addWidget(self.et_label)

        # RoR Label - Rate of Rise (Green)
        self.ror_label = QLabel('RoR: -.-')
        self.ror_label.setStyleSheet('''
            font-size: 28px;
            font-weight: bold;
            color: #27ae60;
            background-color: #d5f4e6;
            padding: 10px;
            border-radius: 5px;
            border: 2px solid #27ae60;
        ''')
        self.ror_label.setAlignment(Qt.AlignCenter)
        frame_layout.addWidget(self.ror_label)

        # Time Label
        self.time_label = QLabel('Time: 00:00')
        self.time_label.setStyleSheet('''
            font-size: 20px;
            font-weight: bold;
            color: #555;
            padding: 8px;
            background-color: #f0f0f0;
            border-radius: 5px;
            border: 1px solid #bdc3c7;
        ''')
        self.time_label.setAlignment(Qt.AlignCenter)
        frame_layout.addWidget(self.time_label)

        return frame

    def create_reference_section(self) -> QFrame:
        """Create the reference profile section"""
        frame = QFrame()
        frame_layout = QVBoxLayout()
        frame.setLayout(frame_layout)
        frame_layout.setSpacing(10)

        # Section title
        title_label = QLabel('REFERENCE')
        title_label.setStyleSheet('font-size: 14px; font-weight: bold; color: #333;')
        frame_layout.addWidget(title_label)

        # Reference label
        self.ref_label = QLabel('Ref: No Profile')
        self.ref_label.setStyleSheet('''
            font-size: 16px;
            font-weight: bold;
            color: #7f8c8d;
            padding: 8px;
            background-color: #ecf0f1;
            border-radius: 5px;
            border: 1px dashed #bdc3c7;
        ''')
        self.ref_label.setAlignment(Qt.AlignCenter)
        self.ref_label.setWordWrap(True)
        frame_layout.addWidget(self.ref_label)

        return frame

    def create_event_buttons_section(self) -> QFrame:
        """Create the event buttons section"""
        frame = QFrame()
        frame_layout = QVBoxLayout()
        frame.setLayout(frame_layout)
        frame_layout.setSpacing(10)

        # Section title - EVENTS (not a button)
        events_label = QLabel('EVENTS')
        events_label.setStyleSheet('''
            font-size: 14px;
            font-weight: bold;
            color: #333;
            padding: 5px 0px;
        ''')
        frame_layout.addWidget(events_label)

        # ============================
        # ALL EVENT BUTTONS (Single Section)
        # Order: Charge, FC Start, FC Finish, SC Start, Drop, Dry End
        # ============================
        events_frame = QFrame()
        events_frame.setStyleSheet('''
            QFrame {
                border: none;
                background-color: #f9f9f9;
                border-radius: 8px;
                padding: 10px;
            }
        ''')
        events_layout = QVBoxLayout()
        events_layout.setSpacing(10)
        events_frame.setLayout(events_layout)
        frame_layout.addWidget(events_frame)

        # 1. Charge button
        self.charge_button = QPushButton('Charge')
        self.charge_button.setStyleSheet('''
            QPushButton {
                font-size: 13px;
                padding: 10px;
                background-color: #8A7650;
                color: white;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #7a6640;
            }
            QPushButton:pressed {
                background-color: #6a5630;
            }
            QPushButton:disabled {
                background-color: #ECE7D1;
                color: #999;
            }
        ''')
        self.charge_button.clicked.connect(self.charge_clicked.emit)
        events_layout.addWidget(self.charge_button)

        # 2. FC Start button
        self.fc_start_button = QPushButton('FC Start')
        self.fc_start_button.setStyleSheet('''
            QPushButton {
                font-size: 12px;
                padding: 8px;
                background-color: #8A7650;
                color: white;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #7a6640;
            }
            QPushButton:pressed {
                background-color: #6a5630;
            }
            QPushButton:disabled {
                background-color: #ECE7D1;
                color: #999;
            }
        ''')
        self.fc_start_button.clicked.connect(self.fc_start_clicked.emit)
        events_layout.addWidget(self.fc_start_button)

        # 3. FC Finish button
        self.fc_finish_button = QPushButton('FC Finish')
        self.fc_finish_button.setStyleSheet('''
            QPushButton {
                font-size: 12px;
                padding: 8px;
                background-color: #8A7650;
                color: white;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #7a6640;
            }
            QPushButton:pressed {
                background-color: #6a5630;
            }
            QPushButton:disabled {
                background-color: #ECE7D1;
                color: #999;
            }
        ''')
        self.fc_finish_button.clicked.connect(self.fc_finish_clicked.emit)
        events_layout.addWidget(self.fc_finish_button)

        # 4. SC Start button
        self.sc_start_button = QPushButton('SC Start')
        self.sc_start_button.setStyleSheet('''
            QPushButton {
                font-size: 12px;
                padding: 8px;
                background-color: #8A7650;
                color: white;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #7a6640;
            }
            QPushButton:pressed {
                background-color: #6a5630;
            }
            QPushButton:disabled {
                background-color: #ECE7D1;
                color: #999;
            }
        ''')
        self.sc_start_button.clicked.connect(self.sc_start_clicked.emit)
        events_layout.addWidget(self.sc_start_button)

        # 5. Drop button
        self.drop_button = QPushButton('Drop')
        self.drop_button.setStyleSheet('''
            QPushButton {
                font-size: 13px;
                padding: 10px;
                background-color: #8A7650;
                color: white;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #7a6640;
            }
            QPushButton:pressed {
                background-color: #6a5630;
            }
            QPushButton:disabled {
                background-color: #ECE7D1;
                color: #999;
            }
        ''')
        self.drop_button.clicked.connect(self.drop_clicked.emit)
        events_layout.addWidget(self.drop_button)

        # 6. Dry End button
        self.dry_end_button = QPushButton('Dry End')
        self.dry_end_button.setStyleSheet('''
            QPushButton {
                font-size: 12px;
                padding: 8px;
                background-color: #8A7650;
                color: white;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #7a6640;
            }
            QPushButton:pressed {
                background-color: #6a5630;
            }
            QPushButton:disabled {
                background-color: #ECE7D1;
                color: #999;
            }
        ''')
        self.dry_end_button.clicked.connect(self.dry_end_clicked.emit)
        events_layout.addWidget(self.dry_end_button)

        return frame

    def create_separator(self) -> QFrame:
        """Create a horizontal separator line"""
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setStyleSheet('background-color: #bdc3c7; max-height: 1px;')
        return separator

    def update_bt(self, value: float):
        """Update BT label with new value"""
        self.bt_label.setText(f'BT: {value:.1f} °C')

    def update_et(self, value: float):
        """Update ET label with new value"""
        self.et_label.setText(f'ET: {value:.1f} °C')

    def update_ror(self, value: float):
        """Update RoR label with new value"""
        self.ror_label.setText(f'RoR: {value:.1f}')

    def update_time(self, seconds: int):
        """Update time label"""
        minutes = seconds // 60
        secs = seconds % 60
        self.time_label.setText(f'Time: {minutes:02d}:{secs:02d}')

    def update_reference(self, profile_name: str):
        """Update reference profile label"""
        self.ref_label.setText(f'Ref: {profile_name}')

    def set_buttons_enabled(self, enabled: bool):
        """Enable or disable all event buttons"""
        # Coffee roasting buttons
        self.charge_button.setEnabled(enabled)
        self.drop_button.setEnabled(enabled)
        self.fc_start_button.setEnabled(enabled)
        self.fc_finish_button.setEnabled(enabled)
        self.sc_start_button.setEnabled(enabled)
        self.dry_end_button.setEnabled(enabled)
