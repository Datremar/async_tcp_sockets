import asyncio
import logging

from json import JSONDecodeError, dumps, loads

from .utils import Request, Response


class _ServerHandler:
    _HOST = "127.0.0.1"
    _PORT = 65432
    _semaphore_value = 500
    _semaphore = asyncio.Semaphore(value=_semaphore_value)

    def __init__(self):
        self.running = True

        logging.basicConfig(
            filename='server_side/logs.log',
            format="[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s",
            level=logging.DEBUG
        )

        logging.info("Initializing server")
        logging.debug("Server params:\n- host {}\n- port {}\n- semaphore value {}\n".format(
            _ServerHandler._HOST,
            _ServerHandler._PORT,
            _ServerHandler._semaphore_value
        ))

    @staticmethod
    def solve(expression):
        try:
            result = str(eval(expression))
        except SyntaxError:
            logging.debug("STATUS 400 SYNTAX ERROR on expression: {}".format(expression))
            return Response(
                {
                    "response": "Syntax error.",
                    "status": 400
                }
            )
        except ZeroDivisionError:
            logging.debug("STATUS 400 DIVISION BY ZERO on expression: {}".format(expression))
            return Response(
                {
                    "response": "Division by zero error.",
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
            response = Response({
                "response": "Error. The request provided was not in JSON format.",
                "status": 400
            })

            logging.debug("STATUS 400 NOT JSON FORMAT on request: {}".format(request.decode(encoding="utf-8")))

            return response

        if "expression" not in request:
            logging.debug("STATUS 400 KEYWORD EXPRESSION NOT PROVIDED on request: {}".format(dumps(request)))

            return Response({
                "response": "Error. The request sent does not contain the expression.",
                "status": 400
            })

        if type(request["expression"]) is not str:
            logging.debug("STATUS 400 EXPRESSION NOT A STRING on request: {}".format(dumps(request)))
            return Response({
                "response": "Error. The request type should be a string.",
                "status": 400
            })

        allowed_symbols = " 1234567890+-/*.()"
        for c in request["expression"]:
            if c not in allowed_symbols:
                logging.debug("STATUS 400 ILLEGAL STRING on request: {}".format(dumps(request)))
                return Response({
                    "response": "Illegal expression detected! Only simple expressions allowed. This will be "
                                "logged and the security team will be alerted.",
                    "status": 400
                })

        return None

    @staticmethod
    async def handle_client(client, server):
        try:
            async with _ServerHandler._semaphore:
                addr = server.get_extra_info('peername')
                logging.info("new connection from: {}:{}".format(addr[0], addr[1]))

                payload = await client.read(1024)

                troubles = _ServerHandler.troubleshoot_request(payload)

                if not troubles:
                    request = Request(payload)
                    logging.debug("accepting request: {}".format(dumps(request)))

                    result = _ServerHandler.solve(request["expression"])

                    if type(result) is bytes:
                        await _ServerHandler.send_response(server, result)
                        return

                    response = Response(
                        {
                            "response": result,
                            "status": 200
                        }
                    )

                    logging.debug(
                        "request {} yields the result: {}".format(
                            dumps(request),
                            dumps(loads(response.decode(encoding="utf-8"))))
                    )

                    await _ServerHandler.send_response(server, response)
                else:
                    await _ServerHandler.send_response(server, troubles)
        except Exception as e:
            logging.error("500 INTERNAL SERVER ERROR\n" + str(e))
            await _ServerHandler.send_response(server, Response(
                {
                    "response": "INTERNAL SERVER ERROR.",
                    "status": 500
                }
            ))

        logging.info("Closing client {}:{}".format(addr[0], addr[1]))

    async def run(self):
        server = await asyncio.start_server(
            _ServerHandler.handle_client,
            _ServerHandler._HOST,
            _ServerHandler._PORT
        )

        logging.info("Starting server on {}:{}".format(_ServerHandler._HOST, _ServerHandler._PORT))

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
