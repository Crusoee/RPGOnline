import socket
import pyray as rl
import raylib as raylib
from Player import Player
import pickle
from CONSTANTS import SCREEN_WIDTH, SCREEN_HEIGHT, TILE_SIZE, CHUNK_SIZE, NUM_CHUNKS

from Perlin import generate_terrain_chunk, generate_terrain_chunk, simplex_noise
from Generation import unpack_landmarks, unpack_colors

import random

import zlib
import threading

# --- main ---

host = '192.168.56.1'
port = 65432

running = True

def get_message(conn, use_compression=True):
    # Receive total size of the data
    total_size = int.from_bytes(conn.recv(4), 'big')
    
    # Receive data in chunks
    received_data = b''
    while len(received_data) < total_size:
        chunk = conn.recv(min(1024, total_size - len(received_data)))
        if not chunk:
            raise ConnectionError("Connection closed while receiving data")
        received_data += chunk
    
    # Optionally decompress data
    if use_compression:
        received_data = zlib.decompress(received_data)
    
    # Deserialize data
    return pickle.loads(received_data)

def send_message(conn, data, use_compression=True):
    # Serialize data
    serialized_data = pickle.dumps(data)
    
    # Optionally compress data
    if use_compression:
        serialized_data = zlib.compress(serialized_data)
    
    # Send total size of the data first
    total_size = len(serialized_data)
    conn.sendall(total_size.to_bytes(4, 'big'))
    
    # Send data in chunks
    chunk_size = 1024
    for i in range(0, total_size, chunk_size):
        chunk = serialized_data[i:i + chunk_size]
        conn.sendall(chunk)

def game_loop(shared_memory):
    global running
    raylib.InitWindow(SCREEN_WIDTH, SCREEN_HEIGHT, b"Hide And Seek")
    raylib.SetTargetFPS(60)

    # Load tile textures
    water_tile = rl.load_texture("topdown_tiles\\tiles\\deep0\\straight\\0\\0.png")
    sand_tile = rl.load_texture("topdown_tiles\\tiles\\beach0\\straight\\0\\0.png")
    grass_tile = rl.load_texture("topdown_tiles\\tiles\\grass0\\straight\\0\\0.png")
    shallow_tile = rl.load_texture("topdown_tiles\\tiles\\shallow0\\straight\\0\\0.png")
    forest_tile = rl.load_texture("topdown_tiles\\Forest.png")
    rock_tile = rl.load_texture("topdown_tiles\\Mountain.png")

    shallow = 0
    water = -.1
    sand = 0.1
    grass = 0.3
    forest = 0.45
    rocks = None

    def get_tile_texture(value):
        if value < water:
            return water_tile
        elif value < shallow:
            return shallow_tile
        elif value < sand:
            return sand_tile
        elif value < grass:
            return grass_tile
        elif value < forest:
            return forest_tile
        else:
            return rock_tile

    # Initialize chunk data
    chunk_data = {}

    while not raylib.WindowShouldClose():
        
        value = simplex_noise(shared_memory['player'].locsize.x // TILE_SIZE, 
                              shared_memory['player'].locsize.y // TILE_SIZE)

        if value < water:
            shared_memory['player'].speed = 150
        else:
            shared_memory['player'].speed = 300

        shared_memory['player'].move()

        raylib.BeginDrawing()
        raylib.ClearBackground(rl.RAYWHITE)
        raylib.BeginMode2D(shared_memory['player'].camera)

        # Calculate player's chunk position
        player_chunk_x = shared_memory['player'].locsize.x // (CHUNK_SIZE * TILE_SIZE)
        player_chunk_y = shared_memory['player'].locsize.y // (CHUNK_SIZE * TILE_SIZE)

        # Determine visible chunk range
        chunk_x_start = player_chunk_x - NUM_CHUNKS // 2
        chunk_y_start = player_chunk_y - NUM_CHUNKS // 2
        chunk_x_end = chunk_x_start + NUM_CHUNKS
        chunk_y_end = chunk_y_start + NUM_CHUNKS

        # Loop through visible chunks
        for chunk_y in range(int(chunk_y_start), int(chunk_y_end)):
            for chunk_x in range(int(chunk_x_start), int(chunk_x_end)):
                # Generate chunk if not already cached
                if (chunk_x, chunk_y) not in chunk_data:
                    chunk_data[chunk_x, chunk_y] = generate_terrain_chunk(chunk_x, chunk_y)
                    # print(chunk_x, chunk_y)

                # Draw tiles in the chunk
                for y in range(CHUNK_SIZE):
                    for x in range(CHUNK_SIZE):
                        tile_type = chunk_data[chunk_x, chunk_y][y][x]
                        tile_texture = get_tile_texture(tile_type)
                        tile_draw_x = (chunk_x * CHUNK_SIZE + x) * TILE_SIZE
                        tile_draw_y = (chunk_y * CHUNK_SIZE + y) * TILE_SIZE
                        rl.draw_texture(tile_texture, tile_draw_x, tile_draw_y, rl.WHITE)

        # Draw shared_memory[0] data received from the server
        for key, value in shared_memory['players'][0].items():
            if key == shared_memory['user']:
                continue
            raylib.DrawRectangleRec(rl.Rectangle(shared_memory['players'][0][key][0], shared_memory['players'][0][key][1], shared_memory['players'][0][key][2], shared_memory['players'][0][key][3]), shared_memory['players'][0][key][4])

        raylib.DrawRectangleRec(shared_memory['player'].locsize, shared_memory['player'].color)

        if shared_memory['player'].coordinate != None:
            raylib.DrawCircle(int(shared_memory['player'].coordinate.x), int(shared_memory['player'].coordinate.y), 10.0, rl.YELLOW)

        raylib.EndMode2D()
        # rl.draw_text(f"{1 / (raylib.GetFrameTime() + .00000000001)}", 50, 50, 40, rl.DARKBLUE)
        rl.draw_text(f"X: {shared_memory['player'].locsize.x // TILE_SIZE}, Y: {shared_memory['player'].locsize.y // TILE_SIZE}", 50, 50, 40, rl.DARKBLUE)
        raylib.EndDrawing()

    running = False
    raylib.CloseWindow()

def communication_loop(shared_memory):
    global running
    s = socket.socket()
    s.connect((host, port))
    print("Connected to the server")

    shared_memory['user'] = get_message(s)
    shared_memory['landscape'] = get_message(s)

    while running:
        send_message(s, [shared_memory['player'].locsize.x, shared_memory['player'].locsize.y, 
                         shared_memory['player'].locsize.width, shared_memory['player'].locsize.height, 
                         shared_memory['player'].color],False)
        
        shared_memory['players'] = get_message(s,False)
    ...

def main() -> int:

    player = Player(rl.SKYBLUE, rl.Rectangle(random.randint(-357018,357018), random.randint(-357018,357018), 40, 80), 500)

    shared_memory = {"player" : player,
                     "landscape" : [[],[]],
                     "players" : [{}],
                     "user" : ""}



    communicationloop = threading.Thread(target=communication_loop, args=(shared_memory,))
    communicationloop.start()

    gameloop = threading.Thread(target=game_loop, args=(shared_memory,))
    gameloop.start()


    gameloop.join()

    return 0

if __name__ == "__main__":
    exit(main())