import json
import struct
import socket
import threading
from queue import Queue, Empty
from . import config, log

HOST = config.get(("ipcqueue",), "host", "127.0.0.1")
PORT = config.get(("ipcqueue",), "port", 64696)
key  = config.get(("ipcqueue",), "key", "gallery_dl").encode("utf-8")
stop_event = threading.Event()
klen = len(key)

# Background thread in master process that accepts data from subsequent gallery-dl processes
def socket_listener(queueObj):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))
        s.listen()
        s.settimeout(1.0) # Check stop_event periodically
        while not stop_event.is_set():
            try:
                conn, _ = s.accept()
                with conn:
                    header = conn.recv(4+klen)
                    if not header[:klen] == key:
                        continue
                    data_len = struct.unpack('>I', header[klen:])[0]
                    chunks = []
                    bytes_received = 0
                    while bytes_received < data_len:
                        chunk = conn.recv(min(data_len - bytes_received, 4096))
                        if not chunk: break
                        chunks.append(chunk)
                        bytes_received += len(chunk)
                    full_payload = b''.join(chunks)
                    data = json.loads(full_payload.decode('utf-8'))
                    if data and isinstance(data, list):
                        log.info(f"Recieved links: {data}")
                        for i in data:
                            queueObj.put(i)
                    elif data:
                        log.info(f"Recieved link: {', '.join(data)}")
                        queueObj.put(data)
            except socket.timeout:
                continue


# send data to master process
def socket_sender(data):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(0.5)
            s.connect((HOST, PORT))

            payload = json.dumps(data).encode('utf-8')
            header = struct.pack('>I', len(payload))

            s.sendall(key + header + payload)
            return True
    except:
        return False

def start(queueObj):
    listener = threading.Thread(target=socket_listener, args=(queueObj,), daemon=True)
    listener.start()

def stop():
    stop_event.set()
