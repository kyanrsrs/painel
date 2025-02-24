import requests
import sys
import time

# Configuração para cores no terminal (códigos ANSI)
LIGHT_PURPLE = "\033[95m"  # Roxo claro
PURPLE = "\033[35m"        # Roxo
DARK_PURPLE = "\033[34m"   # Roxo escuro
RESET = "\033[0m"          # Reseta para a cor padrão

# Banner com cores organizadas
banner = f"""
{LIGHT_PURPLE} ██ ▄█▀▓██   ██▓ ▄▄▄      ███▄    █     ██▓███   ▄▄▄       ██▓ ███▄    █▓█████  ██▓    
 ██▄█▒  ▒██  ██▒▒████▄    ██ ▀█   █    ▓██░  ██▒▒████▄    ▓██▒ ██ ▀█   █▓█   ▀ ▓██▒    
▓███▄░   ▒██ ██░▒██  ▀█▄ ▓██  ▀█ ██▒   ▓██░ ██▓▒▒██  ▀█▄  ▒██▒▓██  ▀█ ██▒███   ▒██░    
{PURPLE}▓██ █▄   ░ ▐██▓░░██▄▄▄▄██▓██▒  ▐▌██▒   ▒██▄█▓▒ ▒░██▄▄▄▄██ ░██░▓██▒  ▐▌██▒▓█  ▄ ▒██░    
▒██▒ █▄  ░ ██▒▓░ ▓█   ▓██▒██░   ▓██░   ▒██▒ ░  ░ ▓█   ▓██▒░██░▒██░   ▓██░▒████▒░██████▒
▒ ▒▒ ▓▒   ██▒▒▒  ▒▒   ▓▒█░ ▒░   ▒ ▒    ▒▓▒░ ░  ░ ▒▒   ▓▒█░░▓  ░ ▒░   ▒ ▒░░ ▒░ ░░ ▒░▓  ░
{DARK_PURPLE}░ ░▒ ▒░ ▓██ ░▒░   ▒   ▒▒ ░ ░░   ░ ▒░   ░▒ ░       ▒   ▒▒ ░ ▒ ░░ ░░   ░ ▒░░ ░  ░░ ░ ▒  ░
░ ░░ ░  ▒ ▒ ░░    ░   ▒     ░   ░ ░    ░░         ░   ▒    ▒ ░   ░   ░ ░   ░     ░ ░   
░  ░    ░ ░           ░  ░        ░                   ░  ░ ░           ░   ░  ░    ░  ░
        ░ ░                                                                            
{RESET}
"""

print(banner)

class Discord:
    def __init__(self):
        self.token = ""
        self.userId = ""

    def testToken(self):
        headers = {'authorization': self.token}
        response = requests.get('https://discord.com/api/v9/users/@me', headers=headers)
        if response.status_code == 200:
            self.userId = response.json()["id"]
            return True
        elif response.status_code == 401:
            return False
        else:
            print(f"[ERRO] Código inesperado: {response.status_code}")
            return False

    def getDMs(self):
        headers = {'authorization': self.token}
        response = requests.get('https://discord.com/api/v9/users/@me/channels', headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"[ERRO] Não foi possível obter DMs. Código: {response.status_code}")
            return []

    def deleteMessage(self, channelId, messageId):
        headers = {'authorization': self.token}
        response = requests.delete(f'https://discord.com/api/v9/channels/{channelId}/messages/{messageId}', headers=headers)
        return response.status_code == 204

    def getMessages(self, channelId):
        headers = {'authorization': self.token}
        params = {'limit': 100}
        response = requests.get(f'https://discord.com/api/v9/channels/{channelId}/messages', headers=headers, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"[ERRO] Não foi possível obter mensagens. Código: {response.status_code}")
            return []

    def deleteAllMessages(self, channelId):
        while True:
            messages = self.getMessages(channelId)
            if not messages:
                print(f"[INFO] Todas as mensagens no canal {channelId} foram apagadas.")
                break
            for message in messages:
                if message["author"]["id"] == self.userId:
                    success = self.deleteMessage(channelId, message["id"])
                    if success:
                        print(f"[INFO] Mensagem {message['id']} apagada com sucesso.")
                    else:
                        print(f"[ERRO] Falha ao apagar mensagem {message['id']}.")
                    time.sleep(0.5)  # Pausa de 500ms entre exclusões

    def closeDM(self, channelId):
        headers = {'authorization': self.token}
        response = requests.delete(f'https://discord.com/api/v9/channels/{channelId}', headers=headers)
        if response.status_code == 200:
            print(f"[INFO] Canal DM {channelId} fechado com sucesso!")
        else:
            print(f"[ERRO] Falha ao fechar DM {channelId}. Código: {response.status_code}")

    def removeAllFriends(self):
        headers = {'authorization': self.token}
        response = requests.get('https://discord.com/api/v9/users/@me/relationships', headers=headers)
        if response.status_code == 200:
            friends = [friend for friend in response.json() if friend["type"] == 1]
            for friend in friends:
                self.removeFriend(friend["id"])
            print("[INFO] Todas as amizades foram removidas.")
        else:
            print(f"[ERRO] Não foi possível obter amigos. Código: {response.status_code}")

    def removeFriend(self, friendId):
        headers = {'authorization': self.token}
        response = requests.delete(f'https://discord.com/api/v9/users/@me/relationships/{friendId}', headers=headers)
        if response.status_code == 204:
            print(f"[INFO] Amizade com {friendId} removida com sucesso.")
        else:
            print(f"[ERRO] Falha ao remover amizade com {friendId}. Código: {response.status_code}")

    def sendMessage(self, channelId, content):
        headers = {'authorization': self.token, 'content-type': 'application/json'}
        data = {'content': content}
        response = requests.post(f'https://discord.com/api/v9/channels/{channelId}/messages', headers=headers, json=data)
        return response.status_code == 200

    def massMessage(self, channelId, content, count):
        for i in range(count):
            success = self.sendMessage(channelId, content)
            if success:
                print(f"[INFO] Mensagem {i + 1} enviada com sucesso.")
            else:
                print(f"[ERRO] Falha ao enviar mensagem {i + 1}.")
            time.sleep(0.5)  # Pausa de 500ms entre envios

# Instancia a classe Discord
discord = Discord()
discord.token = input("[ENTRADA] Token do Discord: ")

if discord.testToken():
    print("[INFO] Token válido, pode começar bb!")
else:
    print("[ERRO] Token inválido. Kitando...")
    sys.exit(0)

# Menu principal
print("\n[OPÇÕES]")
print("[1] Apagar mensagens de uma DM específica")
print("[2] Fechar todas as DMs")
print("[3] Remover todas as amizades")
print("[4] Apagar mensagens de um canal em servidor")
print("[5] Enviar mensagens em massa")

acao = input("[ENTRADA] Escolha uma opção: ")

if acao == "1":
    channel_id = input("[ENTRADA] Insira o ID da DM: ")
    discord.deleteAllMessages(channel_id)
elif acao == "2":
    dms = discord.getDMs()
    for dm in dms:
        discord.closeDM(dm["id"])
elif acao == "3":
    discord.removeAllFriends()
elif acao == "4":
    channel_id = input("[ENTRADA] Insira o ID do canal em servidor: ")
    discord.deleteAllMessages(channel_id)
elif acao == "5":
    channel_id = input("[ENTRADA] Insira o ID do canal ou DM: ")
    message = input("[ENTRADA] Insira a mensagem a ser enviada: ")
    count = int(input("[ENTRADA] Quantas mensagens deseja enviar? "))
    discord.massMessage(channel_id, message, count)

else:
    print("[ERRO] Opção inválida.")


