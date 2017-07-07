
import json
import logging
import asyncio

class Client(object):
    def __init__(self, socketpath='/tmp/crawler.sock'):
        self.socketpath = socketpath
        self.loop = asyncio.new_event_loop()
        #self.loop.set_debug(1)

    def connect(self):
        self.reader, self.writer = yield from asyncio.open_unix_connection(self.socketpath, loop=self.loop)
        logging.debug("Connected")

    @asyncio.coroutine
    def add(self, url):
        yield from self.connect()
        cmd = {'command':'add', 'url': url}
        yield from self.sendcmd(cmd)

    def sendcmd(self, cmd):
        sendline = json.dumps(cmd)
        logging.debug("sending: %s", sendline)
        self.writer.write((sendline+"\r\n").encode())
        response = yield from self.reader.readline()
        data = json.loads(response.decode())
        print("; ".join([k+": "+v for (k,v) in data.items()]))
        self.writer.close()

        return data

    def run(self, task):
        self.loop.run_until_complete(task)
        task.close()
        self.loop.close()
        pass
