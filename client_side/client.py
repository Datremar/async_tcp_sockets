import socket
from sys import argv


HOST = "127.0.0.1"
PORT = 65432

if __name__ == "__main__":
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        expression = argv[1]
        s.connect((HOST, PORT))
        s.sendall(expression.encode(encoding="utf-8"))
        data = s.recv(1024)

    print("{}".format(data.decode(encoding="utf-8")))
