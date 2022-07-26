import selectors
import socket
import threading

HOST = "0.0.0.0"
PORT = 8082

comando = "ls"

sel = selectors.DefaultSelector()

def le_comando_thread():
    print("Thread inciando")
    
    while(True):
        global comando
        comando = input()
        print("Comando mudado para:", comando)

def accept(sock, mask):
    conn, addr = sock.accept()
    print("Conectado com:", addr)
    conn.setblocking(False)

    # Registrando a função de leitura, que vai receber dados enviados pelo cliente
    sel.register(conn, selectors.EVENT_READ, read)

    # Mandamos o comando logo após estabelecermos a conexão com o cliente
    conn.send(comando.encode('utf-8'))

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

# Inicializando a thread:
x = threading.Thread(target=le_comando_thread)
x.start() 

while True:
    events = sel.select()
    for key, mask in events:
        callback = key.data
        callback(key.fileobj, mask)