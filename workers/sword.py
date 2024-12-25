from kivy.storage.jsonstore import JsonStore
from typing import Any, Optional

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
        'recent_connections': []
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

    def get(self, category: str, key: str) -> Any:
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
                #[{'name': 'WorkPC', 'ip': '192.168.1.100'}]
        """
        recent = self.get('recent_connections', [])
        if {'name': pc_name, 'ip': ip} not in recent:
            recent.append({'name': pc_name, 'ip': ip})
            self.set('recent_connections', recent)
            

# # Usage example:
# settings = Settings()
# port = settings.get('server', 'port')
# settings.set('server', 'ip', '192.168.1.100')


# SERVER_IP=getSystem_IpAdd()
# def setSERVER_IP(value):
#   global SERVER_IP
#   SERVER_IP=value
# def getSERVER_IP():
#   return SERVER_IP


# def fallbackderviringGetttingIp():
#     try:
#         import netifaces
#         # Get all network interfaces
#         interfaces = netifaces.interfaces()
        
#         # Prioritize wireless and ethernet interfaces
#         for iface in interfaces:
#             if iface.startswith(('wl', 'en')):  # Wireless or Ethernet
#                 addrs = netifaces.ifaddresses(iface)
#                 if netifaces.AF_INET in addrs:  # IPv4 addresses
#                     for addr in addrs[netifaces.AF_INET]:
#                         ip = addr['addr']
#                         # Skip loopback and empty addresses
#                         if ip and not ip.startswith('127.'):
#                             return ip
        
#         # If no wireless/ethernet found, try all other interfaces
#         for iface in interfaces:
#             addrs = netifaces.ifaddresses(iface)
#             if netifaces.AF_INET in addrs:
#                 for addr in addrs[netifaces.AF_INET]:
#                     ip = addr['addr']
#                     if ip and not ip.startswith('127.'):
#                         return ip
        
#         return None
#     except Exception as e:
#         print(f"Error getting IP address: {e}")
#         return None


# def getSystem_IpAdd():
#     def tryOtherFormat(standard_output):
#       ip_pattern = re.compile(r'IPv4 address.*?:\s*([\d.]+)')
#       return ip_pattern.findall(standard_output)
#     os_name = platform.system()
#     if os_name == 'Linux' or os_name == 'Darwin':  # Linux or macOS
#         if shutil.which('ifconfig'):
#             command = ['ifconfig']
#             ip_pattern = re.compile(r'inet\s([\d.]+)')
#         elif shutil.which('ip'):  # Fallback to 'ip addr' if 'ifconfig' is missing
#             command = ['ip', 'addr']
#             ip_pattern = re.compile(r'inet\s([\d.]+)')
#         else:
#             raise FileNotFoundError("Neither 'ifconfig' nor 'ip' command found on the system")
#     elif os_name == 'Windows':
#         command = ['ipconfig']
#         ip_pattern = re.compile(r'IPv4 Address.*?:\s*([\d.]+)')
#     else:
#         raise OSError("Unsupported operating system")

#     # Run the command and capture output
#     result = subprocess.run(command, capture_output=True, text=True)
#     # print('peek',result.stdout)
#     # Extract IP addresses
#     ip_addresses = ip_pattern.findall(result.stdout)
#     ip_addresses = tryOtherFormat(result.stdout) if os_name == 'Windows' and len(ip_addresses) == 0 else ip_addresses
#     # Exclude loopback addresses like 127.0.0.1
#     ip_addresses = [ip for ip in ip_addresses if not ip.startswith('127.')]
    
#     if len(ip_addresses) == 0 or len(ip_addresses) == 1 and ip_addresses[0] == '127.0.0.1':
        
#         return fallbackderviringGetttingIp()
      
#     if len(ip_addresses) > 1 and ip_addresses[1].startswith('192.168.'):
#         return ip_addresses[1]
#     return ip_addresses[0] if len(ip_addresses) else None
