import json
from typing import Any, Optional,List,Union
import platform
import subprocess
import re
import shutil
import netifaces
from dataclasses import dataclass
import socket
import time
import threading
import os
from PIL import Image 
import PIL
from workers.helper import gen_unique_filname, _joinPath, getAppFolder, getUserPCName


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

        while True:
            sock.sendto(msg.encode(), ('<broadcast>', port))
            # sock.sendto(message.encode(), ('<broadcast>', port))
            time.sleep(.08)  # Broadcast every second
        print('Ended BroadCast !!!')

class JPEGWorker:
        
    # TODO Make an init file or config file for app for things like this
    preview_folder = os.path.join(getAppFolder(), 'preview-imgs')
    def __init__(self,img_path:str,server_ip:str):
        self.server_ip = server_ip
        self.img_path = img_path

        os.makedirs(self.preview_folder,exist_ok=True)
        
        threading.Thread(
                        target=self.genrateJPEG,
                        daemon=True
                    ).start()
        
    def getJPEG_URL(self):
        """Returns JPG path while waiting for server"""
        new_file_name = gen_unique_filname(self.img_path) + '.jpg'
        new_img_path = _joinPath(self.preview_folder,new_file_name)
        return f"http://{self.server_ip}:8000/{new_img_path}"
        
    
    def genrateJPEG(self):
        print('goten img path ',self.img_path)
        new_file_name = gen_unique_filname(self.img_path) + '.jpg'
        new_img_path = _joinPath(self.preview_folder,new_file_name)
        new_img_url=self.getJPEG_URL() #For debugging
        try:
            im = Image.open(self.img_path)
            rgb_im = im.convert("RGB")
            
            rgb_im.save(new_img_path, quality=90)
            # print('new_file_name ',new_file_name)
            print('new_img_url ',new_img_url) #For debugging
            
        except PIL.UnidentifiedImageError:
            im = Image.open(_joinPath(getAppFolder(),'assets','imgs','image.png'))
            rgb_im = im.convert("RGB")
            rgb_im.save(new_img_path, quality=60)
            
            print(f'Failed getting JPEG {self.img_path} -----------------------------------------')
            return "assets/icons/image.png"
        
        #TODO Probalbly catch all errors
# Create singleton instance
# # Usage example:
# network = NetworkManager()
# ip = network.getSERVER_IP()
# network.setSERVER_IP('')
# ip = network.getSERVER_IP()
