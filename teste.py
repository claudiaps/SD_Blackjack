import socket
HOST = '127.0.0.1'     # Endereco IP do Servidor
PORT = 5000            # Porta que o Servidor esta
tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
dest = (HOST, PORT)
tcp.connect(dest)

while True:
    qtd_msg = tcp.recv(1024)
    qtd_msg = qtd_msg.decode()
    if(qtd_msg == "RECV"):
        msg = input()
        tcp.send(msg.encode())
    else:
        print(qtd_msg)
