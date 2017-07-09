
import re
import asyncio
import logging

import aiohttp

from .datastore import DataStore

class Engine(object):
    def __init__(self, loop, workers=5):
        self.loop = loop
        self.queue = asyncio.Queue()
        self.workers = workers
        self.session = aiohttp.ClientSession(loop=self.loop)
        self.datastorepath = 'crawler.sqlite'
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

    def open_datastore(self):
        return DataStore(self.datastorepath)

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
            logging.debug("Headers: %s", response.headers)
            logging.info("Result: %s; %s", url, response.status)
            txt = yield from response.text()
            self.process_result(url, response, txt)
        except Exception as exc:
            logging.warning("Error: %s; %s", url, repr(exc))


    def process_result(self, url, response, txt):
        ds = self.open_datastore()
        urlid = ds.insert_url(url)
        link = None
        if response.status == 451:
            logging.info("451 response detected")
            link = response.headers.get('Link')
            if link is not null:
                if re.match('.* rel="?blocked-by"?', link):
                    logging.info("Valid link header present")
                    link = link.split()[0]
                else:
                    logging.warn("No valid link header present")
        ds.insert_result(response.status, link, urlid=urlid)

