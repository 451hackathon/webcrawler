
import os
import sys
import logging
import argparse

from Crawler451.Client import Client

parser = argparse.ArgumentParser(description="Client program to control crawl451d")
parser.add_argument('--add', metavar='URL', dest='addurl', help="Add a URL to queue")
parser.add_argument('--verbose', '-v', action='store_true', help="Verbose operation")
args = parser.parse_args()
print(args)

logging.basicConfig(
    level=logging.INFO if args.verbose else logging.WARNING,
    format="%(asctime)s\t%(name)s\t%(levelname)s\t%(message)s",
    datefmt="[%Y-%m-%d:%H:%M:%S]",
    )


client = Client()
if args.addurl:
    logging.debug("addurl mode")
    task = client.add(args.addurl)


client.run(task)
