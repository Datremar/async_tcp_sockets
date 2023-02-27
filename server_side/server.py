import socket


class _ServerHandler:
    _HOST = "127.0.0.1"
    _PORT = 65432

    @staticmethod
    def solve(expression):
        return str(eval(expression))

    def __init__(self):
        pass

    def run(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((self._HOST, self._PORT))
            while True:
                s.listen()
                conn, addr = s.accept()

                with conn:
                    print(f"Connected by {addr}")

                    data = conn.recv(1024)

                    result = _ServerHandler.solve(data.decode(encoding="utf-8"))
                    conn.sendall(result.encode(encoding="utf-8"))


class Server:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not Server._instance:
            Server._instance = _ServerHandler()

        return Server._instance


if __name__ == "__main__":
    Server().run()
