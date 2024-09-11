import socket
import multiprocessing
import pickle
import zlib
import time


from SimplexNoise import simplex_noise

# Constants
HOST = "0.0.0.0"
PORT = 65432
TICK_RATE = 1 / 60 # 60 Hz

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

def get_status(client_data):
    while True:
        time.sleep(20)
        print("Amount of Players: ", len(client_data))

def game_loop(client_data, client_data_lock, action_queue):
    try:
        while True: 
            start_time = time.time()
                
            # Process all actions from the queue
            while not action_queue.empty():
                action = action_queue.get()
                target = client_data[action['target']]
                attacker = client_data[action['attacker']]
                # Player attack
                if action['type'] == 'attack':
                    # if action['target'] in client_data and action['attacker'] in client_data:
                    
                    # damage = action['damage']

                    target['hlth'] -= attacker['dmg']

                    with client_data_lock:
                        client_data[action['target']] = target


            # making a sendable copy of client data that doesn't have the socket connection
            client_data_sendable = dict(client_data).copy()
            for addr, stats in client_data_sendable.items():
                client_data_sendable[addr].pop('conn', None)

            # Update all clients
            with client_data_lock:
                for addr, stats in client_data_sendable.items():
                    send_message(client_data[addr]['conn'], [client_data_sendable], False)

            # Wait until the next tick
            elapsed = time.time() - start_time
            if elapsed < TICK_RATE:
                time.sleep(TICK_RATE - elapsed)
    except (KeyError) as e:
        print("Errors!!: ", e)
    ...

def handle_client(conn, addr, client_data, client_data_lock, action_queue):
    print(f"Connection with {addr[0]} on port {addr[1]} started...")
    conn.settimeout(5.0)

    username = f"{addr[0]}:{addr[1]}"

    send_message(conn, username)

    stats = {
                'user' : username,
                'x' : 0,
                'y' : 0,
                'nme' : '',
                'dmg' : 1,
                'mgc' : 0,
                'arm' : 0,
                'hlth' : 10,
                'hit' : '',
                'ats' : .5,
                'conn' : conn
            }
    
    with client_data_lock:
        client_data[username] = stats

    while True:
        try:
            stats = client_data[username]

            data = get_message(conn, False)
            
            if data in [0, None]:
                break

            # Stats that the server trusts from the client
            stats['x'] = data[0]['x']
            stats['y'] = data[0]['y']
            stats['nme'] = data[0]['nme']

            # print(data[0])
            
            if data[0]['action']['type'] != None:
                data[0]['action']['attacker'] = username
                action_queue.put(data[0]['action'])

            with client_data_lock:
                client_data[username] = stats

        except (TimeoutError, EOFError, KeyError, ConnectionResetError) as e:
            print(f"Error processing data from {username}: {e}")
            break

    client_data.pop(username, None)
    print(f"Connection with {addr[0]} on port {addr[1]} finished...")

def start_server():
    client_data_lock = multiprocessing.Lock()
    manager = multiprocessing.Manager()

    client_data = manager.dict()
    action_queue = manager.Queue()

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        print(f"Server listening on {HOST}:{PORT}")

        # multiprocessing.Process(target=get_status, args=(client_data,)).start()
        multiprocessing.Process(target=game_loop, args=(client_data, client_data_lock, action_queue)).start()

        while True:
            try:
                conn, addr = s.accept()
                multiprocessing.Process(target=handle_client, args=(conn, addr, client_data, client_data_lock, action_queue)).start()
            except KeyboardInterrupt:
                print("Server shutting down...")
                break
            except Exception as e:
                print(f"Server error: {e}")

if __name__ == "__main__":
    print('Server Starting...')
    start_server()
