import socket
import multiprocessing
import pickle
import zlib
import logging

from SimplexNoise import simplex_noise

# Constants
HOST = "0.0.0.0"
PORT = 65432

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

def handle_client(conn, addr, client_data, client_data_lock):
    logging.info(f"Connection with {addr[0]} on port {addr[1]} started...")
    conn.settimeout(5.0)

    send_message(conn, f"{addr[0]}:{addr[1]}")

    try:
        while True:
            try:
                data = get_message(conn, False)
                
                if data in [0, None]:
                    break

                with client_data_lock:
                    client_data[f"{addr[0]}:{addr[1]}"] = data

                send_message(conn, [dict(client_data), addr[0]], False)
            except Exception as e:
                logging.error(f"Error processing data from {addr[0]}:{addr[1]}: {e}")
                break
    finally:
        with client_data_lock:
            client_data.pop(f"{addr[0]}:{addr[1]}", None)
        logging.info(f"Connection with {addr[0]} on port {addr[1]} finished...")

def start_server():
    client_data_lock = multiprocessing.Lock()
    manager = multiprocessing.Manager()
    client_data = manager.dict()

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        logging.info(f"Server listening on {HOST}:{PORT}")

        while True:
            try:
                conn, addr = s.accept()
                multiprocessing.Process(target=handle_client, args=(conn, addr, client_data, client_data_lock)).start()
            except KeyboardInterrupt:
                logging.info("Server shutting down...")
                break
            except Exception as e:
                logging.error(f"Server error: {e}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    start_server()
