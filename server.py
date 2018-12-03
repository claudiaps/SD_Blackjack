# -*- coding: utf-8 -*-

import linecache
import sys
from deck import Deck
import time
import socket
import _thread

HOST = ''              # Endereco IP do Servidor
PORT = 4000            # Porta que o Servidor esta

lista_jogadores = []
lista_nicks = []
lista_sala = {}
control_room = 0

sala = {
    'nome': "",
    'jogadores': [],
    'baralho': ""
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


# Função para armazenar o nick do jogador
def getNick(con):
    try:
        con.send("Digite seu nick: ".encode())
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
                    print('sjdajksn')
                    start_game(nome_sala)
                    return

        else:
            con.send("Comando inválido, digite novamente".encode())
            return
    except Exception as ex:
        PrintException()


def start_game(nome_sala):
    configGame(nome_sala)
    while True:
        for player in sala['jogadores']:
            print(player['nick'])
            if(player['socket'] == 'dealer'):
                pass
            else: 
                for p in sala['jogadores']:
                    if(p['socket'] != 'dealer'):
                        p['socket'].send(('Vez do jogador: ' + player['nick']).encode())
                player['socket'].send('SEND'.encode())
                command = player['socket'].recv(1024)
                if(command.decode() == 'MORE'):
                    print('teste')
                elif(command.decode() == 'DONE'):
                    pass
                elif(command.decode() == 'SAIR'):
                    pass
                
                    

def addDealer(nome_sala):
    for player in sala['jogadores']:
        if player['socket'] == 'dealer':
            return

    dealer = {
    'nick': 'dealer',
    'socket': 'dealer',
    'fichas': 100,
    'cartas': []}
    sala['jogadores'].append(dealer)


def configGame(nome_sala):
    d = Deck()
    sala['nome'] = nome_sala
    i = 1
    for player in lista_jogadores:
        print(lista_jogadores)
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
                'cartas': []
            }
            sala['jogadores'].append(jogador)
        i = i + 1

    addDealer(nome_sala)

    sala['baralho'] = d
    sala['baralho'].shuffle()

    for player in sala['jogadores']:
        player['cartas'].append(sala['baralho'].deal())
        player['cartas'].append(sala['baralho'].deal())
        if(player['socket'] != 'dealer'):
            print('aquiiiii')
            player['socket'].send("Sua cartas são: ".encode())
            player['socket'].send(str(player['cartas'][0]).encode())
            player['socket'].send(str(player['cartas'][1]).encode())
            player['socket'].send("Sua quantidade de fichas é: ".encode())
            player['socket'].send(str(player['fichas']).encode())

    return

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
