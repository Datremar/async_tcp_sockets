import socket

from sys import argv

from utils import Request, Response


class Client:
    _HOST = "127.0.0.1"
    _PORT = 65432

    def request(self, expression: str):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            request = Request({
                "expression": expression
            })

            s.connect((self._HOST, self._PORT))
            s.sendall(request)

            return Response(s.recv(1024))


if __name__ == "__main__":
    print(Client().request(argv[1]))
