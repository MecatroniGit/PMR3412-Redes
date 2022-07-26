from flask import Flask
from flask import request
import json

app = Flask(__name__)

# Inicializando a lista de usuários
users = [
    {
        "user_id": 1,
        "user_name": "Gustavo Rubo",
        "user_password": "4584080",
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
        user = {
            "user_id": id_counter,
            "user_name": request.json["user_name"],
            "user_password": request.json["user_password"],
            "user_email": request.json["user_email"]
        }
        id_counter += 1
        users.append(user)

        return json.dumps(user), 201

    elif request.method == "GET":
        # Retornar todos os usuários
        return json.dumps(users), 200

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
            return json.dumps(user), 200
        else:
            return "User not found", 404

    elif request.method == "PUT":
        # Modificar o usuário com o id especificado

        user = next((u for u in users if u["user_id"] == int(user_id)), None)

        if user:
            user["user_name"] = request.json["user_name"]
            user["user_password"] = request.json["user_password"]
            user["user_email"] = request.json["user_email"]
            return json.dumps(user), 200
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
@app.route("/login", methods=["POST"])
def process_login():
    global users
    if request.method == "POST":
        user_name = request.json["user_name"]
        user_password = request.json["user_password"]
        user = next((u for u in users if u["user_name"] == user_name), None)

        if user["user_password"] == user_password:
            return json.dumps({"login": "true"}), 200
        else:
            return json.dumps({"login": "false"}), 200