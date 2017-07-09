
Asyncio crawler daemon prototype
================================

The prototype comprises a client and server program, which communicate using a
simple JSON protocol over a UNIX socket.

Dependecies
-----------

The demo requires python 3.4+ and the aiohttp module from pypi.

Execution
---------

Run:

    python3 crawl451d.py

and in another terminal:

    python3 crawl451-client.py --add <url>


When a URL is added through the client, it is added to a queue internal to the
server process.

Results and checks are recorded in a sqlite database.

Modules & submodules
--------------------

* Crawler451.Client - the client library
* Crawler451.Server - the server library
* Crawler451.Engine - the scheduler and response checking library (used by
  server)
