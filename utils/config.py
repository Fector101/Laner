from kivy.storage.jsonstore import JsonStore
from typing import Any, Optional

from typing import Optional, List,Union
import platform
import subprocess
import re
import shutil
import netifaces
import socket

from dataclasses import dataclass
# Doesn't work adding sets in json
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
        'recent_connections': {
            'ips':[]
        },
        'pcs':{}
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
            settings = Settings()
            settings.set('server', 'ip', '192.168.1.1')\n
            .
        """
        if category in self._store:
            current = self._store.get(category)
            current[key] = value
            self._store.put(category, **current)
        else:
            self._store.put(category, **{key: value})
    def set_pc(self,pc_name,value:dict):
        """
        Sets Values for a specific PC,auto adds port to ports Set
        :param pc_name: The PC's name, is acts as a key in pcs object
        :param value: { ip:'', token:'', port: '3033'} Important `port` not `ports`
        :return: void :)
        """
        if 'pcs' in self._store:
            current = self._store.get('pcs')
            old_pc_values = current.get(pc_name,{})
            if 'port' in value:
                ports= old_pc_values.get('ports',[])
                ports = list({value.get('port'), *ports})# list of last ports connected in certain PC's
                value['ports'] = ports
            current[pc_name] = {**old_pc_values,**value}
            self._store.put('pcs', **current)
        else:
            self._store.put('pcs',**{pc_name: value})
    def get_recent_connections(self) -> List:
        """Returns List of old connections ips

        Returns:
            List: ips list
        """
        if "recent_connections" in self._store:
            recent_connections = self._store.get("recent_connections")
            if 'ips' in recent_connections:
                return recent_connections['ips']
        
    def add_recent_connection(self, ip: str) -> None:
        """Add a new connection to the recent connections list.

        Args:
            ip (str): IP address of the computer

        Example:
            >>> settings = Settings()
            >>> settings.add_recent_connection('192.168.1.100')
            >>> settings.get_recent_connections()
                #['192.168.148.4', '11111','1111','213']
        """
        # recents = self.get('recent_connections')
        # new_name = f"{pc_name}{len(recents)}"
        # for each in recents:
        #     print(each,' each')
        # print('recent_connection ', new_name,ip)
        
        if "recent_connections" in self._store:
            current = self._store.get("recent_connections")
            current['ips'] = list({*current['ips'], ip}) # filter with set then change to list
            self._store.put("recent_connections", **current)

# # Usage example:
# settings = Settings()
# port = settings.get('server', 'port')
# settings.set('server', 'ip', '192.168.1.100')
# settings.add_recent_connection('WorkPC', '192.168.1.100')