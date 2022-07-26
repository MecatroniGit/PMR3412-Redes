import asyncio
import json
import websockets

USERS = []
    
async def mensagem_publica(mensagem, user):
    message = json.dumps({
        "tipo": "mensagem",
        "privacidade": "publica",
        "conteudo": mensagem,
        "username": user
    })
    await (asyncio.wait([user["websocket"].send(message) for user in USERS]))

async def mensagem_privada(websocket, mensagem, user):
    message = json.dumps({
        "tipo": "mensagem",
        "privacidade": "privada",
        "conteudo": mensagem,
        "username": user
    })
    await (asyncio.wait([websocket.send(message)]))

async def aviso_privado(websocket, aviso):
    message = json.dumps({
        "tipo": "aviso",
        "conteudo": aviso
    })
    await (asyncio.wait([websocket.send(message)]))

async def aviso_publico(aviso):
    message = json.dumps({
        "tipo": "aviso",
        "conteudo": aviso
    })
    await (asyncio.wait([user["websocket"].send(message) for user in USERS]))

async def register(websocket):
    USERS.append({"websocket": websocket, "username": None})
    boas_vindas = "Bem vindo à sala de bate-papo. Você pode configurar seu nome com o comando /nome"
    await aviso_privado(websocket, boas_vindas)

async def unregister(websocket):
    USERS.remove([user for user in USERS if user["websocket"] == websocket][0])
    user = get_user(websocket)
    if (user):
        await (aviso_publico(user + " saiu do chat"))

# Confere se um nome já foi registrado
def confere_nome_unico(nome):
    if ([user for user in USERS if user["username"] == nome]):
        return False
    else:
        return True

# Manda uma mensagem de confirmação de nome
async def confirma_nome(websocket, nome):
    message = json.dumps({
        "tipo": "confirmacao",
        "nome": nome
    })
    await(asyncio.wait([websocket.send(message)]))

# Busca o nome do usuário a partir do websocket dele
def get_user(websocket):
    for user in USERS:
        if user["websocket"] == websocket:
            return user["username"]

async def servico_io(websocket, path):
    await register(websocket)
    try:
        async for message in websocket:
            data = json.loads(message)

            # Caso seja enviado um comando:
            if (data["mensagem"][0] == '/'):

                # Caso seja o comando de configuração de nome
                if (data["mensagem"].split(" ")[0].lower() == "/nome"):
                    nome = data["mensagem"][data["mensagem"].find(" ")+1:]

                    # Caso o nome seja nulo, ""
                    if (nome == ""):
                        await(aviso_privado(websocket, "Envie um nome válido"))
                    # Caso o nome não tenha sido tomado
                    elif (confere_nome_unico(nome)):
                        for user in USERS:
                            if (user["websocket"] == websocket):
                                user["username"] = nome
                        await(aviso_publico(nome + " entrou no chat"))
                        await(confirma_nome(websocket, nome))
                    # Caso o nome já tenha sido tomado
                    else:
                        await(aviso_privado(websocket, "Nome \"" + nome + "\" já tomado"))
                
                # Caso seja o comando de mensagem privada
                elif (data["mensagem"].split(" ")[0].lower() == "/pvd"):
                    destinatario = data["mensagem"].split(" ")[1]
                    mensagem = " ".join(data["mensagem"].split(" ")[2:])
                    for user in USERS:
                        if user["username"] == destinatario:
                            ws_destinatario = user["websocket"]
                    print("mensagem privada de "+get_user(websocket)+" para " + destinatario + ": " + mensagem)
                    await(mensagem_privada(ws_destinatario, mensagem, get_user(websocket)))
                    await(mensagem_privada(websocket, mensagem, get_user(websocket)))

                # Caso o comando não seja um dos previamente configurados
                else:
                    await (aviso_privado(websocket, "Comando não compreendido"))

            # Caso seja enviada uma mensagem pública de chat:
            else:
                if (get_user(websocket) == None):
                    await (aviso_privado(websocket, "Você deve escolher um nome com /nome antes de mandar mensagens"))
                else:
                    await (mensagem_publica(data["mensagem"], get_user(websocket)))
            
    finally:
        await unregister(websocket)


start_server = websockets.serve(servico_io, "localhost", 8765)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()