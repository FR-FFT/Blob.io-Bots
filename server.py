import asyncio
import ctypes
import math
import random
import websockets
import struct
import json
import time
import binascii
import httpx
import python_socks  
import node_update_parser as parser



# --- CONFIGURATION (Remains Mostly the Same) ---
TARGET_SERVER_IP_PORT = "51.195.60.134:6001"
SERVER_URI = f"ws://{TARGET_SERVER_IP_PORT}/"
ORIGIN = "http://custom.client.blobgame.io"
skin_names = ['fly', 'fish', 'amber', 'spider', 'small_chick', 'carp', 'lobster', 'wasp', 'gopher', 'chick', 'sea_turtle', 'octopus', 'lizard', 'rabbit', 'pug', 'mouse', 'birdie', 'bat', 'owl', 'squirrel', 'rooster', 'cat', 'snake', 'crow', 'parrot', 'prey', 'chihuahua', 'fox', 'desert_fox', 'pig', 'dog', 'blackcat', 'coyote', 'goat', 'deer', 'bullking', 'seal', 'fury_cat', 'penguin', 'blueswirl', 'sly', 'husky', 'sheep', 'panda', 'cute_panda', 'angry_panda', 'bear', 'bear_', 'bearr', 'rhino_boxer', 'cougar', 'wolf', 'wolff', 'spirxo', 'sabertooth', 'panther', 'kempo_tiger', 'dark_wings', 'firebird', 'wolf_', 'lion_', 'yeti', 'lion', 'leo', 'king_lion', 'crocodile', 'croc', 'jackal', 'taurus', 'shark', 'colossus', 'orc_grunt', 'behemoth', 'mammoth', 'silver_tusk', 'dragon', 'beast', 'raptor', 't_rex', 'godzilla', 'basilisk', 'sentinel', 'poseidon', 'kraken', 'red_fiend', 'wendigo', 'jotun', 'ice_lord', 'medusa', 'reaper'];
USER_AGENTS = [
    # Chrome on Windows
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    # Chrome on macOS
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    # Firefox on Windows
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:127.0) Gecko/20100101 Firefox/127.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:126.0) Gecko/20100101 Firefox/126.0",
    # Firefox on macOS
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:127.0) Gecko/20100101 Firefox/127.0",
    # Safari on macOS
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Safari/605.1.15",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4.1 Safari/605.1.15",
    # Edge on Windows
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.2592.87",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36 Edg/125.0.2535.92",
    # Chrome on Linux
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
]

try:
    with open("jwts.txt", "r") as file:
        jwt_tokens = file.read().splitlines()
except FileNotFoundError as e:
    print(f"Error: Could not find {e.filename}. Please make sure jwts.txt and proxies.txt exist.")
    exit()


player_name = "𝕨𝕒𝕤𝕕𝕗"  

# Helper classes for storing game state
class GameNode:
    def __init__(self, node_id):
        self.node_id = node_id
        self.x = 0
        self.y = 0
        self.size = 0
        self.flags = 0
        self.color = (0, 0, 0)
        self.name = ""
        self.skin = ""

    def __repr__(self):
        return f"Node(id={self.node_id}, pos=({self.x:.0f}, {self.y:.0f}), size={self.size}, name='{self.name}')"

class BinaryReader:
    def __init__(self, buffer): self.buffer=buffer;self.offset=0
    def remaining(self): return len(self.buffer) - self.offset
    def read_uint8(self): val=struct.unpack_from('<B',self.buffer,self.offset)[0];self.offset+=1;return val
    def read_uint16(self): val=struct.unpack_from('<H',self.buffer,self.offset)[0];self.offset+=2;return val
    def read_int32(self): val=struct.unpack_from('<i',self.buffer,self.offset)[0];self.offset+=4;return val
    def read_uint32(self): val=struct.unpack_from('<I',self.buffer,self.offset)[0];self.offset+=4;return val
    def read_float(self): val=struct.unpack_from('<f',self.buffer,self.offset)[0];self.offset+=4;return val
    def read_double(self): val=struct.unpack_from('<d',self.buffer,self.offset)[0];self.offset+=8;return val
    def read_string_utf8(self):
        try:
            end_offset = self.buffer.find(b'\x00', self.offset)
            if end_offset == -1: end_offset = len(self.buffer)
            val = self.buffer[self.offset:end_offset].decode('utf-8'); self.offset = end_offset + (1 if end_offset != len(self.buffer) else 0); return val
        except Exception: return ""
    def read_string_unicode(self):
        try:
            end_offset = self.offset
            while end_offset < len(self.buffer) - 1:
                if self.buffer[end_offset] == 0 and self.buffer[end_offset + 1] == 0: break
                end_offset += 2
            val = self.buffer[self.offset:end_offset].decode('utf-16-le'); self.offset = end_offset + 2; return val
        except Exception: return ""
    def read_string_utf8(self):
        try:
            end_offset = self.buffer.index(b'\x00', self.offset)
            val = self.buffer[self.offset:end_offset].decode('utf-8')
            self.offset = end_offset + 1
            return val
        except ValueError:
            # No null terminator found, read to end
            val = self.buffer[self.offset:].decode('utf-8', errors='ignore')
            self.offset = len(self.buffer)
            return val
            
    def read_string_unicode(self):
        try:
            # Find the null terminator (2 bytes)
            end_offset = self.offset
            while end_offset < len(self.buffer) - 1:
                if self.buffer[end_offset] == 0 and self.buffer[end_offset + 1] == 0:
                    break
                end_offset += 2
            
            val = self.buffer[self.offset:end_offset].decode('utf-16-le')
            self.offset = end_offset + 2
            return val
        except (ValueError, IndexError):
            # No null terminator found or incomplete string
            val = self.buffer[self.offset:].decode('utf-16-le', errors='ignore')
            self.offset = len(self.buffer)
            return val

    def read_utf16le_zero_terminated_string(self):
        chars = []
        
        while self.offset + 1 < len(self.buffer):
            # Read 2 bytes as one UTF-16LE character
            char_code = struct.unpack_from('<H', self.buffer, self.offset)[0]
            self.offset += 2

            if char_code == 0:
                break

            chars.append(char_code)
        
        # Convert list of UTF-16 code units to string
        return bytes(struct.pack('<{}H'.format(len(chars)), *chars)).decode('utf-16le')

class BlobGameClient:
    def __init__(self, nickname, jwt_token, proxy, user_agent, control_server):
        self.nickname = nickname
        self.jwt_token = jwt_token
        self.proxy = proxy
        self.user_agent = user_agent
        self.ws = None
        self.control_server = control_server
        
        # Game State
        self.connected=False
        self.nodes = {}             # All visible nodes, keyed by node_id
        self.my_cell_ids = set()
        self.leaderboard = []
        self.border = {}
        self.center_pos = {'x': 0, 'y': 0}
        self.score = 0
        
        # Mouse position for sending
        self.mouse_target = {'x': 0, 'y': 0}

        self.stopped = False
        
        # Scramble values received from server (usually in SetBorder packet)
        self.scramble_x = 0
        self.scramble_y = 0
        self.scramble_id = 0 # Not directly sent by server, but used in packets
        
        # Event to signal when the spawn is confirmed (i.e., we know our cell ID)
        self.spawn_confirmed = asyncio.Event()
        self.is_respawning = False

        # HTTP session for API calls
        self.session = httpx.AsyncClient(verify=False)

    async def _respawn_loop(self):
        if self.is_respawning:
            return

        self.is_respawning = True
        print(f"[{self.nickname}] Starting respawn loop...")

        while len(self.my_cell_ids) == 0:
            print(f"[{self.nickname}] Attempting to spawn...")
            await self._send_spawn(self.nickname)
            await asyncio.sleep(2.5)

        print(f"[{self.nickname}] Respawn successful!")
        self.is_respawning = False



    async def connect(self):
        """Establishes the WebSocket connection with all necessary headers."""
        headers = {
            'Origin': ORIGIN,
            'User-Agent': self.user_agent,
            'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
            'Pragma': 'no-cache',
            'Cache-Control': 'no-cache',
            'Accept-Encoding': 'gzip, deflate',
        }
        
        # The subprotocols list is crucial for authentication
        subprotocols = [
            "7", "3", "WaWdft", self.jwt_token
        ]
        
        try:
            print(f"[{self.nickname}] Attempting to connect via {self.proxy or 'DIRECT'}")
            proxy_arg = {'proxy': self.proxy} if self.proxy else {}
            self.ws = await websockets.connect(
                SERVER_URI,
                additional_headers=headers,
                subprotocols=subprotocols,
                **proxy_arg,
            )
            print(f"Successfully connected to {SERVER_URI}!")
            #print(f"Server selected subprotocol: {self.ws.subprotocol}")
            self.connected=True
            # self.control_server.update_bot_status(self.nickname, self.get_status())

            # Start concurrent sender and receiver loops
            receiver_task = asyncio.create_task(self._receiver())
            sender_task = asyncio.create_task(self._sender())
            
            await asyncio.gather(sender_task, receiver_task)

        except (websockets.exceptions.InvalidStatusCode, websockets.exceptions.ProxyError,
                python_socks.ProxyConnectionError, ConnectionRefusedError, TimeoutError, websockets.exceptions.InvalidStatus) as e:
            print(f"[{self.nickname}] Connection failed: {type(e).__name__}. This proxy may be bad or the server is blocking it.")
        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            self.connected = False
            # self.control_server.update_bot_status(self.nickname, self.get_status())


    async def _receiver(self):
        """Receives and parses messages from the server."""
        while True:
            try:
                message = await self.ws.recv()
                self._parse_packet(message)
            except websockets.exceptions.ConnectionClosed as e:
                print(f"Receiver: Connection was closed. Code: {e.code}, Reason: {e.reason}")
                self.connected = False
                break
            except Exception as e:
                print(f"Receiver: An error occurred while processing a message: {e}")
                self.connected = False
                raise
                break

    async def _sender(self):
        """Sends messages to the server, including handshake and periodic updates."""
        try:
            # 1. Send binary handshake
            await self._send_handshake()
            
            # 2. Send spawn request
            await self._send_spawn(self.nickname)

            await asyncio.sleep(0.2)
            print("Sender: Spawn confirmed! Starting mouse updates.")
            
            # 4. Main gameplay loop (sending mouse coordinates)
            while True:
                # Update mouse target from control server
                if not self.stopped:
                    self.mouse_target = self.control_server.get_mouse_coords()
                else:
                    self.mouse_target = self.center_pos # i.e. don't move
                
                await self._send_mouse_target(self.mouse_target['x'], self.mouse_target['y'])
                
                # Send at a high frequency, similar to a real client
                await asyncio.sleep(0.04) # ~25 updates per second

        except websockets.exceptions.ConnectionClosed:
            print("Sender: Connection was closed.")
        except Exception as e:
            print(f"Sender: An error occurred: {e}")

    
    

    # --- Packet Sending Methods ---
    async def _send_handshake(self):
        """Sends the initial binary handshake sequence."""
        # Opcode 254: Protocol Version (5)
        packet_254 = struct.pack('<BI', 254, 5)
        await self.ws.send(packet_254)
        #print(f"Sent Handshake Part 1 (Protocol): {packet_254.hex(" ").upper()}")
        
        # Opcode 255: Client Key (from HAR)
        # 0x09381223 (LE) -> 23 12 38 09 (hex)
        packet_255 = struct.pack('<BI', 255, 154669603)
        await self.ws.send(packet_255)
        #print(f"Sent Handshake Part 2 (Client Key): {packet_255.hex(' ').upper()}")

        # Opcode 5: Custom/Third Handshake message (from HAR)
        message = "0507000000370000000000000026da334137000000004406377d"
        packet_5 = binascii.unhexlify(message)
        await self.ws.send(packet_5)
        #print(f"Sent Handshake Part 3 (Opcode 5): {packet_5.hex(' ').upper()}")

    async def _send_spawn(self, name):
        """Sends the spawn request (name and confirmation)."""
        self.sent_spawn = True
        # Opcode 0: Nickname (UTF-16LE)
        opcode_byte = b'\x00'
        encoded_name = name.encode('utf-16-le')
        packet_0 = opcode_byte + encoded_name
        
        await self.ws.send(packet_0)
        print(f"Sent Spawn (Name): {name}")
        #print(f"Packet 0: {packet_0.hex(' ').upper()}")

        # Opcode 1: Confirm Spawn
        packet_1 = struct.pack('<B', 1)
        await self.ws.send(packet_1)
        print("Sent Spawn (Confirm)")
        print(f"Packet 1: {packet_1.hex(' ').upper()}") 


    async def _send_mouse_target(self, x, y):
        """Sends the mouse target coordinates (Opcode 16)."""
        packet = struct.pack('<BiiI', 16, int(x), int(y), 0)
        await self.ws.send(packet)

    async def _send_split(self):
        await self.ws.send(bytes([0x11]))

    async def _send_feed(self):
        await self._send_start_feed()
        await asyncio.sleep(0.1)
        await self._send_stop_feed()

    async def _send_start_feed(self):
        await self.ws.send(bytes([0x20]))

    async def _send_stop_feed(self):
        await self.ws.send(bytes([0x21]))

    def toggle_stopped(self):
        self.stopped = not self.stopped

    # --- Packet Parsing Logic ---
    def _parse_packet(self, message):
        """Dispatches packet parsing based on opcode."""
        if not isinstance(message, bytes) or len(message) == 0:
            return
            
        reader = BinaryReader(message)
        opcode = reader.read_uint8()

        # Packet dispatcher
        handlers = {
            16: self._parse_update_nodes,    # 0x10
            17: self._parse_update_position, # 0x11
            18: self._parse_clear_all,       # 0x12
            32: self._parse_add_node,        # 0x20
            49: self._parse_update_leaderboard_ffa, # 0x31
            50: self._parse_update_leaderboard_team, # 0x32
            53: self._stub_handler,      # 0x35 (custom opcode, stub handler)
            64: self._parse_set_border,      # 0x40
            67: self._stub_handler,      # 0x43 (custom opcode, stub handler)
            99: self._parse_chat_message,    # 0x63
            253: self._handle_second_handshake,      # 0xFD
            254: self._parse_server_stat,    # 0xFE
        }

        handler = handlers.get(opcode)
        if handler:
            handler(reader)
        else:
            print(f"Received unknown opcode: {opcode} with data: {message}")
    def _stub_handler(self, reader):
        opcode = reader.buffer[reader.offset-1]

    def unpack_colour(packed_colour):
        """Unpack a packed color value into RGB components."""
        r = (packed_colour >> 11) & 0x1F
        g = (packed_colour >> 5) & 0x3F
        b = packed_colour & 0x1F
        return round(r * 255 / 31), round(g * 255 / 63), round(b * 255 / 31) # scale to 0-255 range

    def _parse_update_nodes(self, reader):
        destroyed_nodes, added_nodes, removed_nodes = parser.parse_nodes(reader.buffer) # Use the parser module to handle node parsing
        for node in added_nodes:
            node_id = node.node_id
            if node_id not in self.nodes:
                self.nodes[node_id] = node
            else:
                # Update existing node
                existing_node = self.nodes[node_id]
                existing_node.x = node.x
                existing_node.y = node.y
                existing_node.size = node.size
                existing_node.flags = node.flags
                existing_node.color = node.color
                existing_node.name = node.name
                existing_node.skin = node.skin
            if node.u:
                self.my_cell_ids.add(node_id)

        for node_id in removed_nodes:
            if node_id in self.nodes:
                del self.nodes[node_id]
            if node_id in self.my_cell_ids:
                self.my_cell_ids.remove(node_id)

        for killer_id, prey_id in destroyed_nodes:
            if prey_id in self.nodes:
                del self.nodes[prey_id]
            if prey_id in self.my_cell_ids:
                self.my_cell_ids.remove(prey_id)

        if len(self.my_cell_ids) == 0 and not self.is_respawning:
            asyncio.create_task(self._respawn_loop())
        
        self._update_player_state()

    def _parse_update_position(self, reader):
        self.center_pos['x'] = reader.read_float() - self.scramble_x
        self.center_pos['y'] = reader.read_float() - self.scramble_y
        scale = reader.read_float()
        print(f"Camera update: Pos=({self.center_pos['x']:.0f}, {self.center_pos['y']:.0f}), Scale={scale:.2f}")

    def _parse_clear_all(self, reader):
        self.nodes.clear()
        self.my_cell_ids.clear()
        print("Received ClearAll: All nodes cleared.")

    def _parse_add_node(self, reader):
        node_id = reader.read_uint32()
        print(f"Received AddNode for ID: {node_id} (Details will come in next UpdateNodes)")

    def _parse_update_leaderboard_ffa(self, reader):
        return
        self.leaderboard = []
        count = reader.read_uint16()
        for i in range(count):
            id = reader.read_uint16()
            name = reader.read_utf16le_zero_terminated_string() # For protocol 5
            self.leaderboard.append({'name': name})

    def _parse_update_leaderboard_team(self, reader):
        self.leaderboard = []
        count = reader.read_uint32()
        for i in range(count):
            self.leaderboard.append(reader.read_float())
        print(f"Leaderboard (Team): {self.leaderboard}")
        
    def _parse_set_border(self, reader):
        left = reader.read_double()
        top = reader.read_double()
        right = reader.read_double()
        bottom = reader.read_double()
        game_type = reader.read_uint32()
        server_name = reader.read_string_utf8()

        self.border = {'left': left, 'top': top, 'right': right, 'bottom': bottom}
        print(f"Border set: {self.border}, GameType: {game_type}, ServerName: '{server_name}'")

    def _parse_chat_message(self, reader):
        flags = reader.read_uint8()
        color = (reader.read_uint8(), reader.read_uint8(), reader.read_uint8())
        name = reader.read_string_unicode()
        message = reader.read_string_unicode()
        print(f"[CHAT] {name}: {message}")

    def _parse_server_stat(self, reader):
        stat_json = reader.read_string_zero_utf8()
        print(f"Server Stats: {json.loads(stat_json)}")

    def _handle_second_handshake(self, reader):
        """Handles the second handshake packet (opcode 253)."""
        e = reader.read_int32()
        f = reader.read_int32()
        d = ctypes.c_int32((e & f) | ((e << (f & 0x1F)) ^ e)).value
        packet_bytes = struct.pack('<bi', -3, d)
        
        #print(f"Second Handshake: Sending response with d={d} (hex: {packet_bytes.hex().upper()})")

        try:
            asyncio.create_task(self.ws.send(packet_bytes))
            #print(f"Sent Second Handshake Response: {packet_bytes.hex(' ').upper()}")
        except websockets.exceptions.ConnectionClosed as e:
            print(f"Second Handshake: Connection closed while sending response. Code: {e.code}, Reason: {e.reason}")




    def _update_player_state(self):
        """Calculates score and center position from owned cells."""
        if not self.my_cell_ids:
            self.score = 0
            # self.control_server.update_bot_status(self.nickname, self.get_status())
            return

        total_mass = 0
        center_x = 0
        center_y = 0
        
        valid_cells = 0
        for cell_id in self.my_cell_ids:
            if cell_id in self.nodes:
                cell = self.nodes[cell_id]
                mass = cell.size * cell.size / 100
                total_mass += mass
                center_x += cell.x * mass
                center_y += cell.y * mass
                valid_cells += 1

        if total_mass > 0:
            self.center_pos['x'] = center_x / total_mass
            self.center_pos['y'] = center_y / total_mass
            self.score = int(total_mass)
        else:
            self.score = 0
        
        # self.control_server.update_bot_status(self.nickname, self.get_status())

    def get_status(self):
        return {
            "connected": self.connected,
            "score": self.score,
            "position": self.center_pos,
            "distance": math.hypot(self.center_pos["x"] - self.mouse_target["x"], self.center_pos["y"] - self.mouse_target["y"])
        }



class ControlServer:
    def __init__(self, host="localhost", port=8765):
        self.host = host
        self.port = port
        self.clients = set()
        self.bots = []
        self.mouse_coords = {'x': 0, 'y': 0}

    async def register(self, websocket):
        self.clients.add(websocket)
        try:
            await websocket.wait_closed()
        finally:
            self.clients.remove(websocket)

    async def broadcast_status(self):
        while True:
            if self.clients:
                message = json.dumps({"type": "status", "bots": {str(bot_id+1): bot.get_status() for bot_id, bot in enumerate(self.bots)}})
                await asyncio.gather(*(client.send(message) for client in self.clients))
                #print(f"Broadcasting to {len(self.clients)} clients")
            await asyncio.sleep(1/50)

    async def handle_client(self, websocket):
        asyncio.create_task(self.register(websocket))
        print(f"New client connected: {websocket}")
        async for message in websocket:
            # print(f"Received message: {message}")
            data = json.loads(message)
            if data['type'] == 'mouse':
                self.mouse_coords = data['coords']
                # print(f"Received mouse coords: {self.mouse_coords}")
            elif data['type'] == 'split':
                # print("Received split request")
                for bot in self.bots:
                    if bot.get_status()["connected"]:
                        asyncio.create_task(bot._send_split())
            elif data["type"] == "feed":
                for bot in self.bots:
                    if bot.get_status()["connected"]:
                        asyncio.create_task(bot._send_feed())
            elif data["type"] == "start_feed":
                for bot in self.bots:
                    if bot.get_status()["connected"]:
                        asyncio.create_task(bot._send_start_feed())
            elif data["type"] == "stop_feed":
                for bot in self.bots:
                    if bot.get_status()["connected"]:
                        asyncio.create_task(bot._send_stop_feed())
            elif data["type"] == "toggle_stopped":
                for bot in self.bots:
                    if bot.get_status()["connected"]:
                        bot.toggle_stopped()

    def get_mouse_coords(self):
        return self.mouse_coords

    def add_bot_client(self, bot_client):
        self.bots.append(bot_client)

    async def start(self):
        server = await websockets.serve(self.handle_client, self.host, self.port)
        print(f"Control server started on ws://{self.host}:{self.port}")
        asyncio.create_task(self.broadcast_status())
        await server.wait_closed()


async def manage_bot_lifecycle(jwt_token, proxy_manager, bot_config, control_server):
    """A loop that manages a single bot, respawning it on failure."""
    bot_id = bot_config['name']
    while True:
        proxy = None
        if bot_config['use_proxy'] and proxy_manager:
            proxy = proxy_manager.get_next_proxy()
        
        user_agent = random.choice(USER_AGENTS)
        client = BlobGameClient(bot_id, jwt_token, proxy, user_agent, control_server)
        control_server.add_bot_client(client)
        
        await client.connect() # This will block until the client disconnects

        # The bot disconnected, wait before respawning
        cooldown = random.uniform(15, 30)
        print(f"Bot {bot_id} has disconnected. Respawning in {cooldown:.1f} seconds.")
        await asyncio.sleep(cooldown)     

async def main():
    print("Starting bot farm...")
    if not jwt_tokens:
        print("No JWTs found in jwts.txt. Exiting.")
        return

    num_bots_with_proxy = 0
    num_bots_no_proxy = 2
    proxy_manager = None # No proxies needed

    if len(jwt_tokens) < (num_bots_no_proxy + num_bots_with_proxy):
        print("Not enough JWT tokens for the number of bots configured. Exiting.")
        return

    control_server = ControlServer()
    
    tasks = []
    jwt_iter = iter(jwt_tokens)

    # Launch bots
    for i in range(num_bots_no_proxy + num_bots_with_proxy):
        use_proxy_flag = i >= num_bots_no_proxy
        bot_config = {
            "name": f"neuro",
            "use_proxy": use_proxy_flag
        }
        
        task = asyncio.create_task(manage_bot_lifecycle(next(jwt_iter), proxy_manager, bot_config, control_server))
        tasks.append(task)
        
        startup_delay = random.uniform(3, 8)
        print(f"Launching {bot_config['name']} in {startup_delay:.1f} seconds...")
        await asyncio.sleep(startup_delay)

    await asyncio.gather(control_server.start(), *tasks)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nShutting down bot farm.")



