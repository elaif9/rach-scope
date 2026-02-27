"""
Plot Widget - Real-time graph for roasting data using pyqtgraph
"""
import pyqtgraph as pg
from PyQt5.QtWidgets import QWidget, QVBoxLayout
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPen, QColor, QFont
from typing import List, Dict


def hex_to_qcolor(hex_color: str, alpha: int = 255) -> QColor:
    """
    Convert hex color string to QColor

    Args:
        hex_color: Hex color string (e.g., '#e74c3c')
        alpha: Alpha channel (0-255, default: 255)

    Returns:
        QColor object
    """
    # Remove '#' if present
    hex_color = hex_color.lstrip('#')

    # Parse hex values
    if len(hex_color) == 6:
        # RGB format: RRGGBB
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
    elif len(hex_color) == 3:
        # Short format: RGB
        r = int(hex_color[0] * 2, 16)
        g = int(hex_color[1] * 2, 16)
        b = int(hex_color[2] * 2, 16)
    else:
        # Default to black if invalid format
        return QColor(0, 0, 0, alpha)

    return QColor(r, g, b, alpha)


class PlotWidget(QWidget):
    """Widget for plotting real-time roasting data with pyqtgraph"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.event_markers: List[Dict] = []  # Store event marker references
        self.init_ui()
        self.init_plot_items()

    def init_ui(self):
        """Initialize the plot widget UI"""
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        # Create pyqtgraph PlotWidget
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setBackground('#f8f9fa')
        self.plot_widget.showGrid(x=True, y=True, alpha=0.3)

        # Setup plot labels
        self.plot_widget.setLabel('left', 'Temperature', units='°C')
        self.plot_widget.setLabel('bottom', 'Time', units='s')
        self.plot_widget.setTitle('Roasting Profile', color='#2c3e50', size='14pt')

        # Enable legend
        self.legend = self.plot_widget.addLegend(offset=(10, 10))

        # Add plot widget to layout
        layout.addWidget(self.plot_widget)

    def init_plot_items(self):
        """Initialize all plot items (6 lines: 3 live, 3 reference)"""
        # Define colors for each data type
        # BT: Red (#e74c3c), ET: Blue (#3498db), RoR: Green (#27ae60)

        # ============================
        # LIVE DATA (Solid lines)
        # ============================

        # Live BT - Solid Red line
        bt_color = hex_to_qcolor('#e74c3c')
        self.live_bt = self.plot_widget.plot(
            pen=QPen(bt_color, 2, Qt.SolidLine),
            name='BT (Live)',
            symbol='o',
            symbolSize=5,
            symbolBrush=bt_color
        )

        # Live ET - Solid Blue line
        et_color = hex_to_qcolor('#3498db')
        self.live_et = self.plot_widget.plot(
            pen=QPen(et_color, 2, Qt.SolidLine),
            name='ET (Live)',
            symbol='s',
            symbolSize=5,
            symbolBrush=et_color
        )

        # Live RoR - Solid Green line (with scaling factor for visibility)
        ror_color = hex_to_qcolor('#27ae60')
        self.live_ror = self.plot_widget.plot(
            pen=QPen(ror_color, 2, Qt.SolidLine),
            name='RoR (Live)',
            symbol='t',
            symbolSize=5,
            symbolBrush=ror_color
        )

        # ============================
        # REFERENCE DATA (Dashed/Transparent lines)
        # ============================

        # Reference BT - Dashed Red line (semi-transparent)
        bt_color_ref = hex_to_qcolor('#e74c3c', 128)
        self.ref_bt = self.plot_widget.plot(
            pen=QPen(bt_color_ref, 2, Qt.DashLine),
            name='BT (Ref)',
            symbol=None
        )

        # Reference ET - Dashed Blue line (semi-transparent)
        et_color_ref = hex_to_qcolor('#3498db', 128)
        self.ref_et = self.plot_widget.plot(
            pen=QPen(et_color_ref, 2, Qt.DashLine),
            name='ET (Ref)',
            symbol=None
        )

        # Reference RoR - Dashed Green line (semi-transparent)
        ror_color_ref = hex_to_qcolor('#27ae60', 128)
        self.ref_ror = self.plot_widget.plot(
            pen=QPen(ror_color_ref, 2, Qt.DashLine),
            name='RoR (Ref)',
            symbol=None
        )

        # Add view box for RoR secondary axis (optional)
        self.setup_secondary_axis()

    def setup_secondary_axis(self):
        """Setup secondary axis for RoR display"""
        # Create a secondary view box for RoR
        self.plot_widget.showGrid(x=True, y=True, alpha=0.3)
        self.plot_widget.setXRange(0, 60)
        self.plot_widget.setYRange(0, 250)

    def update_live_bt(self, x_data, y_data):
        """Update live BT plot"""
        self.live_bt.setData(x_data, y_data)

    def update_live_et(self, x_data, y_data):
        """Update live ET plot"""
        self.live_et.setData(x_data, y_data)

    def update_live_ror(self, x_data, y_data):
        """Update live RoR plot"""
        self.live_ror.setData(x_data, y_data)

    def update_ref_bt(self, x_data, y_data):
        """Update reference BT plot"""
        self.ref_bt.setData(x_data, y_data)

    def update_ref_et(self, x_data, y_data):
        """Update reference ET plot"""
        self.ref_et.setData(x_data, y_data)

    def update_ref_ror(self, x_data, y_data):
        """Update reference RoR plot"""
        self.ref_ror.setData(x_data, y_data)

    def update_all_live(self, x_data, bt_data, et_data, ror_data):
        """Update all live plots at once"""
        self.live_bt.setData(x_data, bt_data)
        self.live_et.setData(x_data, et_data)
        self.live_ror.setData(x_data, ror_data)

    def update_all_reference(self, x_data, bt_data, et_data, ror_data):
        """Update all reference plots at once"""
        self.ref_bt.setData(x_data, bt_data)
        self.ref_et.setData(x_data, et_data)
        self.ref_ror.setData(x_data, ror_data)

    # ============================
    # EVENT MARKERS (Vertical Lines)
    # ============================

    def add_event_marker(self, x_pos: float, name: str, color: str = '#9b59b6'):
        """
        Add a vertical event marker at specified x position

        Args:
            x_pos: X position (time in seconds)
            name: Event name to display
            color: Color of marker line (default: purple)
        """
        # Convert hex color
        marker_color = hex_to_qcolor(color)

        # Create infinite vertical line
        marker = pg.InfiniteLine(
            pos=x_pos,
            angle=90,
            pen=QPen(marker_color, 2, Qt.DashLine),
            movable=False
        )
        self.plot_widget.addItem(marker)

        # Create text label for event
        label = pg.TextItem(
            text=name,
            color=marker_color,
            anchor=(0, 0),
            fill=QColor(255, 255, 255, 200)
        )
        label.setFont(QFont('Arial', 10, QFont.Bold))
        label.setPos(x_pos, 230)  # Position label at top of graph
        self.plot_widget.addItem(label)

        # Store marker reference for later removal
        self.event_markers.append({
            'line': marker,
            'label': label,
            'x_pos': x_pos,
            'name': name
        })

        return marker

    def add_event_marker_with_bt(self, x_pos: float, name: str, bt: float, color: str = '#9b59b6'):
        """
        Add a vertical event marker with BT temperature label

        Args:
            x_pos: X position (time in seconds)
            name: Event name
            bt: Bean temperature at event
            color: Color of marker line (default: purple)
        """
        # Convert hex color
        marker_color = hex_to_qcolor(color)

        # Create infinite vertical line
        marker = pg.InfiniteLine(
            pos=x_pos,
            angle=90,
            pen=QPen(marker_color, 2, Qt.DashLine),
            movable=False
        )
        self.plot_widget.addItem(marker)

        # Create text label with event name and BT
        label_text = f"{name}\n{bt:.0f}°C"
        label = pg.TextItem(
            text=label_text,
            color=marker_color,
            anchor=(0, 0),
            fill=QColor(255, 255, 255, 200)
        )
        label.setFont(QFont('Arial', 9, QFont.Bold))
        label.setPos(x_pos, bt + 10)  # Position label just above BT value
        self.plot_widget.addItem(label)

        # Store marker reference for later removal
        self.event_markers.append({
            'line': marker,
            'label': label,
            'x_pos': x_pos,
            'name': name,
            'bt': bt
        })

        return marker

    def clear_event_markers(self):
        """Clear all event markers from the plot"""
        for marker in self.event_markers:
            self.plot_widget.removeItem(marker['line'])
            self.plot_widget.removeItem(marker['label'])
        self.event_markers.clear()

    def get_event_markers(self) -> List[Dict]:
        """Get all event markers"""
        return self.event_markers

    # ============================
    # PLOT MANAGEMENT
    # ============================

    def clear_reference_plots(self):
        """Clear all reference plots"""
        self.ref_bt.setData([], [])
        self.ref_et.setData([], [])
        self.ref_ror.setData([], [])

    def clear_live_plots(self):
        """Clear all live plots"""
        self.live_bt.setData([], [])
        self.live_et.setData([], [])
        self.live_ror.setData([], [])
        self.clear_event_markers()

    def clear_all_plots(self):
        """Clear all plots"""
        self.clear_live_plots()
        self.clear_reference_plots()

    def set_x_range(self, min_val, max_val):
        """Set x-axis range"""
        self.plot_widget.setXRange(min_val, max_val)

    def set_y_range(self, min_val, max_val):
        """Set y-axis range"""
        self.plot_widget.setYRange(min_val, max_val)

    def enable_auto_range(self):
        """Enable auto-scaling for both axes"""
        self.plot_widget.enableAutoRange()

    def get_plot_widget(self):
        """Get the underlying pyqtgraph PlotWidget"""
        return self.plot_widget
