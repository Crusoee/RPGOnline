import socket
import pyray as rl
import raylib as raylib
from Player import Player
import pickle
from CONSTANTS import SCREEN_WIDTH, SCREEN_HEIGHT

import random
from Generation import unpack_landmarks, unpack_colors

import zlib

import threading

# --- main ---

host = '192.168.56.1'
port = 65432

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

def game_loop(player):
    while not raylib.WindowShouldClose():
        print(player.locsize.x,player.locsize.y)
    ...

def main() -> int:
    s = socket.socket()
    s.connect((host, port))
    print("Connected to the server")

    landmarks = unpack_landmarks(get_message(s))
    colors = unpack_colors(get_message(s))

    player = Player(rl.RED, rl.Rectangle(0, 0, 40, 80), 300)

    data = []

    raylib.InitWindow(SCREEN_WIDTH, SCREEN_HEIGHT, b"Hide And Seek")
    raylib.SetTargetFPS(60)

    # gameloop = threading.Thread(target=game_loop, args=(player,))
    # gameloop.start()

    while not raylib.WindowShouldClose():
        player.move()

        send_message(s, [player.locsize.x, player.locsize.y, player.locsize.width, player.locsize.height, player.color])

        data = get_message(s)

        raylib.BeginDrawing()
        raylib.ClearBackground(rl.RAYWHITE)
        raylib.BeginMode2D(player.camera)

        raylib.DrawRectangle(0,0,200,50,rl.BLUE)

        for i in range(len(landmarks)):
            raylib.DrawRectangleRec(landmarks[i], colors[i])
        
        # Draw player data received from the server
        for key, value in data[0].items():
            # print(data[0][key][0], data[0][key][1], data[0][key][2], data[0][key][3], data[0][key][4])
            raylib.DrawRectangleRec(rl.Rectangle(data[0][key][0], data[0][key][1], data[0][key][2], data[0][key][3]), rl.GREEN)

        raylib.DrawRectangleRec(player.locsize, player.color)

        if player.coordinate != None:
            raylib.DrawCircle(int(player.coordinate.x),int(player.coordinate.y),10.0,rl.YELLOW)

        raylib.EndMode2D()
        raylib.EndDrawing()

    raylib.CloseWindow()
    s.close()

    # gameloop.join()

    return 0

if __name__ == "__main__":
    exit(main())