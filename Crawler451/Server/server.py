
import os
import json
import logging
import asyncio

from ..Engine import Engine

class Server(object):
    def __init__(self, socketpath='/tmp/crawler.sock'):
        self.loop = asyncio.get_event_loop()
        self.socketpath = socketpath
        self.engine = Engine(self.loop)

    def run(self):
        self.engine.spawn_workers(self.loop)
        server_coroutine = asyncio.start_unix_server(self.on_connect, self.socketpath, loop=self.loop)
        #server = self.loop.run_until_complete(server_coroutine)
        server = self.loop.create_task(server_coroutine)
        try:
            self.loop.run_forever()
        except KeyboardInterrupt as exc:
            pass
        #server.close()
        self.engine.shutdown()
        self.loop.close()
        os.unlink(self.socketpath)

    def on_connect(self, reader, writer):
        data = yield from reader.readline()
        logging.debug("Read: %s", data.decode().strip())

        cmd = json.loads(data.decode())
        result = yield from self.engine.process_command(cmd)

        writer.write((json.dumps(result) + "\r\n").encode())
        writer.close()
