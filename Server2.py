import socket
import multiprocessing
import pickle
import zlib
import time
import random
import os

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

def game_loop(client_updates, client_data_lock, action_queue, client_info):
    while True: 
        try:    
            start_time = time.time()
                
            # Process actions
            while not action_queue.empty():
                action = action_queue.get()
                target = client_info[action['target']]
                attacker = client_info[action['attacker']]

                # Player attack
                if action['type'] == 'attack' and attacker['atc'] >= attacker['ats'] and attacker['hlth'] > 0 and target['hlth'] > 0:
                    # Damage Calculation
                    target['hlth'] -= attacker['dmg'] + ((random.randint(1,100)*.01) * (attacker['crit']))
                    # Reset attack Counter
                    attacker['atc'] = 0

                    if target['hlth'] <= 0:
                        attacker['killcount'] += 1

                with client_data_lock:
                    client_info[action['target']] = target
                    client_info[action['attacker']] = attacker

            # client tick updates
            for addr, stats in client_info.items():

                client = client_info[addr]

                # Melee Attacking
                if client['atc'] < client['ats']:
                    client['atc'] += 1

                # Respawning
                if client['hlth'] <= 0:
                    client['rescntr'] += 1
                    if client['rescntr'] >= client['ress']:
                        client['hlth'] = client['mhlth']
                        client['rescntr'] = 0

                client_info[addr] = client

            # Update all clients
            with client_data_lock:
                # making a sendable copy of client data that doesn't have the socket connection
                client_info_sendable = dict(client_info)
                for addr, value in client_info_sendable.items():
                    client_info_sendable[addr].pop('conn', None)
                for addr, stats in client_info_sendable.items():
                    # sending 2 messages to all clients with both updates and info on other clients
                    send_message(client_info[addr]['conn'], [dict(client_updates)], False)
                    send_message(client_info[addr]['conn'], [client_info_sendable], False)

            # Wait until the next tick
            elapsed = time.time() - start_time
            if elapsed < TICK_RATE:
                time.sleep(TICK_RATE - elapsed)
        except (TimeoutError, EOFError, KeyError, ConnectionResetError, ConnectionAbortedError) as e:
            print(f"Error processing data: {e}")

def handle_client(conn, addr, client_updates, client_data_lock, action_queue, client_info):
    print(f"Connection with {addr[0]} on port {addr[1]} started...")
    conn.settimeout(5.0)

    username = f"{addr[0]}:{addr[1]}"

    # files = os.walk("ServerDB")
    # if username in files:
    #     with open(f"ServerDB\\{username}.pl", "r") as f:
    #         for line in f.readlines()
    # else:
    #     with open(f"ServerDB\\{username}.pl", "w") as f:
    #         for line in f.write(f"0,0,,{username},15,2,0,0,100,100,")

    # sending them their user name in the server
    send_message(conn, username)

    updates =  {
                'x' : 0,
                'y' : 0,
                'nme' : '',
                'swim' : False
            }

    info = {
                'user' : username,

                'dmg' : 15,
                'crit' : 2,

                'mgc' : 0,

                'arm' : 0,

                'hlth' : 100,
                'mhlth' : 100,

                'hit' : '',

                'ats' : 60,
                'atc' : 60,

                'ress' : 600,
                'rescntr' : 0,

                'speed' : 300,
                'swmspeed' : 150,

                'killcount' : 0,

                'conn' : conn
            }
    
    # setting up client
    client_updates[username] = updates
    client_info[username] = info

    while True:
        try:
            # creating a mutable copy of client data
            info = client_updates[username]

            # get the message from the client
            updates = get_message(conn, False)
            
            if updates in [0, None]:
                break

            # Stats that the server trusts from the client
            info['x'] = updates[0]['x']
            info['y'] = updates[0]['y']
            info['nme'] = updates[0]['nme']
            info['swim'] = updates[0]['swim']

            # If an action is created by the client, add it to the queue
            if updates[0]['action']['type'] != None:
                updates[0]['action']['attacker'] = username
                action_queue.put(updates[0]['action'])

            # Finally, update the client_updates dict
            client_updates[username] = info

        except (TimeoutError, EOFError, KeyError, ConnectionResetError) as e:
            print(f"Error processing data from {username}: {e}")
            break

    client_updates.pop(username, None)
    client_info.pop(username, None)
    print(f"Connection with {addr[0]} on port {addr[1]} finished...")

def start_server():
    client_stats_lock = multiprocessing.Lock()
    manager = multiprocessing.Manager()

    client_data = manager.dict()
    client_stats = manager.dict()
    action_queue = manager.Queue()

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        print(f"Server listening on {HOST}:{PORT}")

        # multiprocessing.Process(target=get_status, args=(client_data,)).start()
        multiprocessing.Process(target=game_loop, args=(client_data, client_stats_lock, action_queue, client_stats)).start()

        while True:
            try:
                conn, addr = s.accept()
                multiprocessing.Process(target=handle_client, args=(conn, addr, client_data, client_stats_lock, action_queue, client_stats)).start()
            except KeyboardInterrupt:
                print("Server shutting down...")
                break
            except Exception as e:
                print(f"Server error: {e}")

if __name__ == "__main__":
    print('Server Starting...')
    start_server()
