# -*- coding: utf-8 -*-

import linecache
import sys
from deck import Deck
import time
import socket
import _thread

HOST = ''              # Endereco IP do Servidor
PORT = 5000            # Porta que o Servidor esta

lista_jogadores = []
lista_nicks = []
lista_sala = {}
control_room = 0

sala = {
    'nome': "",
    'jogadores': [],
    'baralho': "",
    'apostas': 0
}

# Função para controlar a parte inicial do programa (criação de sala, etc)


def PrintException():
    exc_type, exc_obj, tb = sys.exc_info()
    f = tb.tb_frame
    lineno = tb.tb_lineno
    filename = f.f_code.co_filename
    linecache.checkcache(filename)
    line = linecache.getline(filename, lineno, f.f_globals)
    print ('EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), exc_obj))


def beforeGame(con, cliente):
    print ('Conectado por', cliente)
    getNick(con)
    while True:
        try:
            time.sleep(1)
            con.send('SEND'.encode())
            command = con.recv(1024)
            command = command.decode()
            command = command.upper()
            if command == "SAIR":
                clientExit(con)
                break
            resolveRooms(con, cliente, command)
            if(control_room == -1):
                break
        except Exception as ex:
            PrintException()


# Função para armazenar o nick do jogador
def getNick(con):
    try:
        con.send("Digite seu nick: ".encode())
        time.sleep(1)
        con.send('SEND'.encode())
        nick = con.recv(1024)
        nick = nick.decode()
        lista_jogadores.append(dict(nick=nick, socket=con, fichas=100))
        con.send(
            "Ok, agora digite um comando para iniciar o jogo. Caso deseje ajuda, digite o comando HELP".encode())
    except Exception as ex:
        PrintException()
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
    except Exception as ex:
        PrintException()
        clientExit(con)


def clientExit(con):
    try:
        print('Finalizando conexao do cliente', cliente)
        for c in lista_jogadores:
            if c['socket'] == con:
                lista_jogadores.remove(c)
        con.close()
        _thread.exit()
    except Exception as ex:
        PrintException()


def resolveRooms(con, cliente, raw_cmd):
    try:
        command = raw_cmd.split(" ")
        if command[0] == "ROOMS":

            con.send(str(lista_sala.keys()).encode())
        elif command[0] == "JOIN_ROOM":

            if len(command) == 1:
                con.send(
                    "O comando está incompleto, digite o nome da sala!".encode())
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

                con.send(
                    "O comando está incompleto, digite o nome da sala!".encode())
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
                global control_room
                control_room = -1
                if ((lista_sala[command[1]][0] == len(lista_sala[command[1]])-1)):
                # if ((lista_sala[command[1]][0] == len(lista_sala[command[1]])-1) and lista_sala[command[1]][0] > 1):
                    start_game(nome_sala)
                    return

        else:
            con.send("Comando inválido, digite novamente".encode())
            return
    except Exception as ex:
        PrintException()

def start_game(nome_sala):
    configGame(nome_sala)
    try:
        while True:
            for player in sala['jogadores']:
                inicialCoins(player)
                sendCards()
                player['jogada'] = sumCards(player)
                checkWinner(player)
                print(player['nick'], player['fichas'])
                if(player['socket'] == 'dealer'):
                    dealDealer(player)
                else: 
                    for p in sala['jogadores']:
                        if(p['socket'] != 'dealer'):
                            time.sleep(1)
                            p['socket'].send(('Vez do jogador: ' + player['nick']).encode())

                    time.sleep(1)
                    player['socket'].send('SEND'.encode())
                    command = player['socket'].recv(1024)

                    if(command.decode() == 'MORE'):
                        while(command.decode() != "DONE"):
                            player['cartas'].append(sala['baralho'].deal())
                            player['socket'].send(str(player['cartas'][len(player['cartas'])-1]).encode())
                            player['jogada'] = sumCards(player)
                            time.sleep(1)
                            player['socket'].send('SEND'.encode())
                            command = player['socket'].recv(1024)
                    elif(command.decode() == 'UP'):
                        pass
            newround()
    except Exception as ex:
        PrintException()

def inicialCoins(player):
    player['fichas'] = player['fichas'] - 5 
    sala['apostas'] = sala['apostas'] + 5 

def configGame(nome_sala):

    sala['nome'] = nome_sala
    i = 1
    for player in lista_jogadores:
        if i == len(lista_sala[nome_sala]):
            break
        if player['socket'] == lista_sala[nome_sala][i]:
            for j in sala['jogadores']:
                if player['socket'] == j['socket']:
                    break
            jogador = {
                'nick': player['nick'],
                'socket': player['socket'],
                'fichas': player['fichas'],
                'cartas': [],
                'jogada': 0
            }
            sala['jogadores'].append(jogador)
        i = i + 1

    addDealer(nome_sala)
    dealCards()
    return

def dealCards():
    d = Deck()
    sala['baralho'] = d
    del sala['baralho'][53]
    del sala['baralho'][52]
    sala['baralho'].shuffle()

    for player in sala['jogadores']:
        player['cartas'].append(sala['baralho'].deal())
        player['cartas'].append(sala['baralho'].deal())
        if(player['socket'] != 'dealer'):
            time.sleep(1)
            player['socket'].send("Sua cartas são: ".encode())
            time.sleep(1)
            player['socket'].send(str(player['cartas'][0]).encode())
            time.sleep(1)
            player['socket'].send(str(player['cartas'][1]).encode())
            time.sleep(1)
            player['socket'].send("Sua quantidade de fichas é: ".encode())
            time.sleep(1)
            player['socket'].send(str(player['fichas']).encode())

    return


def addDealer(nome_sala):
    for player in sala['jogadores']:
        if player['socket'] == 'dealer':
            return

    dealer = {
    'nick': 'dealer',
    'socket': 'dealer',
    'fichas': 100,
    'cartas': [],
    'jogada': 0
    }
    sala['jogadores'].append(dealer)


def sendCards():
    for player in sala['jogadores']:
        for p in sala['jogadores']:
            if(player['socket'] != 'dealer'):
                if(p['socket'] != player['socket']):
                    time.sleep(1)
                    player['socket'].send(('\nCartas do jogador: ' + p['nick']).encode())
                    for cartas in p['cartas']:
                        time.sleep(1)
                        player['socket'].send(str(cartas).encode())


def treatCards(carta):
    carta = str(carta)
    if (len(carta) == 3):
        c = (int(carta[0]) * 10) + int(carta[1])
    else:
        c = int(carta[0])
    return c


def sumCards(player):
    try:
        values = 0
        for carta in player['cartas']:
            values = values + (treatCards(carta))
        if(player['socket'] == 'dealer'):
            for p in sala['jogadores']:
                if(p['socket'] != 'dealer'):
                    p['socket'].send(("\nSomatória Dealer: " + str(values)).encode())
                    return values
        else:
            player['socket'].send(('\nSomatoria do jogador ' +player['nick'] + ": " + str(values)).encode())
            return values
    except:
        PrintException()


def dealDealer(player):
    for player in sala['jogadores']:
        if(player['socket'] != 'dealer'):
            time.sleep(1)
            player['socket'].send('\nVez do Dealer'.encode())
    value = sumCards(player)
    if((21 - value) >= 6):
        player['cartas'].append(sala['baralho'].deal())
        value = sumCards(player)
        player['jogada'] = value
        return
    else: 
        return


def newround():
    winner = ""
    value = 21
    for player in sala['jogadores']:
        if(21 - player['jogada'] < 0):
            pass
        else:
            if(21 - player['jogada'] < value ):
                value = 21 - player['jogada']
                winner = player
    for player in sala['jogadores']:
        player['cartas'] = []
        if(player['socket'] != 'dealer'):
            player['socket'].send(("\nVencedor da rodada: " + winner['nick']).encode())
        if(player['socket'] == winner['socket']):
            print(sala['apostas'])
            player['fichas'] = player['fichas'] + sala['apostas']
    sala['apostas'] = 0
    dealCards()


def checkWinner(player):
    if(player['jogada'] == 21):
        time.sleep(1)
        player['socket'].send("BLACKJACK!".encode())
    elif(player['jogada'] > 21):
        time.sleep(1)
        player['socket'].send("ESTOUROU!!".encode())

def dealCoins():
    pass

tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

orig = (HOST, PORT)

tcp.bind(orig)
tcp.listen(1)

while True:
    con, cliente = tcp.accept()
    _thread.start_new_thread(beforeGame, tuple([con, cliente]))

tcp.close()


#TODO: implementar vencedor da partida
#TODO: implementar vencedor da rodada
#TODO: aumentar aposta

