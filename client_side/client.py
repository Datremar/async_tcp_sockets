import asyncio
import logging

from json import dumps
from socket import socket, AF_INET, SOCK_STREAM

from utils import Request, Response


class Client:
    _HOST = "127.0.0.1"
    _PORT = 65432
    _semaphore_value = 500

    def __init__(self):
        self._semaphore = asyncio.Semaphore(value=Client._semaphore_value)

        logging.basicConfig(
            filename='./logs.log',
            format="[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s",
            level=logging.DEBUG
        )
        logging.info("Initializing client")
        logging.debug("Client params:\n- host {}\n- port {}\n- semaphore value {}\n".format(
            Client._HOST,
            Client._PORT,
            Client._semaphore_value
        ))

    async def request(self, expression: str):
        logging.info("Making request {} to: {}:{}".format(expression, Client._HOST, Client._PORT))
        async with self._semaphore:
            reader, writer = await asyncio.open_connection(Client._HOST, Client._PORT)

            request = Request({
                "expression": expression
            })

            writer.write(request)
            await writer.drain()

            response = Response(await reader.read(10000))
            logging.info("Got response: {} from {}:{}".format(dumps(response), Client._HOST, Client._PORT))

            logging.info("Closing connection with {}:{}".format(Client._HOST, Client._PORT))
            writer.close()
            await writer.wait_closed()

            return response

    def run(self):
        logging.info("Starting ")
        print("Enter the expression to calculate on the server.\nIf you wish to exit the client, enter 'exit' as an "
              "input.")
        while True:
            expression = input()
            if expression == "exit":
                break

            try:
                response = asyncio.run(self.request(expression))
            except Exception as e:
                print("EXCEPTION OCCURED:", str(e))
                logging.error("EXCEPTION OCCURED:\n{}".format(str(e)))

                continue

            print("Response:", response)


if __name__ == "__main__":
    Client().run()
