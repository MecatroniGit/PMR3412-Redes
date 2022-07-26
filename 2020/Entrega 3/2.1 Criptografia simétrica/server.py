from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, hmac
import socket

HOST = ''                 # Symbolic name meaning all available interfaces
PORT = 50007              # Arbitrary non-privileged port

aes_key = bytes.fromhex('f91f9fb307b198f22370f6d158d1f1c65d83cfecee1ab1f0ab8879e54494af50')
nonce = bytes.fromhex('f24e6038126c7c8cddc59a871797c806')
hmac_key = bytes.fromhex('e5081bdce6bd796cd1be4f6cb5488d5c')

h = hmac.HMAC(hmac_key, hashes.SHA256(), backend=default_backend())
h.update(b'Hello world')
h.finalize.hex()

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen(1)
    conn, addr = s.accept()
    with conn:
        print('Connected by', addr)
        while True:
            data = conn.recv(1024)
            if not data: break
            conn.sendall(data)