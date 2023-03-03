import asyncio

from server_side.server import Server

if __name__ == '__main__':
    asyncio.run(Server().run())
