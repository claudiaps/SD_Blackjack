import socket
HOST = '127.0.0.1'     # Endereco IP do Servidor
PORT = 5000            # Porta que o Servidor esta
tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
dest = (HOST, PORT)
tcp.connect(dest)

while True:
    while True:
        recive = tcp.recv(1024)
        if (recive.decode() == 'SEND'):
            snd = input()
            if(snd == 'SAIR'):
                break
            else:
                tcp.send(snd.encode())
        else:
            print(recive.decode())
    tcp.close()
    break