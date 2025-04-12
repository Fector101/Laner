import json,asyncio,websockets,threading
import traceback
from getpass import getuser
from typing import Any, Optional

from typing import Optional, List,Union
import platform
import subprocess
import re
import shutil
import netifaces
import socket

from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor
from threading import Thread
from kivy.clock import Clock

from utils.helper import get_device_name, getUserPCName


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
        self._ip_for_websocket= None # Not clear old IP incase PC user rejects connection,
        self._port_for_websocket= None # Not clear old IP incase PC user rejects connection,
        self._password_response_callback=None # Not clear old IP incase PC user rejects connection,
        # then if user was already connected to a PC they keep using the old ip
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
    def find_server(self,port,timeout,on_find=None):
        # TODO continue broadcast till you find right PORT
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(('', port))  # Listen on all available interfaces
        sock.settimeout(timeout)
        # print(f"Listening for server IP on port {port}...")
        data=''
        try:
            data, addr = sock.recvfrom(1024)
            if data:
                msg = json.loads(data.decode())
                server_ip = msg['ip']
                print("Detected Server IP:", server_ip,'at port: ',port, 'pc name: ',msg['name'])
                if on_find:
                    Clock.schedule_once(lambda dt: on_find(msg))
                return server_ip  # Use this IP to connect to the server
        except socket.timeout:
            pass
            # print("Timeout: No broadcast received")

        except json.JSONDecodeError:
            print(f"Invalid JSON received when finding ip: {data}")
        except:
            traceback.print_exc()
        finally:
            sock.close()

    def scan_ports(self, ports,on_find, timeout=5, on_complete=None):
        def run_scan():
            results = []
            with ThreadPoolExecutor(max_workers=len(ports)) as executor:
                futures = [executor.submit(self.find_server, port, timeout,on_find) for port in ports]
                for future in futures:
                    result = future.result()
                    if result:
                        results.append(result)

            if on_complete:
                Clock.schedule_once(lambda dt: on_complete(results))

        Thread(target=run_scan, daemon=True).start()

    def start_password_request(self,ip,websocket_port,password_response_callback):
        self._ip_for_websocket = ip
        self._port_for_websocket = websocket_port
        self._password_response_callback=password_response_callback
        threading.Thread(target=self._run_async).start()

    def _run_async(self):
        asyncio.run(self._connect_websocket())

    async def _connect_websocket(self):
        try:
            # uri = f"ws://{listen_for_pc()}:8765"  # Replace <PC-IP>
            uri = f"ws://{self._ip_for_websocket}:{self._port_for_websocket}"
            try:
                print(get_device_name())
            except:
                traceback.print_exc()
            print('Cool Method+++++++++++++++++++++++++++++ ',getuser())
            message = {
                    'name': getUserPCName(),
                    'request': 'password'
                }
            # print('dumpsss',json.dumps(message))
            print(uri)
            async with websockets.connect(uri) as ws:
                await ws.send(json.dumps(message))
                response = await ws.recv()
                if response.startswith("accepted:"):
                    password = response.split("accepted:")[1]
                    # print(f"Connected! Password: {password}")
                    await ws.send(json.dumps({'request':'auth','token':password}))
                    auth_response = await ws.recv()
                    if self._password_response_callback:
                        Clock.schedule_once(lambda dt: self._password_response_callback(auth_response))
                    # print(f"Auth: {auth_response}")
                else:
                    if self._password_response_callback:
                        Clock.schedule_once(lambda dt: self._password_response_callback(response))
                    # print("Connection rejected.")
        except Exception as e:
            traceback.print_exc()


# settings = Settings()
# network = NetworkManager()
# settings.set('server', 'ip', network.get_server_ip())
# Create singleton instance
# # Usage example:
# network = NetworkManager()
# ip = network.getSERVER_IP()
# network.setSERVER_IP('')
# ip = network.getSERVER_IP()
