import os
import base64
import cryptography
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

from flask import Flask
from flask import request
from flask import make_response
import json

counter = 'E9RVpfQ2N0A6rIXX1Nw/7A=='

class EncryptionManager:
    def __init__(self):
        key = base64.b64decode(b'NbUQlSIhq/Tlq8GuN0LKkMHl0IPvMwOS4ajBWRbom38=')
        nonce = base64.b64decode(b'QwxHQWlXtn6Smq9ajeJlzQ==')
        aes_context = Cipher(algorithms.AES(key), modes.CTR(nonce), backend=default_backend())
        self.encryptor = aes_context.encryptor()
        self.decryptor = aes_context.decryptor()

    def updateEncryptor(self, plaintext):
        return self.encryptor.update(plaintext)

    def finalizeEncryptor(self):
        return self.encryptor.finalize()
    
    def updateDecryptor(self, ciphertext):
        return self.decryptor.update(ciphertext)
    
    def finalizeDecryptor(self):
        return self.decryptor.finalize()


# Definir o sal. Enquanto o servidor rodar, ele só irá usar este sal.
salt = os.urandom(16)
kdf = Scrypt(salt=salt, length=32, n=2**14, r=8, p=1, backend=default_backend())

app = Flask(__name__)

# Inicializando a lista de usuários
users = [
    {
        "user_id": 1,
        "user_name": "Gustavo Rubo",
        "user_password_digest": base64.b64encode(kdf.derive(b"4584080")),
        "user_email": "gustavo.rubo@usp.br"
    }
]

id_counter = 2

# Rota para coleção de usuários
@app.route("/users", methods=["POST", "GET", "PUT", "DELETE"])
def process_users():
    global id_counter, users
    if request.method == "POST":
        # Criar um usuário e adicioná-lo à lista

        kdf = Scrypt(salt=salt, length=32, n=2**14, r=8, p=1, backend=default_backend())
        user = {
            "user_id": id_counter,
            "user_name": request.json["user_name"],
            "user_password_digest": base64.b64encode(kdf.derive(str.encode(request.json["user_password"]))),
            "user_email": request.json["user_email"]
        }
        id_counter += 1
        users.append(user)

        print("New digest password:", user["user_password_digest"])

        return user, 201

    elif request.method == "GET":
        # Retornar todos os usuários
        return {"users": users}, 200

    elif request.method == "PUT":
        return "Method not allowed", 405
    elif request.method == "DELETE":
        return "Method not allowed", 405

# Rota específica para usuários
@app.route("/users/<user_id>", methods=["POST", "GET", "PUT", "DELETE"])
def process_users_id(user_id):
    global id_counter, users
    if request.method == "POST":
        return "Method not allowed", 405

    elif request.method == "GET":
        # Retornar o usuário com o id especificado

        user = next((u for u in users if u["user_id"] == int(user_id)), None)
    
        if user:
            return user, 200
        else:
            return "User not found", 404

    elif request.method == "PUT":
        # Modificar o usuário com o id especificado

        user = next((u for u in users if u["user_id"] == int(user_id)), None)

        if user:
            user["user_name"] = request.json["user_name"]
            user["user_password_digest"] = base64.b64encode(kdf.derive(request.json["user_password"]))
            user["user_email"] = request.json["user_email"]

            print("New digest password:", user["user_password_digest"])

            return user, 200
        else:
            return "User not found", 404

    elif request.method == "DELETE":
        # Remover o usuário com o id especificado

        user = next((u for u in users if u["user_id"] == int(user_id)), None)

        if user:
            users[:] = [u for u in users if u["user_id"] != int(user_id)]
            return "User deleted succesfully", 200
        else:
            return "User not found", 404

# Rota para login de usuário
@app.route("/login", methods=["POST", "GET"])
def process_login():
    global users
    if request.method == "POST":

        user_name = request.json["user_name"]
        user_password = request.json["user_password"]
        user = next((u for u in users if u["user_name"] == user_name), None)
        kdf = Scrypt(salt=salt, length=32, n=2**14, r=8, p=1, backend=default_backend())
        enc_manager = EncryptionManager()

        try:
            # Caso o nome de usuário e senha existam no banco de dados
            kdf.verify(str.encode(user_password), base64.b64decode(user["user_password_digest"]))

            plaintext = counter+str(user["user_id"])
            ciphertext = enc_manager.updateEncryptor(bytes(str.encode(plaintext)))
            enc_manager.finalizeEncryptor()

            print("Cookie encriptado:", base64.b64encode(ciphertext))

            resp = make_response(f'Signing in as {request.json["user_name"]}')
            resp.set_cookie("user_cookie", base64.b64encode(ciphertext))
            return resp

        except cryptography.exceptions.InvalidKey:
            # Caso de senha inválida
            return json.dumps({"message": "Invalid password", "login": "false"}), 200
        except:
            # Outros casos (ex: usuário inexistente)
            return json.dumps({"message": "Invalid user/password", "login": "false"}), 200

    elif request.method == "GET":
        user_name =request.cookies.get("user_name")

        if (user_name):
            return f'Logged in as {user_name}'
        else:
            return f'Not logged in yet'

# Rota para página de boas vindas. Usuário deve estar logado para acessar.
@app.route("/welcome", methods=["GET"])
def process_welcome():
    
    if request.method == "GET":
        if(request.cookies.get("user_cookie")):

            enc_manager = EncryptionManager()
            ciphertext = base64.b64decode(request.cookies.get("user_cookie"))
            plaintext = str(enc_manager.updateDecryptor(ciphertext))
            enc_manager.finalizeDecryptor()

            print("Cookie encriptado:", base64.b64encode(ciphertext))

            user_id = int(plaintext[26:][:-1])
            user = next((u for u in users if u["user_id"] == user_id), None)

            return f'Welcome {user["user_name"]}'
        else:
            return f'You need to log in to access this page.'

# Rota para logout. Apaga os cookies de usuário.
@app.route("/logout", methods=["DELETE"])
def process_logout():

    if request.method == "DELETE":
        resp = make_response("Cookie removed")
        resp.set_cookie("user_cookie", "", max_age=0)
        return resp