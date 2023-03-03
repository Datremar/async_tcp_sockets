import asyncio

from json import JSONDecodeError

from utils import Request, Response


class _ServerHandler:
    _HOST = "127.0.0.1"
    _PORT = 65432
    semaphore = asyncio.Semaphore(value=500)

    def __init__(self):
        self.running = True

    @staticmethod
    def solve(expression):
        try:
            result = str(eval(expression))
        except SyntaxError:
            return Response(
                {
                    "response": "Syntax error.",
                    "status": 400
                }
            )

        return result

    @staticmethod
    async def send_response(server, response):
        server.write(response)
        await server.drain()

        server.close()
        await server.wait_closed()

    @staticmethod
    def troubleshoot_request(request):
        try:
            request = Request(request)
        except JSONDecodeError:
            return Response({
                "response": "Error. The request provided was not in JSON format.",
                "status": 400
            })

        if "expression" not in request:
            return Response({
                "response": "Error. The request sent does not contain the expression.",
                "status": 400
            })

        if type(request["expression"]) is not str:
            return Response({
                "response": "Error. The request type should be a string.",
                "status": 400
            })

        allowed_symbols = " 1234567890+-/*.()"
        for c in request["expression"]:
            if c not in allowed_symbols:
                return Response({
                    "response": "Unauthorized expression detected! Only simple expressions allowed. This will be "
                                "logged and the security team will be alerted.",
                    "status": 400
                })

        return None

    @staticmethod
    async def handle_client(client, server):
        async with _ServerHandler.semaphore:
            addr = server.get_extra_info('peername')
            print(addr)
            payload = await client.read(1024)

            troubles = _ServerHandler.troubleshoot_request(payload)

            if not troubles:
                request = Request(payload)
                result = _ServerHandler.solve(request["expression"])

                if type(result) is bytes:
                    await _ServerHandler.send_response(server, result)
                    return

                response = Response({
                    "response": result,
                    "status": 200
                })

                await _ServerHandler.send_response(server, response)
            else:
                await _ServerHandler.send_response(server, troubles)

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
