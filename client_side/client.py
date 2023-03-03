import asyncio

from socket import socket, AF_INET, SOCK_STREAM
from sys import argv

from utils import Request, Response


class Client:
    _HOST = "127.0.0.1"
    _PORT = 65432
    semaphore = asyncio.Semaphore(value=500)

    async def request(self, expression: str):
        async with Client.semaphore:
            loop = asyncio.get_event_loop()

            s = socket(AF_INET, SOCK_STREAM)
            s.setblocking(False)

            request = Request({
                "expression": expression
            })

            await loop.sock_connect(s, (self._HOST, self._PORT))
            await loop.sock_sendall(s, request)

            return Response(await loop.sock_recv(s, 100000))


if __name__ == "__main__":
    print(asyncio.run(Client().request(argv[1])))
