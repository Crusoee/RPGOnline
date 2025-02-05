import asyncio
import pickle
import zlib

async def send_message(writer: asyncio.StreamWriter, data, use_compression=True):
    # Serialize data
    serialized_data = pickle.dumps(data)
    
    # Optionally compress data
    if use_compression:
        serialized_data = zlib.compress(serialized_data)
    
    # Send total size of the data first
    total_size = len(serialized_data)
    writer.write(total_size.to_bytes(4, 'big'))
    await writer.drain()  # Ensure the size is sent
    
    # Send data in chunks
    chunk_size = 1024
    for i in range(0, total_size, chunk_size):
        chunk = serialized_data[i:i + chunk_size]
        writer.write(chunk)
        await writer.drain()  # Ensure the chunk is sent

async def get_message(reader: asyncio.StreamReader, use_compression=True):
    # Receive total size of the data (first 4 bytes)
    size_data = await reader.readexactly(4)  # Read exactly 4 bytes for size
    total_size = int.from_bytes(size_data, 'big')
    
    # Receive data in chunks
    received_data = b''
    while len(received_data) < total_size:
        chunk = await reader.read(min(1024, total_size - len(received_data)))
        if not chunk:
            raise ConnectionError("Connection closed while receiving data")
        received_data += chunk
    
    # Optionally decompress data
    if use_compression:
        received_data = zlib.decompress(received_data)
    
    # Deserialize data
    return pickle.loads(received_data)