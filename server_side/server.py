import asyncio

from .utils import Request, Response


class _ServerHandler:
    _HOST = "127.0.0.1"
    _PORT = 65432
    semaphore = asyncio.Semaphore(value=250)

    def __init__(self):
        self.running = True

    @staticmethod
    def solve(expression):
        return str(eval(expression))

    @staticmethod
    async def handle_client(client, server):
        async with _ServerHandler.semaphore:
            request = Request(await client.read(1024))
            addr = server.get_extra_info('peername')

            print(f"Received {request!r} from {addr!r}")

            response = Response({
                "response": _ServerHandler.solve(request["expression"]),
                "status": 200
            })

            print(f"Send: {response!r}")
            server.write(response)
            await server.drain()

            print("Close the connection")
            server.close()
            await server.wait_closed()

    async def run(self):
        server = await asyncio.start_server(
            _ServerHandler.handle_client,
            _ServerHandler._HOST,
            _ServerHandler._PORT
        )

        addrs = ', '.join(str(sock.getsockname()) for sock in server.sockets)
        print(f'Serving on {addrs}')

        async with server:
            await server.serve_forever()

    def terminate(self):
        self.running = False


class Server:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not Server._instance:
            Server._instance = _ServerHandler()

        return Server._instance
