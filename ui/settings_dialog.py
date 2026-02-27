"""
Settings Dialog - Hardware configuration dialog
"""
from PyQt5.QtWidgets import (QDialog, QFormLayout, QLineEdit, QSpinBox,
                             QDoubleSpinBox, QDialogButtonBox, QVBoxLayout,
                             QLabel, QGroupBox, QWidget)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from typing import Dict


class SettingsDialog(QDialog):
    """Dialog for configuring hardware connection settings"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Hardware Settings')
        self.setModal(True)
        self.setMinimumWidth(400)

        self.init_ui()

    def init_ui(self):
        """Initialize the settings dialog UI"""
        # Main layout
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        # Create form layout
        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        form_layout.setContentsMargins(20, 20, 20, 20)

        # ============================
        # CONNECTION SETTINGS
        # ============================

        connection_group = QGroupBox('Connection')
        connection_group.setStyleSheet('''
            QGroupBox {
                font-weight: bold;
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                margin-top: 10px;
                padding: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        ''')

        # IP Address
        self.ip_input = QLineEdit()
        self.ip_input.setPlaceholderText('192.168.1.100')
        self.ip_input.setMinimumWidth(200)
        form_layout.addRow('IP Address:', self.ip_input)

        # Port
        self.port_input = QSpinBox()
        self.port_input.setRange(1, 65535)
        self.port_input.setValue(502)
        self.port_input.setMinimumWidth(150)
        form_layout.addRow('Port:', self.port_input)

        connection_group.setLayout(form_layout)
        main_layout.addWidget(connection_group)

        # ============================
        # MODBUS PARAMETERS
        # ============================

        modbus_layout = QFormLayout()
        modbus_layout.setSpacing(10)
        modbus_layout.setContentsMargins(20, 20, 20, 20)

        modbus_group = QGroupBox('Modbus Parameters')
        modbus_group.setStyleSheet('''
            QGroupBox {
                font-weight: bold;
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                margin-top: 10px;
                padding: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        ''')

        # Slave ID for BT (Bean Temperature)
        self.slave_id_bt_input = QSpinBox()
        self.slave_id_bt_input.setRange(0, 247)
        self.slave_id_bt_input.setValue(1)
        self.slave_id_bt_input.setMinimumWidth(150)
        self.slave_id_bt_input.setPrefix('BT: ')
        modbus_layout.addRow('Slave ID for BT:', self.slave_id_bt_input)

        # Slave ID for ET (Environmental Temperature)
        self.slave_id_et_input = QSpinBox()
        self.slave_id_et_input.setRange(0, 247)
        self.slave_id_et_input.setValue(1)
        self.slave_id_et_input.setMinimumWidth(150)
        self.slave_id_et_input.setPrefix('ET: ')
        modbus_layout.addRow('Slave ID for ET:', self.slave_id_et_input)

        # Scale Factor
        self.scale_input = QDoubleSpinBox()
        self.scale_input.setRange(0.1, 1000.0)
        self.scale_input.setValue(10.0)
        self.scale_input.setSingleStep(0.1)
        self.scale_input.setDecimals(1)
        self.scale_input.setMinimumWidth(150)
        modbus_layout.addRow('Scale Factor:', self.scale_input)

        modbus_group.setLayout(modbus_layout)
        main_layout.addWidget(modbus_group)

        # ============================
        # REGISTER SETTINGS
        # ============================

        register_layout = QFormLayout()
        register_layout.setSpacing(10)
        register_layout.setContentsMargins(20, 20, 20, 20)

        register_group = QGroupBox('Registers')
        register_group.setStyleSheet('''
            QGroupBox {
                font-weight: bold;
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                margin-top: 10px;
                padding: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        ''')

        # BT Register
        self.bt_register_input = QSpinBox()
        self.bt_register_input.setRange(0, 65535)
        self.bt_register_input.setValue(0)
        self.bt_register_input.setMinimumWidth(150)
        register_layout.addRow('BT Register:', self.bt_register_input)

        # ET Register
        self.et_register_input = QSpinBox()
        self.et_register_input.setRange(0, 65535)
        self.et_register_input.setValue(0)
        self.et_register_input.setMinimumWidth(150)
        register_layout.addRow('ET Register:', self.et_register_input)

        register_group.setLayout(register_layout)
        main_layout.addWidget(register_group)

        # Add description/help text
        help_label = QLabel('''
            <p style="color: #7f8c8d; font-size: 11px; margin-top: 10px;">
            <i>Configure your HF2211 device connection settings.</i><br><br>
            <i>Set different Slave IDs for BT and ET if needed.</i><br><br>
            <i>Changes will be saved to settings.json.</i>
            </p>
        ''')
        help_label.setWordWrap(True)
        help_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(help_label)

        # ============================
        # BUTTON BOX
        # ============================

        button_box = QDialogButtonBox(
            QDialogButtonBox.Save | QDialogButtonBox.Cancel
        )
        button_box.setOrientation(Qt.Horizontal)

        # Style the buttons
        save_button = button_box.button(QDialogButtonBox.Save)
        save_button.setStyleSheet('''
            QPushButton {
                background-color: #27ae60;
                color: white;
                padding: 8px 16px;
                font-weight: bold;
                border-radius: 4px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #219150;
            }
            QPushButton:pressed {
                background-color: #1e8449;
            }
        ''')

        cancel_button = button_box.button(QDialogButtonBox.Cancel)
        cancel_button.setStyleSheet('''
            QPushButton {
                background-color: #e74c3c;
                color: white;
                padding: 8px 16px;
                font-weight: bold;
                border-radius: 4px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
            QPushButton:pressed {
                background-color: #a93226;
            }
        ''')

        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        main_layout.addWidget(button_box)

    def set_data(self, config: Dict):
        """
        Fill form fields with configuration data

        Args:
            config: Dictionary containing configuration values
        """
        # Connection settings
        if 'ip' in config:
            self.ip_input.setText(config['ip'])
        if 'port' in config:
            self.port_input.setValue(config['port'])

        # Modbus parameters
        if 'slave_id_bt' in config:
            self.slave_id_bt_input.setValue(config['slave_id_bt'])
        if 'slave_id_et' in config:
            self.slave_id_et_input.setValue(config['slave_id_et'])
        if 'scale' in config:
            self.scale_input.setValue(config['scale'])

        # Register settings
        if 'reg_bt' in config:
            self.bt_register_input.setValue(config['reg_bt'])
        if 'reg_et' in config:
            self.et_register_input.setValue(config['reg_et'])

    def get_data(self) -> Dict:
        """
        Get configuration values from form fields

        Returns:
            Dictionary with all configuration values
        """
        return {
            'ip': self.ip_input.text().strip(),
            'port': self.port_input.value(),
            'slave_id_bt': self.slave_id_bt_input.value(),
            'slave_id_et': self.slave_id_et_input.value(),
            'reg_bt': self.bt_register_input.value(),
            'reg_et': self.et_register_input.value(),
            'scale': self.scale_input.value()
        }
