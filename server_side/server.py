import socket

from server_side.utils import Request, Response


class _ServerHandler:
    _HOST = "127.0.0.1"
    _PORT = 65432

    @staticmethod
    def solve(expression):
        return str(eval(expression))

    def __init__(self):
        self.running = True

    def run(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((self._HOST, self._PORT))
            while self.running:
                s.listen()
                conn, addr = s.accept()

                with conn:
                    print(f"Connected by {addr}")

                    request = Request(conn.recv(1024))
                    result = _ServerHandler.solve(request["expression"])

                    conn.sendall(Response(
                        {
                            "response": result,
                            "status": 200
                        }
                    ))

    def terminate(self):
        self.running = False


class Server:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not Server._instance:
            Server._instance = _ServerHandler()

        return Server._instance
