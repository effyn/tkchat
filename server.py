import asyncio
import asyncio.exceptions as async_exc

import configtool

# import sqlite3

# db = sqlite3.connect("server.db")

class Server:

    defaults = {
        "port": 8888
    }

    def __init__(self):
        self.config = configtool.read("server", self.defaults)
        self.streams = []

    async def broadcast(self, message):
        await asyncio.gather(*(stream.write(message) for stream in self.streams))

    async def on_connect(self, stream):
        self.streams.append(stream)
        try:
            while not stream.is_closing():
                await self.broadcast(await stream.readuntil())
        except (ConnectionResetError, async_exc.IncompleteReadError) as e:
            print(stream, "RESULTED IN", e)
        self.streams.remove(stream)

    async def start(self):
        port = self.config["port"]
        async with asyncio.StreamServer(self.on_connect, port=port) as ss:
            await ss.serve_forever()

server = Server()

try:
    asyncio.run(server.start())
except KeyboardInterrupt:
    pass
