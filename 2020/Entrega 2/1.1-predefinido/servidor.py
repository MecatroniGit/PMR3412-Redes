import selectors
import socket

HOST = "0.0.0.0"
PORT = 8082

sel = selectors.DefaultSelector()

def accept(sock, mask):
    conn, addr = sock.accept()
    print("Conectado com:", addr)
    conn.setblocking(False)

    # Registrando a função de leitura, que vai receber dados enviados pelo cliente
    sel.register(conn, selectors.EVENT_READ, read)

    # Mandamos o comando logo após estabelecermos a conexão com o cliente
    comando = b"ls"
    conn.send(comando)

def read(conn, mask):
    data = conn.recv(1000)
    if data:
        # Imprimimos os dados recebidos do cliente:
        print("Dados recebidos:", data)

sock = socket.socket()
sock.bind((HOST, PORT))
sock.listen(100)
sock.setblocking(False)
sel.register(sock, selectors.EVENT_READ, accept)

while True:
    events = sel.select()
    for key, mask in events:
        callback = key.data
        callback(key.fileobj, mask)