
import logging

from Crawler451.Server import Server

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s\t%(name)s\t%(levelname)s\t%(message)s",
    datefmt="[%Y-%m-%d:%H:%M:%S]",
    )

server = Server()
server.run()
