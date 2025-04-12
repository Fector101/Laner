import json,traceback
import socket,threading,asyncio
import websockets

from threading import Thread
from concurrent.futures import ThreadPoolExecutor

from kivy.clock import Clock
from utils.helper import get_device_name


class FindHosts:
    def __init__(self):
        self._ip_for_websocket = None  # Not clear old IP incase PC user rejects connection,
        self._port_for_websocket = None  # Not clear old IP incase PC user rejects connection,
        self._password_response_callback = None  # Not clear old IP incase PC user rejects connection,
        # then if user was already connected to a PC they keep using the old ip

    def find_server(self,port,timeout,on_find=None):
        """
            Checks if PC's is Broadcasting from a Port
            :param port: to scan
            :param timeout: Finding Timeout for response
            :param on_find: callback for when a port is found
            :return:
        """
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
                return server_ip
        except socket.timeout:
            pass

        except json.JSONDecodeError:
            print(f"Invalid JSON received when finding ip: {data}")
        except:
            traceback.print_exc()
        finally:
            sock.close()

    def scan_ports(self, ports,on_find, timeout=5, on_complete=None):
        """
            Scan a number of port
        """
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
            uri = f"ws://{self._ip_for_websocket}:{self._port_for_websocket}"
            message = {
                    'name': get_device_name(),
                    'request': 'password'
                }
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
            print('add error to exceptions ',e)
            traceback.print_exc()
