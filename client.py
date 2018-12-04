import socket
HOST = '127.0.0.1'     # Endereco IP do Servidor
PORT = 5000            # Porta que o Servidor esta
tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
dest = (HOST, PORT)
tcp.connect(dest)


def PrintException():
    exc_type, exc_obj, tb = sys.exc_info()
    f = tb.tb_frame
    lineno = tb.tb_lineno
    filename = f.f_code.co_filename
    linecache.checkcache(filename)
    line = linecache.getline(filename, lineno, f.f_globals)
    print ('EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), exc_obj))


while True:
    try:
        recive = tcp.recv(1024)
        if (recive.decode() == 'SEND'):
            # print(recive.decode())
            snd = input()
            if(snd == 'SAIR'):
                tcp.close()
                break
            else:
                tcp.send(snd.encode())
        else:
            print(recive.decode())
    except:
        PrintException()
