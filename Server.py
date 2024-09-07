import socket
import threading
import pickle

import zlib
from Generation import landmark_generation, color_generation
from Perlin import generate_landscape

hostname = socket.gethostname()
IPAddr = socket.gethostbyname(hostname)

HOST = "0.0.0.0"  # Standard loopback interface address (localhost)
PORT = 65432  # Port to listen on (non-privileged ports are > 1023)

run = True
client_data = {}
data_lock = threading.Lock()


landscape = generate_landscape()

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


def player_data(conn, addr):
    print(f"Threaded connection with {addr[0]} on port {addr[1]} started...")
    conn.settimeout(5.0)

    send_message(conn, f"{addr[0]}:{addr[1]}")
    send_message(conn, landscape)

    with conn:
        while True:
            try:
                data = get_message(conn, False)
                

                if data == 0 or None:
                    break

                with data_lock:
                    client_data[f"{addr[0]}:{addr[1]}"] = data

                send_message(conn, [client_data, addr[0]], False)
            except (pickle.PickleError, OSError, EOFError) as e:
                print(f"Error processing data from {addr[0]}: {e}")
                break
    with data_lock:
        client_data.pop(f"{addr[0]}:{addr[1]}", None)
    print(f"Threaded connection with {addr[0]} on port {addr[1]} finished...")

def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        print(f"Server listening on {HOST}:{PORT}")

        while run:
            try:
                conn, addr = s.accept()
                threading.Thread(target=player_data, args=(conn, addr)).start()
            except KeyboardInterrupt:
                print("Server shutting down...")
                break
            except Exception as e:
                print(f"Server error: {e}")

if __name__ == "__main__":
    start_server()