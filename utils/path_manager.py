"""
Path Manager - Handles cross-platform paths for packaged applications
Ensures data files are written to writable user directories
"""
import os
import sys
from pathlib import Path


class PathManager:
    """
    Manages application paths for data, config, and logs
    Works in both development and packaged (PyInstaller) environments
    """

    APP_NAME = "RachScope"

    def __init__(self):
        """Initialize path manager and create directories"""
        self._app_dir = self._get_app_dir()
        self._data_dir = self._get_data_dir()
        self._config_dir = self._get_config_dir()
        self._log_dir = self._get_log_dir()
        self._assets_dir = self._get_assets_dir()

        # Create directories if they don't exist
        self._create_directories()

    @staticmethod
    def _get_app_dir() -> Path:
        """
        Get the application directory
        Returns the directory where the application is installed/run from

        For PyInstaller onefile:
        - In temp during execution: sys._MEIPASS
        - We use this to read bundled assets

        For development:
        - Project root directory
        """
        if getattr(sys, 'frozen', False):
            # Running as PyInstaller bundle
            return Path(sys._MEIPASS)
        else:
            # Running in development
            return Path(__file__).parent.parent

    def _get_data_dir(self) -> Path:
        """
        Get user data directory for writable files

        Windows: C:\\Users\\<username>\\AppData\\Local\\RachScope
        MacOS: ~/Library/Application Support/RachScope
        Linux: ~/.local/share/RachScope
        """
        if sys.platform == 'win32':
            base = Path(os.environ.get('LOCALAPPDATA', Path.home() / 'AppData' / 'Local'))
        elif sys.platform == 'darwin':
            base = Path.home() / 'Library' / 'Application Support'
        else:  # Linux and others
            base = Path.home() / '.local' / 'share'

        return base / self.APP_NAME

    def _get_config_dir(self) -> Path:
        """
        Get user config directory

        Windows: C:\\Users\\<username>\\AppData\\Roaming\\RachScope
        MacOS: ~/Library/Preferences/RachScope
        Linux: ~/.config/RachScope
        """
        if sys.platform == 'win32':
            base = Path(os.environ.get('APPDATA', Path.home() / 'AppData' / 'Roaming'))
        elif sys.platform == 'darwin':
            base = Path.home() / 'Library' / 'Preferences'
        else:  # Linux and others
            base = Path.home() / '.config'

        return base / self.APP_NAME

    def _get_log_dir(self) -> Path:
        """
        Get log directory

        Windows: C:\\Users\\<username>\\AppData\\Local\\RachScope\\logs
        MacOS: ~/Library/Logs/RachScope
        Linux: ~/.local/share/RachScope/logs
        """
        if sys.platform == 'darwin':
            log_dir = Path.home() / 'Library' / 'Logs' / self.APP_NAME
        else:
            log_dir = self._get_data_dir() / 'logs'

        return log_dir

    def _get_assets_dir(self) -> Path:
        """
        Get assets directory (for reading bundled files)

        For packaged: Returns _MEIPASS/assets
        For development: Returns project_root/assets
        """
        assets_dir = self._app_dir / 'assets'
        return assets_dir

    def _create_directories(self):
        """Create all necessary directories if they don't exist"""
        directories = [
            self._data_dir,
            self._config_dir,
            self._log_dir,
        ]

        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)

    # ============================
    # PUBLIC METHODS
    # ============================

    def get_config_file(self, filename: str = 'settings.json') -> Path:
        """
        Get path to config file

        Args:
            filename: Config filename (default: settings.json)

        Returns:
            Full path to config file
        """
        return self._config_dir / filename

    def get_log_file(self, filename: str) -> Path:
        """
        Get path to log file

        Args:
            filename: Log filename

        Returns:
            Full path to log file
        """
        return self._log_dir / filename

    def get_data_file(self, filename: str) -> Path:
        """
        Get path to data file (CSV exports, etc.)

        Args:
            filename: Data filename

        Returns:
            Full path to data file
        """
        return self._data_dir / filename

    def get_asset_file(self, filename: str) -> Path:
        """
        Get path to asset file (icons, images, etc.)

        Args:
            filename: Asset filename

        Returns:
            Full path to asset file
        """
        return self._assets_dir / filename

    def get_data_dir(self) -> Path:
        """Get the data directory"""
        return self._data_dir

    def get_config_dir(self) -> Path:
        """Get the config directory"""
        return self._config_dir

    def get_log_dir(self) -> Path:
        """Get the log directory"""
        return self._log_dir

    def get_assets_dir(self) -> Path:
        """Get the assets directory"""
        return self._assets_dir

    def ensure_dir_exists(self, path: Path):
        """
        Ensure a directory exists

        Args:
            path: Directory path
        """
        path.mkdir(parents=True, exist_ok=True)

    def is_frozen(self) -> bool:
        """
        Check if running as frozen (packaged) application

        Returns:
            True if packaged, False if in development
        """
        return getattr(sys, 'frozen', False)


# Global instance
_path_manager = None


def get_path_manager() -> PathManager:
    """
    Get the global PathManager instance

    Returns:
        PathManager instance
    """
    global _path_manager
    if _path_manager is None:
        _path_manager = PathManager()
    return _path_manager
