import zlib
import pickle
import socket

host = '192.168.56.1'
# host = '10.0.0.128'
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

def client_communication_loop(shared_memory):
    s = socket.socket()
    s.connect((host, port))
    print("Connected to the server")

    shared_memory['user'] = get_message(s)

    while shared_memory['running']:
        # send_message(s, [int(shared_memory['player'][0]), int(shared_memory['player'][1]), int(shared_memory['player'][2]), int(shared_memory['player'][3]), int(shared_memory['player'][4]), int(shared_memory['player'][5])],False)
        send_message(s, [shared_memory['player']],False)

        # shared_memory['stats'] = get_message(s,False)

        shared_memory['players'] = get_message(s,False)
