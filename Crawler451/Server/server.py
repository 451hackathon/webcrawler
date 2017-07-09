
import os
import json
import logging
import asyncio

from ..Engine import Engine

class Server(object):
    def __init__(self, socketpath='/tmp/crawler.sock'):
        self.loop = asyncio.get_event_loop()
        self.socketpath = socketpath

        # create an instance of the scheduling engine
        self.engine = Engine(self.loop)

    def run(self):
        # startup workers in engine
        self.engine.spawn_workers(self.loop)

        # create a server instance with a unix socket connection
        server_coroutine = asyncio.start_unix_server(self.on_connect, self.socketpath, loop=self.loop)
        
        server = self.loop.create_task(server_coroutine)
        try:
            self.loop.run_forever()
        except KeyboardInterrupt as exc:
            pass
        
        self.engine.shutdown()
        self.loop.close()
        os.unlink(self.socketpath)

    def on_connect(self, reader, writer):
        """Callback to run on client connection"""

        # wait on client command
        data = yield from reader.readline()
        logging.debug("Read: %s", data.decode().strip())

        cmd = json.loads(data.decode())
        # wait on engine processing
        result = yield from self.engine.process_command(cmd)

        # send engine response back to client
        writer.write((json.dumps(result) + "\r\n").encode())
        writer.close()
