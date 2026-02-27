"""
Main Window - Combines control panel and plot widget with full integration
"""
from typing import Optional
from PyQt5.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, QMenuBar,
                             QMenu, QAction, QToolBar, QStatusBar,
                             QFileDialog, QMessageBox, QLabel, QApplication, QDialog)
from PyQt5.QtCore import Qt, QSize, QTimer
from PyQt5.QtGui import QIcon

from .control_panel import ControlPanel
from .plot_widget import PlotWidget
from .settings_dialog import SettingsDialog
from core.models import EventType, RoastEvent


class MainWindow(QMainWindow):
    """Main application window for Rach Scope"""

    def __init__(self):
        super().__init__()

        # Core components (will be initialized from main.py)
        self.config_manager = None
        self.modbus_reader = None
        self.data_manager = None

        # UI components
        self.control_panel = None
        self.plot_widget = None

        # Timer for data reading
        self.read_timer = QTimer()
        self.read_timer.setInterval(1000)  # 1 second interval
        self.read_timer.timeout.connect(self.on_timer_tick)

        # State
        self.is_roasting = False
        self.is_connected = False

        # Coffee roasting state tracking
        self.fc_start_time: Optional[float] = None
        self.sc_start_time: Optional[float] = None
        self.fc_start_event: Optional[RoastEvent] = None
        self.sc_start_event: Optional[RoastEvent] = None
        self.current_stage = "IDLE"

        self.init_ui()

    def init_ui(self):
        """Initialize the user interface"""
        # Window setup
        self.setWindowTitle('Rach Scope - Coffee Roasting Monitor')
        self.setGeometry(100, 100, 1200, 800)

        # Create central widget and layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(5, 5, 5, 5)
        self.main_layout.setSpacing(5)

        # Setup menu bar
        self.setup_menu_bar()

        # Setup toolbar
        self.setup_toolbar()

        # Setup status bar
        self.setup_status_bar()

        # Create control panel (left side)
        self.control_panel = ControlPanel()
        self.control_panel.setFixedWidth(280)
        self.main_layout.addWidget(self.control_panel)

        # Create plot widget (right side)
        self.plot_widget = PlotWidget()
        self.main_layout.addWidget(self.plot_widget, stretch=1)

        # Connect control panel signals
        self.control_panel.dry_end_clicked.connect(lambda: self.on_mark_event("Dry End", "#9b59b6"))

        # Connect coffee roasting button signals
        self.control_panel.charge_clicked.connect(self.on_charge)
        self.control_panel.drop_clicked.connect(self.on_drop)
        self.control_panel.fc_start_clicked.connect(self.on_fc_start)
        self.control_panel.fc_finish_clicked.connect(self.on_fc_finish)
        self.control_panel.sc_start_clicked.connect(self.on_sc_start)

    # ============================
    # INITIALIZATION (called from main.py)
    # ============================

    def set_components(self, config_manager, modbus_reader, data_manager):
        """
        Set core components from main.py

        Args:
            config_manager: ConfigManager instance
            modbus_reader: ModbusReader instance
            data_manager: DataManager instance
        """
        self.config_manager = config_manager
        self.modbus_reader = modbus_reader
        self.data_manager = data_manager

        # Update reader config from settings
        self._update_reader_config()

        # Try to connect to hardware
        self._connect_to_hardware()

    def _update_reader_config(self):
        """Update modbus reader config from config manager"""
        if self.config_manager and self.modbus_reader:
            self.modbus_reader.update_config(
                ip=self.config_manager.get('ip'),
                port=self.config_manager.get('port'),
                slave_id_bt=self.config_manager.get('slave_id_bt', 1),
                slave_id_et=self.config_manager.get('slave_id_et', 1),
                reg_bt=self.config_manager.get('reg_bt'),
                reg_et=self.config_manager.get('reg_et'),
                scale=self.config_manager.get('scale')
            )

    def _connect_to_hardware(self) -> bool:
        """Connect to hardware and update status"""
        if self.modbus_reader:
            self.is_connected = self.modbus_reader.connect()
            self.update_connection_status()
            return self.is_connected
        return False

    # ============================
    # UI SETUP
    # ============================

    def setup_menu_bar(self):
        """Setup the menu bar with File, Settings, and Help menus"""
        menubar = self.menuBar()

        # File Menu
        file_menu = menubar.addMenu('&File')

        new_roast_action = QAction('&New Roast', self)
        new_roast_action.setShortcut('Ctrl+N')
        new_roast_action.setStatusTip('Start a new roast')
        new_roast_action.triggered.connect(self.on_new_roast)
        file_menu.addAction(new_roast_action)

        save_action = QAction('&Save', self)
        save_action.setShortcut('Ctrl+S')
        save_action.setStatusTip('Save roast data')
        save_action.triggered.connect(self.on_save)
        file_menu.addAction(save_action)

        save_as_action = QAction('Save &As...', self)
        save_as_action.setShortcut('Ctrl+Shift+S')
        save_as_action.setStatusTip('Save roast data as...')
        save_as_action.triggered.connect(self.on_save_as)
        file_menu.addAction(save_as_action)

        file_menu.addSeparator()

        load_profile_action = QAction('Load &Profile...', self)
        load_profile_action.setShortcut('Ctrl+O')
        load_profile_action.setStatusTip('Load a reference profile')
        load_profile_action.triggered.connect(self.on_load_profile)
        file_menu.addAction(load_profile_action)

        file_menu.addSeparator()

        exit_action = QAction('E&xit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.setStatusTip('Exit application')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Settings Menu
        settings_menu = menubar.addMenu('&Settings')

        hardware_action = QAction('&Hardware Settings', self)
        hardware_action.setStatusTip('Configure hardware connection')
        hardware_action.triggered.connect(self.on_hardware_settings)
        settings_menu.addAction(hardware_action)

        reconnect_action = QAction('&Reconnect Hardware', self)
        reconnect_action.setStatusTip('Reconnect to hardware')
        reconnect_action.triggered.connect(self._connect_to_hardware)
        settings_menu.addAction(reconnect_action)

        # Help Menu
        help_menu = menubar.addMenu('&Help')

        about_action = QAction('&About', self)
        about_action.setStatusTip('About Rach Scope')
        about_action.triggered.connect(self.on_about)
        help_menu.addAction(about_action)

    def setup_toolbar(self):
        """Setup the toolbar with main action buttons"""
        self.toolbar = QToolBar('Main Toolbar')
        self.toolbar.setMovable(False)
        self.toolbar.setIconSize(QSize(32, 32))
        self.addToolBar(self.toolbar)

        # Start button
        self.start_action = QAction('Start', self)
        self.start_action.setStatusTip('Start roasting')
        self.start_action.triggered.connect(self.on_start)
        self.toolbar.addAction(self.start_action)

        # Stop button
        self.stop_action = QAction('Stop', self)
        self.stop_action.setStatusTip('Stop roasting')
        self.stop_action.setEnabled(False)
        self.stop_action.triggered.connect(self.on_stop)
        self.toolbar.addAction(self.stop_action)

        self.toolbar.addSeparator()

        # Save button
        self.save_action = QAction('Save', self)
        self.save_action.setStatusTip('Save roast data')
        self.save_action.triggered.connect(self.on_save)
        self.toolbar.addAction(self.save_action)

        # Load Profile button
        self.load_action = QAction('Load Profile', self)
        self.load_action.setStatusTip('Load reference profile')
        self.load_action.triggered.connect(self.on_load_profile)
        self.toolbar.addAction(self.load_action)

        # Settings button
        self.toolbar.addSeparator()
        self.settings_action = QAction('Settings', self)
        self.settings_action.setStatusTip('Hardware configuration')
        self.settings_action.triggered.connect(self.on_hardware_settings)
        self.toolbar.addAction(self.settings_action)

    def setup_status_bar(self):
        """Setup the status bar"""
        self.status_bar = QStatusBar()

        # Connection status label
        self.connection_label = QLabel('Not Connected')
        self.connection_label.setStyleSheet('color: #e74c3c; font-weight: bold; padding: 2px 8px;')
        self.status_bar.addPermanentWidget(self.connection_label)

        # Message label
        self.status_bar.showMessage('Ready')

    # ============================
    # TIMER LOOP
    # ============================

    def on_timer_tick(self):
        """Called every second by the timer to read data"""
        if not self.modbus_reader or not self.data_manager:
            return

        # Read data from hardware
        bt, et = self.modbus_reader.read_once()

        # Handle connection status
        if bt is None or et is None:
            self.is_connected = False
            self.update_connection_status()
            self.status_bar.showMessage('Error reading from hardware')
            return

        self.is_connected = True
        self.update_connection_status()

        # Add data point to manager (RoR calculated automatically)
        self.data_manager.add_data_point(bt, et)

        # Get latest data for UI update
        latest = self.data_manager.get_latest_data()
        if latest:
            # Update control panel
            self.control_panel.update_bt(latest.bt)
            self.control_panel.update_et(latest.et)
            self.control_panel.update_ror(latest.ror)

            # Update time display
            elapsed = int(self.data_manager.get_elapsed_time())
            self.control_panel.update_time(elapsed)

            # Update live plot
            plot_data = self.data_manager.get_live_for_plotting()
            self.plot_widget.update_all_live(
                plot_data['time'],
                plot_data['bt'],
                plot_data['et'],
                plot_data['ror']
            )

    # ============================
    # ACTION HANDLERS
    # ============================

    def on_start(self):
        """Handle Start button click"""
        # Check if connected to hardware
        if not self.is_connected:
            # Try to reconnect first
            reconnect_success = self._connect_to_hardware()

            if not reconnect_success:
                # Build detailed error message
                error_msg = "<h3>Hardware Connection Failed</h3>"

                if self.modbus_reader and self.modbus_reader.last_connection_error:
                    error_msg += f"<p><b>Error:</b> {self.modbus_reader.last_connection_error}</p>"
                else:
                    error_msg += "<p><b>Error:</b> Cannot establish connection to hardware.</p>"

                # Add current settings
                if self.config_manager:
                    ip = self.config_manager.get('ip', 'Unknown')
                    port = self.config_manager.get('port', 502)
                    error_msg += f"<p><b>Current Settings:</b><br>IP: {ip}<br>Port: {port}</p>"

                # Add troubleshooting steps
                error_msg += """
                <p><b>Troubleshooting Steps:</b></p>
                <ul>
                    <li>Check if the hardware device is powered on</li>
                    <li>Verify the IP address and port in Settings</li>
                    <li>Check network cable or WiFi connection</li>
                    <li>Try clicking 'Settings' to configure hardware</li>
                    <li>Try clicking 'Reconnect Hardware' in Settings menu</li>
                </ul>
                """

                QMessageBox.critical(self, 'Connection Error', error_msg)
                return

        # Reset data and start new roast
        self.data_manager.start_roast()
        self.plot_widget.clear_live_plots()

        # Reset coffee roasting state
        self.fc_start_time = None
        self.sc_start_time = None
        self.fc_start_event = None
        self.sc_start_event = None
        self.current_stage = "IDLE"

        # Update button states
        self.is_roasting = True
        self.start_action.setEnabled(False)
        self.stop_action.setEnabled(True)
        self.control_panel.set_buttons_enabled(True)

        # Start timer
        self.read_timer.start()
        self.status_bar.showMessage('Roasting started...')

    def on_stop(self):
        """Handle Stop button click"""
        # Stop timer
        self.read_timer.stop()

        # Update button states
        self.is_roasting = False
        self.start_action.setEnabled(True)
        self.stop_action.setEnabled(False)
        self.control_panel.set_buttons_enabled(False)

        # Reset stage
        self.current_stage = "IDLE"

        # Show statistics
        if self.modbus_reader:
            stats = self.modbus_reader.get_statistics()
            self.status_bar.showMessage(
                f'Roasting stopped. Reads: {stats["total_reads"]}, Rate: {stats["read_rate_per_second"]:.1f}/sec'
            )
        else:
            self.status_bar.showMessage('Roasting stopped')

    def on_save(self):
        """Handle Save action"""
        if self.is_roasting:
            QMessageBox.warning(self, 'Warning', 'Cannot save while roasting is in progress')
            return

        if not self.data_manager.get_live_data():
            QMessageBox.warning(self, 'Warning', 'No data to save')
            return

        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getSaveFileName(
            self,
            'Save Roast Data',
            '',
            'CSV Files (*.csv);;All Files (*)',
            options=options
        )

        if file_name:
            if not file_name.endswith('.csv'):
                file_name += '.csv'

            if self.data_manager.save_csv(file_name):
                self.status_bar.showMessage(f'Saved to: {file_name}')
            else:
                QMessageBox.critical(self, 'Error', 'Failed to save file')

    def on_save_as(self):
        """Handle Save As action"""
        self.on_save()

    def on_new_roast(self):
        """Handle New Roast action"""
        if self.is_roasting:
            reply = QMessageBox.question(
                self,
                'Confirm',
                'Roasting is in progress. Stop and create new roast?',
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.No:
                return
            self.on_stop()

        # Clear data and plots
        if self.data_manager:
            self.data_manager.clear_live_data()
        self.plot_widget.clear_live_plots()

        # Reset control panel
        self.control_panel.update_bt(0)
        self.control_panel.update_et(0)
        self.control_panel.update_ror(0)
        self.control_panel.update_time(0)

        self.status_bar.showMessage('New roast ready')

    def on_load_profile(self):
        """Handle Load Profile action"""
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            'Load Reference Profile',
            '',
            'CSV Files (*.csv);;All Files (*)',
            options=options
        )

        if file_name and self.data_manager:
            # Load CSV to reference data
            if self.data_manager.load_csv(file_name):
                # Get filename for display
                import os
                profile_name = os.path.basename(file_name)
                self.control_panel.update_reference(profile_name)

                # Plot reference data as dashed lines
                plot_data = self.data_manager.get_reference_for_plotting()
                self.plot_widget.update_all_reference(
                    plot_data['time'],
                    plot_data['bt'],
                    plot_data['et'],
                    plot_data['ror']
                )

                # Set X range based on reference data
                if plot_data['time']:
                    max_time = max(plot_data['time'])
                    self.plot_widget.set_x_range(0, max_time + 60)

                self.status_bar.showMessage(f'Loaded profile: {profile_name}')
            else:
                QMessageBox.critical(self, 'Error', 'Failed to load profile')

    def on_mark_event(self, event_name: str, color: str):
        """
        Handle event button clicks

        Args:
            event_name: Name of the event
            color: Color for the event marker
        """
        if not self.data_manager or not self.is_roasting:
            return

        # Get latest BT temperature
        latest = self.data_manager.get_latest_data()
        if latest:
            # Add event to data manager
            self.data_manager.add_event(
                name=event_name,
                bt=latest.bt,
                et=latest.et,
                description=""
            )

            # Get elapsed time
            elapsed = self.data_manager.get_elapsed_time()

            # Add vertical marker to plot
            self.plot_widget.add_event_marker_with_bt(
                x_pos=elapsed,
                name=event_name,
                bt=latest.bt,
                color=color
            )

            self.status_bar.showMessage(f'Event marked: {event_name} at {latest.bt:.1f}°C')

    # ============================
    # COFFEE ROASTING EVENT HANDLERS
    # ============================

    def on_charge(self):
        """Handle Charge button click - when coffee beans are added"""
        if not self.data_manager or not self.is_roasting:
            return

        latest = self.data_manager.get_latest_data()
        if latest:
            # Add CHARGE event
            event = self.data_manager.add_event(
                name="Charge",
                bt=latest.bt,
                et=latest.et,
                event_type=EventType.CHARGE
            )

            # Get elapsed time and add marker
            elapsed = self.data_manager.get_elapsed_time()
            self.plot_widget.add_event_marker_with_bt(
                x_pos=elapsed,
                name="Charge",
                bt=latest.bt,
                color="#2ecc71"
            )

            self.current_stage = "CHARGING"
            self.status_bar.showMessage(f'Charge marked at {latest.bt:.1f}°C')

    def on_drop(self):
        """Handle Drop button click - when coffee beans are dropped"""
        if not self.data_manager or not self.is_roasting:
            return

        latest = self.data_manager.get_latest_data()
        if latest:
            # Add DROP event
            event = self.data_manager.add_event(
                name="Drop",
                bt=latest.bt,
                et=latest.et,
                event_type=EventType.DROP
            )

            # Get elapsed time and add marker
            elapsed = self.data_manager.get_elapsed_time()
            self.plot_widget.add_event_marker_with_bt(
                x_pos=elapsed,
                name="Drop",
                bt=latest.bt,
                color="#e67e22"
            )

            self.current_stage = "COOLING"
            self.status_bar.showMessage(f'Drop marked at {latest.bt:.1f}°C')

    def on_fc_start(self):
        """Handle FC Start button click - First Crack start"""
        if not self.data_manager or not self.is_roasting:
            return

        latest = self.data_manager.get_latest_data()
        if latest:
            # Record FC start
            elapsed = self.data_manager.get_elapsed_time()
            self.fc_start_time = elapsed
            self.fc_start_event = self.data_manager.add_event(
                name="FC Start",
                bt=latest.bt,
                et=latest.et,
                event_type=EventType.FC_START
            )

            # Add marker
            self.plot_widget.add_event_marker_with_bt(
                x_pos=elapsed,
                name="FC Start",
                bt=latest.bt,
                color="#8e44ad"
            )

            self.current_stage = "FC ROASTING"
            self.status_bar.showMessage(f'FC Start marked at {latest.bt:.1f}°C')

    def on_fc_finish(self):
        """Handle FC Finish button click - First Crack end"""
        if not self.data_manager or not self.is_roasting or self.fc_start_time is None:
            return

        latest = self.data_manager.get_latest_data()
        if latest:
            # Calculate end time and add FC_FINISH event
            elapsed = self.data_manager.get_elapsed_time()
            end_time = elapsed - self.fc_start_time
            end_bt = latest.bt

            event = self.data_manager.add_event(
                name="FC Finish",
                bt=latest.bt,
                et=latest.et,
                event_type=EventType.FC_FINISH,
                end_bt=end_bt,
                end_time=end_time
            )

            # Add marker
            self.plot_widget.add_event_marker_with_bt(
                x_pos=elapsed,
                name="FC Finish",
                bt=latest.bt,
                color="#c0392b"
            )

            self.current_stage = "DEVELOPMENT"
            self.status_bar.showMessage(f'FC Finish at {latest.bt:.1f}°C (Duration: {end_time:.1f}s)')

    def on_sc_start(self):
        """Handle SC Start button click - Second Crack start"""
        if not self.data_manager or not self.is_roasting:
            return

        latest = self.data_manager.get_latest_data()
        if latest:
            # Record SC start
            elapsed = self.data_manager.get_elapsed_time()
            self.sc_start_time = elapsed
            self.sc_start_event = self.data_manager.add_event(
                name="SC Start",
                bt=latest.bt,
                et=latest.et,
                event_type=EventType.SC_START
            )

            # Add marker
            self.plot_widget.add_event_marker_with_bt(
                x_pos=elapsed,
                name="SC Start",
                bt=latest.bt,
                color="#8e44ad"
            )

            self.current_stage = "SC ROASTING"
            self.status_bar.showMessage(f'SC Start marked at {latest.bt:.1f}°C')

    def on_hardware_settings(self):
        """Handle Hardware Settings action"""
        self.status_bar.showMessage('Opening hardware settings...')

        # Create settings dialog
        dialog = SettingsDialog(self)

        # Load current configuration
        if self.config_manager:
            current_config = {
                'ip': self.config_manager.get('ip'),
                'port': self.config_manager.get('port'),
                'slave_id_bt': self.config_manager.get('slave_id_bt', 1),
                'slave_id_et': self.config_manager.get('slave_id_et', 1),
                'reg_bt': self.config_manager.get('reg_bt'),
                'reg_et': self.config_manager.get('reg_et'),
                'scale': self.config_manager.get('scale')
            }
            dialog.set_data(current_config)

        # Show dialog and wait for result
        if dialog.exec_() == QDialog.Accepted:
            # Get new configuration
            new_config = dialog.get_data()

            # Validate IP address
            if not new_config['ip']:
                QMessageBox.warning(self, 'Invalid Input', 'IP Address cannot be empty')
                return

            # Save configuration
            if self.config_manager:
                self.config_manager.update(new_config)

                # Update modbus reader with new configuration
                if self.modbus_reader:
                    self.modbus_reader.update_config(
                        ip=new_config['ip'],
                        port=new_config['port'],
                        slave_id_bt=new_config['slave_id_bt'],
                        slave_id_et=new_config['slave_id_et'],
                        reg_bt=new_config['reg_bt'],
                        reg_et=new_config['reg_et'],
                        scale=new_config['scale']
                    )

            self.status_bar.showMessage(f'Settings saved: {new_config["ip"]}:{new_config["port"]}')

            # If currently connected, try to reconnect with new settings
            if self.is_connected:
                self._connect_to_hardware()
        else:
            self.status_bar.showMessage('Settings cancelled')

    def on_about(self):
        """Handle About action"""
        QMessageBox.about(
            self,
            'About Rach Scope',
            '<h3>Rach Scope</h3>'
            '<p>Coffee Roasting Monitoring Application</p>'
            '<p>Version: 1.0.0</p>'
            '<p>Real-time visualization of BT, ET, and RoR data from HF2211 hardware.</p>'
        )

    # ============================
    # STATUS UPDATE
    # ============================

    def update_connection_status(self):
        """Update connection status in status bar"""
        if self.is_connected:
            ip = self.config_manager.get('ip', '') if self.config_manager else ''
            self.connection_label.setText(f'Connected to {ip}')
            self.connection_label.setStyleSheet('color: #27ae60; font-weight: bold; padding: 2px 8px;')
        else:
            self.connection_label.setText('Disconnected')
            self.connection_label.setStyleSheet('color: #e74c3c; font-weight: bold; padding: 2px 8px;')

    # ============================
    # GETTERS
    # ============================

    def get_control_panel(self) -> ControlPanel:
        """Get the control panel widget"""
        return self.control_panel

    def get_plot_widget(self) -> PlotWidget:
        """Get the plot widget"""
        return self.plot_widget
