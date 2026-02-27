"""
Rach Scope - Coffee Roasting Monitoring Application
Entry point for the application
"""
import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt

from ui.main_window import MainWindow
from core.config_manager import ConfigManager
from core.hardware_reader import ModbusReader
from core.data_manager import DataManager


def main():
    """Main entry point for the application"""
    # Enable high DPI scaling BEFORE creating QApplication
    if hasattr(Qt, 'AA_EnableHighDpiScaling'):
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    # Create Qt application
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # Use Fusion style for consistent look across platforms

    # Initialize core components
    print("Initializing Rach Scope...")

    # 1. Load configuration
    config_manager = ConfigManager()
    print(f"  Config loaded: {config_manager.get_config_path()}")

    # 2. Initialize Modbus Reader
    modbus_reader = ModbusReader(
        ip=config_manager.get('ip'),
        port=config_manager.get('port'),
        slave_id_bt=config_manager.get('slave_id_bt', 1),
        slave_id_et=config_manager.get('slave_id_et', 1),
        reg_bt=config_manager.get('reg_bt'),
        reg_et=config_manager.get('reg_et'),
        scale=config_manager.get('scale')
    )
    print(f"  Modbus Reader initialized (IP: {config_manager.get('ip')}:{config_manager.get('port')})")

    # 3. Initialize Data Manager
    data_manager = DataManager()
    print("  Data Manager initialized")

    # 4. Create and setup main window
    window = MainWindow()
    print("  Main Window created")

    # 5. Connect components to window
    window.set_components(config_manager, modbus_reader, data_manager)
    print("  Components connected")

    # 6. Show window
    window.show()
    print("  Window shown")

    print("\nRach Scope is ready!")
    print(f"Hardware IP: {config_manager.get('ip')}:{config_manager.get('port')}")
    print(f"Slave IDs - BT: {config_manager.get('slave_id_bt', 1)}, ET: {config_manager.get('slave_id_et', 1)}")
    print(f"Registers - BT: {config_manager.get('reg_bt')}, ET: {config_manager.get('reg_et')}")
    print(f"Scale Factor: {config_manager.get('scale')}")

    # Run application event loop
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
