# -*- coding: utf-8 -*-

from deck import Deck
import socket
import _thread

HOST = ''              # Endereco IP do Servidor
PORT = 5000            # Porta que o Servidor esta

lista_jogadores = []
lista_nicks = []
lista_sala = {}


sala = {
    'nome' : "",
    'jogadores' : [],
    'baralho': ""
}

# Função para controlar a parte inicial do programa (criação de sala, etc)
def beforeGame(con, cliente):
    print ('Conectado por', cliente)
    getNick(con)
    while True:
        command = con.recv(1024)
        command = command.decode()
        command = command.upper()
        if command == "SAIR":
            clientExit(con)
            break
        resolveRooms(con, cliente, command)


# Função para armazenar o nick do jogador
def getNick(con):
    con.send("Digite seu nick: ".encode())
    nick = con.recv(1024)
    lista_jogadores.append(dict(nick=nick, socket=con, fichas=100))
    con.send(
        "Ok, agora digite um comando para iniciar o jogo. Caso deseje ajuda, digite o comando HELP".encode())

# Função para executar uma ação com base no comando digitado pelo usuário


def checkRoom(con):
    for p in lista_jogadores:
        if p['socket'] == con:
            return 1
    con.send(
        "Você não está em nenhuma sala! Utilize o comando JOIN_ROOM [nome] para adentrar ou criar uma sala!".encode())
    return -1


def clientExit(con):
    print('Finalizando conexao do cliente', cliente)
    for c in lista_jogadores:
        if c['socket'] == con:
            lista_jogadores.remove(c)
    con.send("Obrigado por jogar!".encode())
    con.close()
    _thread.exit()

def resolveRooms(con, cliente, raw_cmd):
    command = raw_cmd.split(" ")
    if command[0] == "ROOMS":
        con.send(str(lista_sala.keys()))

    elif command[0] == "JOIN_ROOM":
        if len(command) == 1:
            con.send("O comando está incompleto, digite o nome da sala!".encode())
            return
        if command[1] in lista_sala:
            lista_sala[command[1]].append(con)
            con.send(("Sucesso ao entrar na sala " + command[1]).encode())
        else:
            con.send(
                "Não há uma sala com este nome, por isso foi criada uma nova sala!".encode())
            lista_sala[command[1]] = []
            lista_sala[command[1]].append(0)
            for p in lista_jogadores:
                if p['socket'] == con:
                    lista_sala[command[1]].append(p['socket'])

    elif command[0] == "READY":
        if len(command) == 1:
            con.send("O comando está incompleto, digite o nome da sala!".encode())
            return
        if command[1] not in lista_sala.keys():
            con.send(
                "Não há uma sala com esse nome. Escolha outra sala, ou crie uma nova!".encode())
            return
        if(checkRoom(con) == -1):
            return
        nome_sala = command[1]
        lista_sala[command[1]][0] = lista_sala[command[1]][0] + 1
        con.send("Aguardando outros jogadores".encode())
        if ((lista_sala[command[1]][0] == len(lista_sala[command[1]])-1)):
        # if ((lista_sala[command[1]][0] == len(lista_sala[command[1]])-1) and lista_sala[command[1]][0] > 1):

            configGame(nome_sala)

    else:
        con.send("Comando inválido, digite novamente".encode())
    return

def configGame(nome_sala):

    d = Deck()
    sala['nome'] = nome_sala
    i = 1
    for player in lista_jogadores:
        if i == len(lista_sala[nome_sala]):
            break
        if player['socket'] == lista_sala[nome_sala][i]:
            jogador = {
                'socket': player['socket'],
                'fichas': player['fichas'],
                'cartas': []
            }
            sala['jogadores'].append(jogador)
        i = i + 1
    
    sala['baralho'] = d
    sala['baralho'].shuffle()
    game(sala)

def game(sala):
    pass


tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

orig = (HOST, PORT)

tcp.bind(orig)
tcp.listen(1)

while True:
    con, cliente = tcp.accept()
    _thread.start_new_thread(beforeGame, tuple([con, cliente]))

tcp.close()
