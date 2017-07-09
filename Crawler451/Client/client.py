
import json
import logging
import asyncio

class Client(object):
    """A client class for communicating with the Crawler451 server"""

    def __init__(self, socketpath='/tmp/crawler.sock'):
        self.socketpath = socketpath
        self.loop = asyncio.new_event_loop()
        #self.loop.set_debug(1)

    def connect(self):
        """Get a stream-style unix socket connection to the server"""
        self.reader, self.writer = yield from asyncio.open_unix_connection(self.socketpath, loop=self.loop)
        logging.debug("Connected")

    @asyncio.coroutine
    def add(self, url):
        """Add a url"""

        # wait on server connection
        yield from self.connect()
        cmd = {'command':'add', 'url': url}

        # wait on command send and response
        yield from self.sendcmd(cmd)

    def sendcmd(self, cmd):

        # create the command json 
        sendline = json.dumps(cmd)
        logging.debug("sending: %s", sendline)

        # write to the server, with network line ending.
        self.writer.write((sendline+"\r\n").encode())

        # wait on response
        response = yield from self.reader.readline()

        # decode and print respone
        data = json.loads(response.decode())

        # response is printed rather than logged; it is real output
        # TODO: better formatting of output (key order is random with dicts)
        print("; ".join([k+": "+v for (k,v) in data.items()]))
        self.writer.close()

        return data

    def run(self, task):
        """Run the client command (obtained from self.add or other coro methods)"""

        self.loop.run_until_complete(task)
        task.close()
        self.loop.close()
        pass
