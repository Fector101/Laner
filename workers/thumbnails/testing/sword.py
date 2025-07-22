import json
import traceback
from typing import Optional,List
import platform
import subprocess
import re
import shutil
from dataclasses import dataclass
import socket
import time

try:
    import netifaces
except:
    print('Running without netifaces...')

from .helper import getUserPCName


@dataclass
class NetworkConfig:
    """Store network configuration settings"""
    server_ip: str = ""
    port: str = "8000"

class NetworkManager:
    """Manage network settings and IP detection"""
    _instance = None
    keep_broadcasting = True
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(NetworkManager, cls).__new__(cls)
        return cls._instance
    
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
        print("Dev using netifaces")
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
        result = subprocess.run(['ipconfig'], capture_output=True, text=True, shell=True,creationflags=subprocess.CREATE_NO_WINDOW)
        pattern = re.compile(r'IPv4.*?:\s*([\d.]+)')
        
        ips = [ip for ip in pattern.findall(result.stdout) 
               if not ip.startswith('127.')]
               
        return self._select_best_ip(ips)

    def _get_ip_from_netifaces(self) -> Optional[str]:
        """Fallback method using netifaces"""
        try:
            for iface in netifaces.interfaces():
                # Prioritize wireless/ethernet
                print('Dev see face',iface)
                if iface.startswith(('wl', 'en')):
                    ip = self._get_interface_ip(iface)
                    if ip:
                        return ip
                        
            # Try other interfaces
            print('Trying Something apart from Wireless')
            return None
            # for iface in netifaces.interfaces():
            #     ip = self._get_interface_ip(iface)
            #     if ip:
            #         return ip
                    
        except Exception:
            print("Dev neatifaces main failed")
            return None

    def _get_interface_ip(self, iface: str) -> Optional[str]:
        """Get IP from specific interface"""
        addrs = netifaces.ifaddresses(iface)
        if netifaces.AF_INET in addrs:
            # print(addrs,'\n',netifaces.AF_INET,'\n','addrs netfaces')
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
    
    def broadcast_ip(self,port,websocket_port):
        server_ip = self._get_system_ip()
        msg=json.dumps({'ip':server_ip,'name':getUserPCName(),'websocket_port':websocket_port})
        # message = f"SERVER_IP:{server_ip}"
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

        print(f"Broadcasting server IP: {server_ip} on port {port}")
        try:
            while True:
                sock.sendto(msg.encode(), ('<broadcast>', port))
                # sock.sendto(message.encode(), ('<broadcast>', port))
                time.sleep(.08)  # Broadcast every second
        except Exception as e:
            print(f"Broadcasting error: {e}")
            traceback.print_exc()
        finally:
            sock.close()
            print('Ended BroadCast !!!')

# Create singleton instance
# # Usage example:
# network = NetworkManager()
# ip = network.getSERVER_IP()
# network.setSERVER_IP('')
# ip = network.getSERVER_IP()
