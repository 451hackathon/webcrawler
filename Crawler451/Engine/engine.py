
import asyncio
import aiohttp
import logging

class Engine(object):
    def __init__(self, loop, workers=5):
        self.loop = loop
        self.queue = asyncio.Queue()
        self.workers = workers
        self.session = aiohttp.ClientSession(loop=self.loop)
        pass

    def process_command(self, cmd):
        routine = "process_" + cmd['command']
        if not hasattr(self, routine):
            return {'status':'failed','msg':'command not recognized'}

        try:
            result = yield from getattr(self, routine)(cmd)
        except Exception as exc:
            result = {'status':'failed', 'msg': repr(exc)}

        return result

    @asyncio.coroutine
    def process_add(self, cmd):
        logging.debug("Adding: %s", cmd['url'])
        yield from self.queue.put(cmd['url'])
        return {'status': 'success', 'added': cmd['url']}


    def spawn_workers(self, loop):
        self.tasks = []
        for i in range(self.workers):
            self.tasks.append(loop.create_task(self.worker()))

    def shutdown(self):
        for task in self.tasks:
            task.cancel()

    @asyncio.coroutine
    def worker(self):
        logging.debug("Spawned worker")
        while True:
            logging.debug("Waiting on queue")
            url = yield from self.queue.get()
            logging.debug("Got url: %s", url)
            yield from self.check_url(url)
            logging.debug("Completed")
        logging.debug("Worker exited")

        
    @asyncio.coroutine
    def check_url(self, url):
        try:
            response = yield from self.session.get(url)
            logging.info("Result: %s; %s", url, response.status)
            txt = yield from response.text()
        except Exception as exc:
            logging.warning("Error: %s; %s", url, repr(exc))
