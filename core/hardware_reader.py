"""
Hardware Reader - Modbus TCP Reader for HF2211
Integrates HF2211 hardware via Modbus TCP protocol
"""
import logging
from datetime import datetime
from typing import Optional, Tuple
from pymodbus.client import ModbusTcpClient
from pymodbus.exceptions import ModbusException
from utils.path_manager import get_path_manager


class ModbusReader:
    """
    Modbus TCP Reader for HF2211 temperature sensors
    Supports reading Bean Temperature (BT) and Environmental Temperature (ET)
    from different slave IDs
    """

    def __init__(
        self,
        ip: str = '192.168.1.100',
        port: int = 502,
        slave_id_bt: int = 1,
        slave_id_et: int = 1,
        reg_bt: int = 0,
        reg_et: int = 0,
        scale: float = 10.0,
        max_errors: int = 10
    ):
        """
        Initialize Modbus Reader

        Args:
            ip: IP address of the HF2211 device
            port: Modbus TCP port (default: 502)
            slave_id_bt: Slave ID for Bean Temperature (default: 1)
            slave_id_et: Slave ID for Environmental Temperature (default: 1)
            reg_bt: Register address for BT
            reg_et: Register address for ET
            scale: Scale factor for temperature conversion
            max_errors: Maximum consecutive errors before reconnect attempt
        """
        self.ip = ip
        self.port = port
        self.slave_id_bt = slave_id_bt
        self.slave_id_et = slave_id_et
        self.reg_bt = reg_bt
        self.reg_et = reg_et
        self.scale = scale
        self.max_errors = max_errors

        # Client connection
        self.client: Optional[ModbusTcpClient] = None

        # Last connection error (for UI feedback)
        self.last_connection_error: Optional[str] = None

        # Statistics
        self.read_count = 0
        self.error_count = 0
        self.start_time = datetime.now()

        # Path manager for writable directories
        self._path_manager = get_path_manager()

        # Setup logging
        self.logger = self._setup_logging()

    def _setup_logging(self) -> logging.Logger:
        """
        Setup logging to file

        Returns:
            Configured logger instance
        """
        # Get log file path from path manager
        log_path = self._path_manager.get_log_file('hardware.log')

        # Ensure log directory exists
        self._path_manager.ensure_dir_exists(log_path.parent)

        logger = logging.getLogger('ModbusReader')
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

    def connect(self) -> bool:
        """
        Establish connection to Modbus TCP device and validate by reading data

        Returns:
            True if connection successful and data can be read, False otherwise
        """
        self.last_connection_error = None

        try:
            self.client = ModbusTcpClient(
                host=self.ip,
                port=self.port,
                timeout=3
            )

            if not self.client.connect():
                self.logger.error(f"Failed to connect to {self.ip}:{self.port}")
                self.last_connection_error = f"Could not establish TCP connection to {self.ip}:{self.port}"
                return False

            self.logger.info(f"TCP connected to HF2211 at {self.ip}:{self.port}")

            # Validate by actually trying to read data from BT register
            try:
                response = self.client.read_holding_registers(
                    address=self.reg_bt,
                    count=1,
                    slave_id=self.slave_id_bt
                )

                if response.isError():
                    error_msg = str(response)
                    self.logger.error(f"Modbus read validation failed: {error_msg}")
                    self.last_connection_error = f"Modbus read failed: {error_msg}"
                    # Disconnect since validation failed
                    self.client.close()
                    return False

                # Successfully read data
                self.logger.info(f"BT Slave ID: {self.slave_id_bt}, ET Slave ID: {self.slave_id_et}")
                self.logger.info(f"BT Register: {self.reg_bt}, ET Register: {self.reg_et}")
                self.logger.info(f"Scale Factor: {self.scale}")
                self.logger.info("Connection validated - data can be read")
                return True

            except ModbusException as e:
                self.logger.error(f"Modbus exception during validation: {e}")
                self.last_connection_error = f"Modbus error: {e}"
                self.client.close()
                return False
            except Exception as e:
                self.logger.error(f"Unexpected error during validation: {e}")
                self.last_connection_error = f"Validation error: {e}"
                self.client.close()
                return False

        except Exception as e:
            self.logger.error(f"Connection error: {e}")
            self.last_connection_error = f"Connection failed: {e}"
            return False

    def disconnect(self):
        """Close Modbus TCP connection"""
        if self.client:
            self.client.close()
            self.client = None
            self.logger.info("Disconnected from HF2211")

    def _read_temperature(
        self,
        slave_id: int,
        register: int,
        sensor_name: str
    ) -> Optional[float]:
        """
        Read temperature from a specific register

        Args:
            slave_id: Modbus slave ID
            register: Register address
            sensor_name: Name of the sensor (for logging)

        Returns:
            Temperature in Celsius or None if read failed
        """
        try:
            if not self.client or not self.client.connected:
                self.logger.warning(f"Client not connected for {sensor_name}")
                return None

            # Read holding register (use slave_id parameter for pymodbus 3.x)
            response = self.client.read_holding_registers(
                address=register,
                count=1,
                slave_id=slave_id
            )

            if response.isError():
                self.logger.error(f"Modbus error reading {sensor_name}: {response}")
                return None

            # Extract value and apply scale
            raw_value = response.registers[0]
            temperature = raw_value / self.scale

            self.logger.debug(f"{sensor_name}: {raw_value} / {self.scale} = {temperature:.1f}°C")
            return temperature

        except ModbusException as e:
            self.logger.error(f"Modbus exception reading {sensor_name}: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Unexpected error reading {sensor_name}: {e}")
            return None

    def read_once(self) -> Tuple[Optional[float], Optional[float]]:
        """
        Read BT and ET temperatures once

        This method is designed to be called periodically by a timer.

        Returns:
            Tuple of (bt, et) temperatures in Celsius
            Returns (None, None) if read failed
        """
        # Reconnect if client is not connected
        if not self.client or not self.client.connected:
            self.logger.warning("Client not connected, attempting reconnect...")
            if not self.connect():
                self.error_count += 1
                return None, None

        # Read BT
        bt = self._read_temperature(self.slave_id_bt, self.reg_bt, "BT")

        # Read ET
        if self.reg_et == self.reg_bt and self.slave_id_et == self.slave_id_bt:
            # Same register and slave ID, use same value
            et = bt
        else:
            et = self._read_temperature(self.slave_id_et, self.reg_et, "ET")

        # Update statistics
        if bt is not None and et is not None:
            self.read_count += 1
            self.error_count = 0

            # Log success every 10 reads
            if self.read_count % 10 == 0:
                self.logger.debug(f"Read #{self.read_count}: ET={et:.1f}°C, BT={bt:.1f}°C")
        else:
            self.error_count += 1
            self.logger.warning(f"Failed read (error #{self.error_count})")

            # Try reconnect on too many errors
            if self.error_count >= self.max_errors:
                self.logger.error("Too many errors, attempting reconnect...")
                self.disconnect()
                self.connect()
                self.error_count = 0

        return bt, et

    def update_config(
        self,
        ip: Optional[str] = None,
        port: Optional[int] = None,
        slave_id_bt: Optional[int] = None,
        slave_id_et: Optional[int] = None,
        reg_bt: Optional[int] = None,
        reg_et: Optional[int] = None,
        scale: Optional[float] = None
    ):
        """
        Update configuration parameters

        Args:
            ip: New IP address
            port: New port
            slave_id_bt: New BT slave ID
            slave_id_et: New ET slave ID
            reg_bt: New BT register
            reg_et: New ET register
            scale: New scale factor
        """
        reconnect_needed = False

        if ip is not None and ip != self.ip:
            self.ip = ip
            reconnect_needed = True

        if port is not None and port != self.port:
            self.port = port
            reconnect_needed = True

        if slave_id_bt is not None:
            self.slave_id_bt = slave_id_bt

        if slave_id_et is not None:
            self.slave_id_et = slave_id_et

        if reg_bt is not None:
            self.reg_bt = reg_bt

        if reg_et is not None:
            self.reg_et = reg_et

        if scale is not None:
            self.scale = scale

        if reconnect_needed and self.client:
            self.logger.info("Configuration changed, reconnecting...")
            self.disconnect()
            self.connect()

    def get_statistics(self) -> dict:
        """
        Get reading statistics

        Returns:
            Dictionary with statistics
        """
        elapsed = (datetime.now() - self.start_time).total_seconds()
        rate = self.read_count / elapsed if elapsed > 0 else 0

        return {
            'runtime_seconds': elapsed,
            'total_reads': self.read_count,
            'error_count': self.error_count,
            'read_rate_per_second': rate
        }

    def log_statistics(self):
        """Log current statistics to file"""
        stats = self.get_statistics()
        self.logger.info("=" * 50)
        self.logger.info("STATISTICS:")
        self.logger.info(f"  Runtime      : {stats['runtime_seconds']:.1f} seconds")
        self.logger.info(f"  Total reads  : {stats['total_reads']}")
        self.logger.info(f"  Error count  : {stats['error_count']}")
        self.logger.info(f"  Read rate    : {stats['read_rate_per_second']:.1f} reads/sec")
        self.logger.info("=" * 50)

    def is_connected(self) -> bool:
        """
        Check if client is connected

        Returns:
            True if connected, False otherwise
        """
        return self.client is not None and self.client.connected
