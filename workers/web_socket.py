import websockets,asyncio,traceback
from websockets.asyncio.connection import Connection # for type
import json,secrets
# Socket for connection (handling only authns for now)
class WebSocketConnectionHandler:
    def __init__(self, websocket:Connection, connection_signal=None):
        self.websocket= websocket
        self.connection_signal = connection_signal
        self.authenticated = False
        self.response_event = asyncio.Event()
        # TODO Please secert file to store connected users
        self.connected_clients = {}
    async def handle_connection_request(self,message):
        """Handle WebSocket connection requests"""
        print('didn"t call me')
        # TODO don't remove line use ip later in setting for some other stuff
        try:
            device_ip = f"Device-{self.websocket.remote_address[0]}"
            # message = await self.websocket.recv()
            message_dict = json.loads(message)
            print(message_dict,type(message_dict),message_dict['request'])
            if self.connection_signal and message_dict['request'] == 'password':
            #     print('self ---- ',self)
                print('erro')
                self.connection_signal.connection_request.emit(message_dict, self)  # Pass the handler instance
                print('erro1')
                await self.response_event.wait() # this keeps connection open
            elif message_dict['request'] == 'auth':
                print('doing authn')
                token = message_dict['token'] if 'token' else ''
                if self.connected_clients.get(self.websocket.remote_address[0]) == token:
                    await self.websocket.send("authenticated_successfully")
                else:
                    await self.websocket.send("authentication_failed")
                # return self.authenticated
        except json.JSONDecodeError:
            print(f"Received non-JSON message: {message}")
        except Exception as e:
            traceback.print_exc()
            print('unexcepted error from WebSocketConnectionHandler.handle_connection_request ',e)
        
        # if self.connection_signal:
        #     print('self ---- ',self)
        #     self.connection_signal.connection_request.emit(message_dict, self)  # Pass the handler instance
        #     await self.response_event.wait()
        #     print('test0----------------------')
        #     return self.authenticated
        #     print('test1----------------------')
        return False
    # Seprate accept and reject methods because will add other stuff to each, TO KEEP CLEAN
    async def accept(self):
        password = secrets.token_hex(16)
        self.connected_clients[self.websocket.remote_address[0]] = password
        await self.websocket.send(f"accepted:{password}")
        self.response_event.set()
        # await self.websocket.send("ACCESS_GRANTED")
    async def reject(self):
        await self.websocket.send("ACCESS_DENIED")
        self.response_event.set()
        
    async def handle_connection(self):
        """Main connection handling loop"""
        try:
            # Wait for authentication
            msg = await self.websocket.recv()
            print('test0 ',msg)
            authenticated = await self.handle_connection_request(message=msg)
            print('test1')
            
            # if not authenticated:
            #     await self.websocket.close()
            #     return
            # # Keep connection alive
            # while True:
            #     message = await self.websocket.recv()
            #     print(f"Received: {message}")
            #     print('not reachs here')
                # Handle messages here
                
        except websockets.exceptions.ConnectionClosed:
            print("Client disconnected")
        except Exception as e:
            print(f"WebSocket error: {e}")
            traceback.print_exc()
            await self.websocket.close()

      
    # async def send_response(self, accepted):
    #     """Send acceptance/rejection to client"""
    #     self.authenticated = accepted
    #     if accepted:
    #         await self.websocket.send("ACCESS_GRANTED")
    #     else:
    #         await self.websocket.send("ACCESS_DENIED")
        # self.response_event.set()

    # async def on_connect(self):
    #     """Handle new WebSocket connections"""
    #     try:
    #         authenticated = await self.handle_connection_request()
    #         if not authenticated:
    #             await self.websocket.close()
    #             return

    #         # Connection is authenticated, handle messages
    #         async for message in self.websocket:
    #             print(f"Received: {message}")
    #             # Handle your WebSocket messages here

    #     except websockets.exceptions.ConnectionClosed:
    #         print("Client disconnected")
    #     except Exception as e:
    #         print(f"WebSocket error: {e}")
    #         await self.websocket.close()
