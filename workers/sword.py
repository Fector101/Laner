from kivy.storage.jsonstore import JsonStore
from typing import Any, Optional

from typing import Optional, List,Union
import platform
import subprocess
import re
import shutil
import netifaces
from dataclasses import dataclass

class Settings:
    """A singleton class to manage application settings stored in a JSON file.

    This class provides methods to get and set settings values stored in a JSON file,
    as well as manage recent connections.

    Attributes:
        _instance (Settings): The singleton instance.
        _store (JsonStore): The JSON store for settings.
        _defaults (dict): Default settings values.

    Example:
        >>> settings = Settings()
        >>> settings.get('server', 'ip')
        '192.168.1.1'
        >>> settings.set('server', 'ip', '192.168.1.2')
        >>> settings.add_recent_connection('MyPC', '192.168.1.2')
    """
    _instance = None
    _store = JsonStore('settings.json')
    
    _defaults = {
        'server': {
            'ip': '',
            'port': '8000',
            'passcode': '08112321825'
        },
        'display': {
            'show_hidden_files': False,
            'theme': 'Dark'
        },
        'recent_connections': {}
    }

    def __new__(cls):
        # """Create and return singleton instance of Settings.
    
        # This method ensures only one Settings instance exists:
        # 1. First call: Creates new instance
        # 2. Subsequent calls: Returns existing instance
        
        # Returns:
        #     Settings: The singleton Settings instance
        
        # Example:
        #     >>> s1 = Settings()
        #     >>> s2 = Settings()
        #     >>> s1 is s2
        #     True
        # """
        if cls._instance is None:
            # First time: Create new instance
            cls._instance = super(Settings, cls).__new__(cls)
            # Initialize settings
            cls._instance._initialize()
        # Return existing or new instance
        return cls._instance

    def _initialize(self) -> None:
        """Initialize settings with defaults if not exists"""
        for category, values in self._defaults.items():
            # print(category, values)
            if not self._store.exists(category):
                if isinstance(values, dict):
                    self._store.put(category, **values)  # Unpack dict as kwargs
                else:
                    self._store.put(category, value=values)  # Single value as kwarg

    def get(self, category: str, key: Union[str, None]=None) -> Any:
        """Retrieve a setting value from specified category and key.

        Args:
            category (str): The settings category (e.g., 'server', 'display')
            key (str): The setting key to retrieve

        Returns:
            Any: The value of the setting

        Example:
            >>> settings.get('server', 'ip')
            '192.168.1.1'
        """
        if category in self._store:
            stored_data = self._store.get(category)
            if key in stored_data:
                return stored_data[key]
            else:
                return stored_data#['value']
        # last resort return default values
        return self._defaults[category][key]

    def set(self, category: str, key: str, value: Any) -> None:
        """Set a setting value for specified category and key.

        Args:
            category (str): The settings category
            key (str): The setting key to modify
            value (Any): The new value to set

        Example:
            >>> settings.set('server', 'ip', '192.168.1.1')
        """
        if category in self._store:
            current = self._store.get(category)
            current[key] = value
            self._store.put(category, **current)
        else:
            self._store.put(category, **{key: value})

    def add_recent_connection(self, pc_name: str, ip: str) -> None:
        """Add a new connection to the recent connections list.

        Args:
            pc_name (str): Name of the computer to connect to
            ip (str): IP address of the computer

        Example:
            >>> settings = Settings()
            >>> settings.add_recent_connection('WorkPC', '192.168.1.100')
            >>> settings.get('recent_connections', [])
                #{'fabian-X550LA': '192.168.148.4', 'Test': '111', 'Last': 'zzzz'}
        """
        recents = self.get('recent_connections')
        self.set('recent_connections', key=pc_name, value= ip)
            
# # Usage example:
# settings = Settings()
# port = settings.get('server', 'port')
# settings.set('server', 'ip', '192.168.1.100')
# settings.add_recent_connection('WorkPC', '192.168.1.100')

@dataclass
class NetworkConfig:
    """Store network configuration settings"""
    server_ip: str = ""
    port: str = "8000"

class NetworkManager:
    """Manage network settings and IP detection"""
    
    def __init__(self):
        self.config = NetworkConfig()
        self.config.server_ip = self._get_system_ip()

    def set_server_ip(self, ip: str) -> None:
        """Set server IP address"""
        self.config.server_ip = ip

    def get_server_ip(self) -> str:
        """Get current server IP address"""
        return self.config.server_ip

    def set_port(self, port: str) -> None:
        """Set server port"""
        self.config.port = port

    def get_port(self) -> str:
        """Get current server port"""
        return self.config.port

    def _get_system_ip(self) -> Optional[str]:
        """Get system IP address using available methods"""
        os_name = platform.system()
        
        # Try primary method
        ip = self._get_ip_from_commands(os_name)
        if ip:
            return ip
            
        # Fallback to netifaces
        return self._get_ip_from_netifaces()

    def _get_ip_from_commands(self, os_name: str) -> Optional[str]:
        """Get IP using system commands"""
        try:
            if os_name in ('Linux', 'Darwin'):
                return self._get_unix_ip()
            elif os_name == 'Windows':
                return self._get_windows_ip()
            raise OSError("Unsupported operating system")
        except Exception:
            return None

    def _get_unix_ip(self) -> Optional[str]:
        """Get IP on Unix-like systems"""
        command = ['ifconfig'] if shutil.which('ifconfig') else ['ip', 'addr']
        pattern = re.compile(r'inet\s([\d.]+)')
        
        result = subprocess.run(command, capture_output=True, text=True)
        ips = [ip for ip in pattern.findall(result.stdout) 
               if not ip.startswith('127.')]
               
        return self._select_best_ip(ips)

    def _get_windows_ip(self) -> Optional[str]:
        """Get IP on Windows systems"""
        result = subprocess.run(['ipconfig'], capture_output=True, text=True)
        pattern = re.compile(r'IPv4.*?:\s*([\d.]+)')
        
        ips = [ip for ip in pattern.findall(result.stdout) 
               if not ip.startswith('127.')]
               
        return self._select_best_ip(ips)

    def _get_ip_from_netifaces(self) -> Optional[str]:
        """Fallback method using netifaces"""
        try:
            for iface in netifaces.interfaces():
                # Prioritize wireless/ethernet
                if iface.startswith(('wl', 'en')):
                    ip = self._get_interface_ip(iface)
                    if ip:
                        return ip
                        
            # Try other interfaces
            for iface in netifaces.interfaces():
                ip = self._get_interface_ip(iface)
                if ip:
                    return ip
                    
        except Exception:
            return None

    def _get_interface_ip(self, iface: str) -> Optional[str]:
        """Get IP from specific interface"""
        addrs = netifaces.ifaddresses(iface)
        if netifaces.AF_INET in addrs:
            for addr in addrs[netifaces.AF_INET]:
                ip = addr['addr']
                if ip and not ip.startswith('127.'):
                    return ip
        return None

    def _select_best_ip(self, ips: List[str]) -> Optional[str]:
        """Select best IP from list"""
        if not ips:
            return None
        # Prefer 192.168.x.x addresses
        for ip in ips:
            if ip.startswith('192.168.'):
                return ip
        return ips[0]

    def setSERVER_IP(self, value: str) -> None:
        """Set server IP address (public method)"""
        self.set_server_ip(value)

    def getSERVER_IP(self) -> str:
        """Get current server IP address (public method)"""
        return self.get_server_ip()


settings = Settings()
network = NetworkManager()
settings.set('server', 'ip', network.get_server_ip())
# Create singleton instance
# # Usage example:
# network = NetworkManager()
# ip = network.getSERVER_IP()
# network.setSERVER_IP('')
# ip = network.getSERVER_IP()
