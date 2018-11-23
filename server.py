# -*- coding: utf-8 -*-

from deck import Deck
import time
import socket
import _thread

HOST = ''              # Endereco IP do Servidor
PORT = 5000            # Porta que o Servidor esta

lista_jogadores = []
lista_nicks = []
lista_sala = {}


sala = {
    'nome': "",
    'jogadores': [],
    'baralho': ""
}

# Função para controlar a parte inicial do programa (criação de sala, etc)


def beforeGame(con, cliente):
    print ('Conectado por', cliente)
    getNick(con)
    while True:
        con.send('SEND'.encode())
        command = con.recv(1024)
        command = command.decode()
        command = command.upper()
        if command == "SAIR":
            clientExit(con)
            break
        resolveRooms(con, cliente, command)


# Função para armazenar o nick do jogador
def getNick(con):
    try:
        con.send("Digite seu nick: ".encode())
        con.send('SEND'.encode())
        nick = con.recv(1024)
        lista_jogadores.append(dict(nick=nick, socket=con, fichas=100))
        con.send(
            "Ok, agora digite um comando para iniciar o jogo. Caso deseje ajuda, digite o comando HELP".encode())
    except:
        print('azedou')
    return

# Função para executar uma ação com base no comando digitado pelo usuário


def checkRoom(con):
    for p in lista_jogadores:
        if p['socket'] == con:
            return 1
    try:
       
        con.send(
            "Você não está em nenhuma sala! Utilize o comando JOIN_ROOM [nome] para adentrar ou criar uma sala!".encode())
        return -1
    except:
        clientExit(con)


def clientExit(con):
    try:
        print('Finalizando conexao do cliente', cliente)
        for c in lista_jogadores:
            if c['socket'] == con:
                lista_jogadores.remove(c)
       
        con.send("Obrigado por jogar!".encode())
        con.close()
        _thread.exit()
    except:
        print('azedou')


def resolveRooms(con, cliente, raw_cmd):
    try:
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
            else:
                nome_sala = command[1]
                lista_sala[command[1]][0] = lista_sala[command[1]][0] + 1
                con.send("Aguardando outros jogadores".encode())
                con.send("\nAjustando contagem de cartas...".encode())
                while True:
                    if ((lista_sala[command[1]][0] == len(lista_sala[command[1]])-1)):
                    # if ((lista_sala[command[1]][0] == len(lista_sala[command[1]])-1) and lista_sala[command[1]][0] > 1):
                        configGame(nome_sala)
                        break

        else:
           
            con.send("Comando inválido, digite novamente".encode())
            return
    except:
        print('azedou')

def addDealer(nome_sala):
    for player in sala['jogadores']:
        if player['socket'] == 'dealer':
            return
            
    dealer = {
    'socket': 'dealer',
    'fichas': 100, 
    'cartas': []}
    sala['jogadores'].append(dealer)

def configGame(nome_sala):

    #TODO tratar remoção da variável lista_sala

    d = Deck()
    sala['nome'] = nome_sala
    i = 1
    for player in lista_jogadores:
        if i == len(lista_sala[nome_sala]):
            break
        if player['socket'] == lista_sala[nome_sala][i]:
            for i in sala['jogadores']:
                if player['socket'] == i['socket']:
                    break
            jogador = {
                'socket': player['socket'],
                'fichas': player['fichas'],
                'cartas': []
            }
            sala['jogadores'].append(jogador)
        i = i + 1

    addDealer(nome_sala)    

    print(sala['jogadores'])
    print('aquiiiii')
    sala['baralho'] = d
    sala['baralho'].shuffle()

    for player in sala['jogadores']:
        print('player',player)
        player['socket'].send("OLAAAAAAAAA".encode())
    game(sala)


def game(sala):
    for player in sala['jogadores']:
        player['cartas'].append(sala['baralho'].deal())
        player['cartas'].append(sala['baralho'].deal())
        print(player)
        print(player['cartas'])
        for i in player['cartas']:
            player['socket'].send(str(player['cartas'][i]).encode())


def treatCards(carta):
    carta = str(carta)
    if (len(carta) == 3):
        c = (int(carta[0]) * 10) + int(carta[1])
    else:
        c = int(carta[0])
    return c


def checkBlackjack(cartas):
    pass


tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

orig = (HOST, PORT)

tcp.bind(orig)
tcp.listen(1)

while True:
    con, cliente = tcp.accept()
    _thread.start_new_thread(beforeGame, tuple([con, cliente]))

tcp.close()
