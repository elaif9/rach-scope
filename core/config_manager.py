"""
Configuration Manager for Rach Scope
Handles loading and saving settings to/from settings.json
"""
import json
from typing import Dict, Any
from utils.path_manager import get_path_manager


class ConfigManager:
    """Manages application configuration settings"""

    DEFAULT_CONFIG = {
        'ip': '192.168.1.100',
        'port': 502,
        'slave_id_bt': 1,
        'slave_id_et': 1,
        'reg_bt': 0,
        'reg_et': 0,
        'scale': 10.0
    }

    def __init__(self, config_file: str = 'settings.json'):
        """
        Initialize ConfigManager

        Args:
            config_file: Path to the configuration file (default: settings.json)
        """
        self.config_file = config_file
        self.config: Dict[str, Any] = {}
        self._path_manager = get_path_manager()
        self.load_config()

    def get_config_path(self) -> str:
        """
        Get the absolute path to the config file

        Returns:
            Absolute path to settings.json in user config directory
        """
        return str(self._path_manager.get_config_file(self.config_file))

    def load_config(self) -> Dict[str, Any]:
        """
        Load configuration from settings.json

        Returns:
            Dictionary containing configuration settings
        """
        config_path = self._path_manager.get_config_file(self.config_file)

        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    loaded_config = json.load(f)
                    # Merge loaded config with defaults (in case of missing keys)
                    self.config = {**self.DEFAULT_CONFIG, **loaded_config}
            except (json.JSONDecodeError, IOError) as e:
                print(f"Error loading config file: {e}")
                print("Using default configuration")
                self.config = self.DEFAULT_CONFIG.copy()
        else:
            # Config file doesn't exist, use defaults and create it
            self.config = self.DEFAULT_CONFIG.copy()
            self.save_config()

        return self.config

    def save_config(self) -> bool:
        """
        Save current configuration to settings.json

        Returns:
            True if save was successful, False otherwise
        """
        config_path = self._path_manager.get_config_file(self.config_file)

        try:
            # Ensure directory exists
            self._path_manager.ensure_dir_exists(config_path.parent)

            with open(config_path, 'w') as f:
                json.dump(self.config, f, indent=4)
            return True
        except IOError as e:
            print(f"Error saving config file: {e}")
            return False

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value by key

        Args:
            key: Configuration key
            default: Default value if key doesn't exist

        Returns:
            Configuration value or default
        """
        return self.config.get(key, default)

    def set(self, key: str, value: Any) -> bool:
        """
        Set a configuration value and save to file

        Args:
            key: Configuration key
            value: Value to set

        Returns:
            True if save was successful, False otherwise
        """
        self.config[key] = value
        return self.save_config()

    def update(self, settings: Dict[str, Any]) -> bool:
        """
        Update multiple configuration values at once

        Args:
            settings: Dictionary of settings to update

        Returns:
            True if save was successful, False otherwise
        """
        self.config.update(settings)
        return self.save_config()

    def reset_to_defaults(self) -> bool:
        """
        Reset configuration to default values

        Returns:
            True if save was successful, False otherwise
        """
        self.config = self.DEFAULT_CONFIG.copy()
        return self.save_config()
