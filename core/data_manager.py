"""
Data Manager - Handles live data, reference data, and CSV operations
"""
import csv
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
import logging

from .models import RoastData, RoastEvent, EventType
from utils.path_manager import get_path_manager


class DataManager:
    """
    Manages roasting data including live data collection, reference profiles,
    RoR calculations, and CSV import/export
    """

    def __init__(self, log_file: str = 'data_manager.log'):
        """
        Initialize Data Manager

        Args:
            log_file: Path to log file
        """
        # Live data storage
        self.live_data: List[RoastData] = []
        self.live_events: List[RoastEvent] = []

        # Reference data storage (from loaded CSV)
        self.reference_data: List[RoastData] = []
        self.reference_name: str = ''

        # Start time for roast
        self.start_time: Optional[datetime] = None

        # Path manager for writable directories
        self._path_manager = get_path_manager()

        # Setup logging
        self.logger = self._setup_logging(log_file)

        # CSV column mapping
        self.csv_columns = ['timestamp', 'bt', 'et', 'ror']

    def _setup_logging(self, log_file: str) -> logging.Logger:
        """
        Setup logging to file

        Args:
            log_file: Path to log file

        Returns:
            Configured logger instance
        """
        # Get log file path from path manager
        log_path = self._path_manager.get_log_file(log_file)

        # Ensure log directory exists
        self._path_manager.ensure_dir_exists(log_path.parent)

        logger = logging.getLogger('DataManager')
        logger.setLevel(logging.DEBUG)

        # File handler
        file_handler = logging.FileHandler(log_path)
        file_handler.setLevel(logging.DEBUG)

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)

        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        # Add handlers
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

        return logger

    # ============================
    # LIVE DATA MANAGEMENT
    # ============================

    def start_roast(self):
        """Start a new roast session"""
        self.live_data = []
        self.live_events = []
        self.start_time = datetime.now()
        self.logger.info(f"Roast started at {self.start_time}")

    def add_data_point(self, bt: float, et: float, timestamp: Optional[datetime] = None) -> RoastData:
        """
        Add a new data point with RoR calculation

        Args:
            bt: Bean Temperature
            et: Environmental Temperature
            timestamp: Timestamp for this data point (default: now)

        Returns:
            RoastData object with calculated RoR
        """
        if self.start_time is None:
            self.start_time = datetime.now()

        if timestamp is None:
            timestamp = datetime.now()

        # Calculate RoR
        ror = self.calculate_ror(bt, timestamp)

        # Create data point
        data_point = RoastData(
            timestamp=timestamp,
            bt=bt,
            et=et,
            ror=ror
        )

        self.live_data.append(data_point)
        self.logger.debug(f"Added data point: BT={bt:.1f}°C, ET={et:.1f}°C, RoR={ror:.1f}")

        return data_point

    def calculate_ror(
        self,
        current_bt: float,
        current_time: datetime,
        window_seconds: float = 10.0
    ) -> float:
        """
        Calculate Rate of Rise (RoR)

        RoR = (bt_current - bt_previous) / (time_current - time_previous)
        Uses a sliding window of window_seconds for stability

        Args:
            current_bt: Current bean temperature
            current_time: Current timestamp
            window_seconds: Time window in seconds for RoR calculation (default: 10)

        Returns:
            Rate of Rise in °C/second
        """
        if not self.live_data:
            return 0.0

        # Find the data point that's approximately window_seconds ago
        target_time = current_time - timedelta(seconds=window_seconds)
        previous_data = None

        # Search backwards through data for the closest point
        for data in reversed(self.live_data):
            if data.timestamp <= target_time:
                previous_data = data
                break

        if previous_data is None:
            # Not enough data yet, use the first point
            if len(self.live_data) > 0:
                previous_data = self.live_data[0]
            else:
                return 0.0

        # Calculate time difference in seconds
        time_diff = (current_time - previous_data.timestamp).total_seconds()

        if time_diff <= 0:
            return 0.0

        # Calculate RoR
        ror = (current_bt - previous_data.bt) / time_diff

        return ror

    def add_event(
        self,
        name: str,
        bt: float,
        et: float,
        description: str = "",
        event_type: Optional[EventType] = None,
        end_bt: Optional[float] = None,
        end_time: Optional[float] = None,
        bean_color: Optional[str] = None
    ) -> RoastEvent:
        """
        Add a roast event

        Args:
            name: Event name (e.g., "Dry End", "First Crack")
            bt: Bean temperature at event
            et: Environmental temperature at event
            description: Event description
            event_type: Event type from EventType enum
            end_bt: End temperature for FC/SC operations
            end_time: Elapsed time for FC/SC operations (seconds)
            bean_color: Bean color for tracking

        Returns:
            RoastEvent object
        """
        # Calculate RoR for this event
        timestamp = datetime.now()
        ror = self.calculate_ror(bt, timestamp)

        event = RoastEvent(
            event_type=event_type,
            name=name,
            timestamp=timestamp,
            bt=bt,
            et=et,
            ror=ror,
            description=description,
            end_bt=end_bt,
            end_time=end_time,
            bean_color=bean_color
        )

        self.live_events.append(event)
        self.logger.info(f"Event added: {name} at BT={bt:.1f}°C")

        return event

    def get_live_data(self) -> List[RoastData]:
        """
        Get all live data points

        Returns:
            List of RoastData objects
        """
        return self.live_data

    def get_live_events(self) -> List[RoastEvent]:
        """
        Get all live events

        Returns:
            List of RoastEvent objects
        """
        return self.live_events

    def get_latest_data(self) -> Optional[RoastData]:
        """
        Get the latest data point

        Returns:
            Latest RoastData or None if no data
        """
        if self.live_data:
            return self.live_data[-1]
        return None

    def get_elapsed_time(self) -> float:
        """
        Get elapsed time since roast start

        Returns:
            Elapsed time in seconds
        """
        if self.start_time is None:
            return 0.0
        return (datetime.now() - self.start_time).total_seconds()

    def clear_live_data(self):
        """Clear all live data"""
        self.live_data = []
        self.live_events = []
        self.start_time = None
        self.logger.info("Live data cleared")

    # ============================
    # REFERENCE DATA MANAGEMENT
    # ============================

    def load_csv(self, file_path: str) -> bool:
        """
        Load CSV file into reference data

        Expected CSV format: timestamp, bt, et, ror
        Timestamp can be ISO format or elapsed seconds

        Args:
            file_path: Path to CSV file

        Returns:
            True if load successful, False otherwise
        """
        try:
            self.reference_data = []

            # Get filename for reference name
            import os
            self.reference_name = os.path.basename(file_path)

            with open(file_path, 'r', newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)

                # Check required columns
                required_cols = ['bt', 'et']
                fieldnames = reader.fieldnames if reader.fieldnames else []
                if not all(col in fieldnames for col in required_cols):
                    self.logger.error(f"CSV must contain columns: {required_cols}")
                    return False

                for row_num, row in enumerate(reader, 1):
                    try:
                        # Parse timestamp
                        if 'timestamp' in row and row['timestamp']:
                            try:
                                # Try ISO format first
                                timestamp = datetime.fromisoformat(row['timestamp'].replace('Z', '+00:00'))
                            except (ValueError, AttributeError):
                                # Try as elapsed seconds
                                timestamp = datetime.fromtimestamp(float(row['timestamp']))
                        else:
                            # Use row number as elapsed time from start
                            timestamp = datetime.now() - timedelta(seconds=len(self.reference_data))

                        # Parse values
                        bt = float(row['bt'])
                        et = float(row['et'])
                        ror = float(row.get('ror', 0.0))

                        data_point = RoastData(
                            timestamp=timestamp,
                            bt=bt,
                            et=et,
                            ror=ror
                        )

                        self.reference_data.append(data_point)

                    except (ValueError, KeyError) as e:
                        self.logger.warning(f"Skipping row {row_num}: {e}")
                        continue

            self.logger.info(f"Loaded {len(self.reference_data)} data points from {file_path}")
            return True

        except Exception as e:
            self.logger.error(f"Error loading CSV: {e}")
            return False

    def load_from_dict_list(self, data_list: List[Dict[str, Any]], name: str = 'Custom Profile') -> bool:
        """
        Load reference data from a list of dictionaries

        Args:
            data_list: List of dictionaries with 'bt', 'et', 'ror', 'timestamp' keys
            name: Name for the reference profile

        Returns:
            True if load successful
        """
        try:
            self.reference_data = []
            self.reference_name = name

            for item in data_list:
                bt = float(item['bt'])
                et = float(item.get('et', 0.0))
                ror = float(item.get('ror', 0.0))

                # Parse timestamp if provided, otherwise use datetime.now
                if 'timestamp' in item and item['timestamp']:
                    timestamp = item['timestamp']
                    if isinstance(timestamp, str):
                        timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                else:
                    timestamp = datetime.now()

                data_point = RoastData(
                    timestamp=timestamp,
                    bt=bt,
                    et=et,
                    ror=ror
                )

                self.reference_data.append(data_point)

            self.logger.info(f"Loaded {len(self.reference_data)} data points from dict list")
            return True

        except Exception as e:
            self.logger.error(f"Error loading from dict list: {e}")
            return False

    def get_reference_data(self) -> List[RoastData]:
        """
        Get all reference data points

        Returns:
            List of RoastData objects
        """
        return self.reference_data

    def get_reference_name(self) -> str:
        """
        Get reference profile name

        Returns:
            Reference profile name
        """
        return self.reference_name

    def clear_reference_data(self):
        """Clear all reference data"""
        self.reference_data = []
        self.reference_name = ''
        self.logger.info("Reference data cleared")

    # ============================
    # CSV EXPORT
    # ============================

    def save_csv(self, file_path: str, include_events: bool = True) -> bool:
        """
        Save live data to CSV file

        Args:
            file_path: Path to save CSV file
            include_events: Whether to include events in the CSV

        Returns:
            True if save successful, False otherwise
        """
        try:
            # Ensure directory exists
            self._path_manager.ensure_dir_exists(file_path)

            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                # Write data header
                writer = csv.writer(f)
                writer.writerow(self.csv_columns)

                # Write data rows
                start_time = self.start_time if self.start_time else self.live_data[0].timestamp if self.live_data else datetime.now()

                for data in self.live_data:
                    elapsed_seconds = (data.timestamp - start_time).total_seconds()
                    writer.writerow([
                        f"{elapsed_seconds:.1f}",
                        f"{data.bt:.1f}",
                        f"{data.et:.1f}",
                        f"{data.ror:.1f}"
                    ])

                self.logger.info(f"Saved {len(self.live_data)} data points to {file_path}")

                # Write events if requested
                if include_events and self.live_events:
                    writer.writerow([])  # Empty row separator
                    writer.writerow(['EVENTS'])
                    writer.writerow(['Event Type', 'Event Name', 'Elapsed Time (s)', 'BT', 'ET', 'RoR', 'Description', 'End BT', 'End Time (s)', 'Bean Color'])

                    for event in self.live_events:
                        elapsed_seconds = (event.timestamp - start_time).total_seconds()
                        event_type_str = event.event_type.value if event.event_type else ''
                        end_bt_str = f"{event.end_bt:.1f}" if event.end_bt is not None else ''
                        end_time_str = f"{event.end_time:.1f}" if event.end_time is not None else ''
                        bean_color_str = event.bean_color if event.bean_color else ''

                        writer.writerow([
                            event_type_str,
                            event.name,
                            f"{elapsed_seconds:.1f}",
                            f"{event.bt:.1f}",
                            f"{event.et:.1f}",
                            f"{event.ror:.1f}",
                            event.description,
                            end_bt_str,
                            end_time_str,
                            bean_color_str
                        ])

                    self.logger.info(f"Saved {len(self.live_events)} events to {file_path}")

            return True

        except Exception as e:
            self.logger.error(f"Error saving CSV: {e}")
            return False

    # ============================
    # DATA EXTRACTION HELPERS
    # ============================

    def get_data_for_plotting(self, data_list=None) -> dict:
        """
        Extract data arrays for plotting

        Args:
            data_list: List of RoastData (default: live_data)

        Returns:
            Dictionary with 'time', 'bt', 'et', 'ror' lists
        """
        if data_list is None:
            data_list = self.live_data

        if not data_list:
            return {'time': [], 'bt': [], 'et': [], 'ror': []}

        # Calculate elapsed times from first data point
        start_time = data_list[0].timestamp

        time_data = []
        bt_data = []
        et_data = []
        ror_data = []

        for data in data_list:
            elapsed_seconds = (data.timestamp - start_time).total_seconds()
            time_data.append(elapsed_seconds)
            bt_data.append(data.bt)
            et_data.append(data.et)
            ror_data.append(data.ror)

        return {
            'time': time_data,
            'bt': bt_data,
            'et': et_data,
            'ror': ror_data
        }

    def get_reference_for_plotting(self) -> dict:
        """
        Extract reference data arrays for plotting

        Returns:
            Dictionary with 'time', 'bt', 'et', 'ror' lists
        """
        return self.get_data_for_plotting(self.reference_data)

    def get_live_for_plotting(self) -> dict:
        """
        Extract live data arrays for plotting

        Returns:
            Dictionary with 'time', 'bt', 'et', 'ror' lists
        """
        return self.get_data_for_plotting(self.live_data)
