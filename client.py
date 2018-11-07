import socket
HOST = '127.0.0.1'     # Endereco IP do Servidor
PORT = 5000            # Porta que o Servidor esta
tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
dest = (HOST, PORT)
tcp.connect(dest)
print('Para sair digite SAIR\n')

while True:
    msg2 = tcp.recv(1024)
    print(msg2.decode())
    msg = input()
    tcp.send (msg.encode())
    msg.upper()
    if msg == "SAIR":
        tcp.close()
        break
    