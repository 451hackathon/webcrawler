
import re
import asyncio
import logging

import aiohttp

from .datastore import DataStore

class Engine(object):
    """The Engine class manages the HTTP client workers and processes results."""
    def __init__(self, loop, workers=5):
        self.loop = loop
        # define an async queue
        self.queue = asyncio.Queue()
        # save number of workers to start
        self.workers = workers
        # create the HTTP client session
        self.session = aiohttp.ClientSession(loop=self.loop)
        # define the database path
        self.datastorepath = 'crawler.sqlite'
        pass

    def process_command(self, cmd):
        """Dispatch engine commands to named methods"""
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
        """The add command processor.  Adds a passed url to the queue for processing by a worker."""
        logging.debug("Adding: %s", cmd['url'])
        # wait on queue addition
        yield from self.queue.put(cmd['url'])
        # return status to server
        return {'status': 'success', 'added': cmd['url']}


    def spawn_workers(self, loop):
        """Start up workers and retain task objects for controlled shutdown."""
        self.tasks = []
        for i in range(self.workers):
            self.tasks.append(loop.create_task(self.worker()))

    def shutdown(self):
        """Shut down the task workers"""
        for task in self.tasks:
            task.cancel()

    def open_datastore(self):
        """Return an instance of the datastore"""
        return DataStore(self.datastorepath)

    @asyncio.coroutine
    def worker(self):
        """The worker routine.  Loops on queued entries, retrieving the pages and checking the responses."""
        logging.debug("Spawned worker")
        while True:
            logging.debug("Waiting on queue")
            # wait on queue retrieval; blocks if empty
            url = yield from self.queue.get()
            logging.debug("Got url: %s", url)
            # wait on page check
            yield from self.check_url(url)
            logging.debug("Completed")
        logging.debug("Worker exited")

        
    @asyncio.coroutine
    def check_url(self, url):
        """Retrieve and check the url"""
        try:
            # wait on page response
            response = yield from self.session.get(url)
            logging.debug("Headers: %s", response.headers)
            logging.info("Result: %s; %s", url, response.status)
            # wait on page body
            txt = yield from response.text()
            self.process_result(url, response, txt)
        except Exception as exc:
            logging.warning("Error: %s; %s", url, repr(exc))


    def process_result(self, url, response, txt):
        """Check the page response for status code and Link header"""
        ds = self.open_datastore()
        # insert the URL (or get ID for a URL that is already known)
        urlid = ds.insert_url(url)
        link = None
        if response.status == 451:
            logging.info("451 response detected")
            link = response.headers.get('Link')
            if link is not null:
                # link header format: 'Link: <http://example.com>; rel="blocked-by"'
                if re.match('.*; rel="?blocked-by"?', link):
                    logging.info("Valid link header present")
                    link = link.split()[0]
                else:
                    logging.warn("No valid link header present")
        # save status code and link header content (if present)
        ds.insert_result(response.status, link, urlid=urlid)

