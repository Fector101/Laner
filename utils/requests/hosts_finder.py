import json,traceback
import socket,threading,asyncio,websockets
from threading import Thread
from concurrent.futures import ThreadPoolExecutor
from android_notify.config import from_service_file
from utils.helper import get_device_name

if not from_service_file():
    from kivy.clock import Clock
else:
    class Clock:
        def schedule_once(self):
            print('A fall back function async_requests',self)


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
        error_dict={'error':True}
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
                response = json.loads(response)
                if response.get('status') == 'yes':
                    token = response['token']
                    await ws.send(json.dumps({'request':'auth','token':token}))
                    auth_response = await ws.recv()
                    if self._password_response_callback:
                        Clock.schedule_once(lambda dt: self._password_response_callback(json.loads(auth_response)))
                    else:
                        print('invalid format pass in callback to `start_password_request` method')
                elif response['status'] == 'no':
                    if self._password_response_callback:
                        response['auth'] = False #self._password_response_callback expecting 'auth' state
                        Clock.schedule_once(lambda dt: self._password_response_callback(response))
                    else:
                        print('invalid format pass in callback to `start_password_request` method')
                else:
                    print("Bad (Broke Token Auth)Haven't Planned For This Response: ",response)
        except websockets.exceptions.ConnectionClosedError as e:
            error_dict['error']=e
            print('websockets.exceptions.ConnectionClosedError-101: ',e)
            Clock.schedule_once(lambda dt: self._password_response_callback(error_dict))
        except json.JSONDecodeError as e:
            error_dict['error']=e
            print('Server Sent Bad Format: ',e)
            traceback.print_exc()
        except ConnectionRefusedError as e:
            print('ConnectionRefusedError-101: ',e)
            error_dict['error']=e
            Clock.schedule_once(lambda dt: self._password_response_callback(error_dict))
        except Exception as e:
            error_dict['error']=e
            print('add error to exceptions ',e)
            Clock.schedule_once(lambda dt: self._password_response_callback(error_dict))
            traceback.print_exc()
