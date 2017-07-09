
import logging
import sqlite3

class DataStore(object):
    def __init__(self, path):
        self.path = path
        self.conn = sqlite3.connect(path)
        self.create_tables()

    def create_tables(self):
        c = self.conn.cursor()
        try:
            c.execute("select 1 from urls limit 1")
            c.close()
        except sqlite3.OperationalError:
            self.conn.rollback()
            c.execute("""CREATE TABLE urls (id integer primary key, url varchar unique, created datetime);""")
            c.execute("""CREATE TABLE results (id integer primary key, urlid int, status int, blockedby varchar(2048), created datetime);""")
            c.close()
        self.conn.commit()

    def insert_url(self, url):
        c = self.conn.cursor()
        try:
            c.execute("insert into urls(url, created) values (?, CURRENT_TIMESTAMP)",
                [url])
            ret = c.lastrowid
            logging.debug("Added: %s", ret)
        except sqlite3.IntegrityError:
            c.execute("select id from urls where url = ?",[url])
            row = c.fetchone()
            ret = row[0]
        c.close()
        self.conn.commit()
        return ret

    def insert_result(self, status, blockedby, url=None, urlid=None):
        c = self.conn.cursor()
        if url is None and urlid is None:
            raise ValueError("supply url or urlid for insert_result")
        if urlid is None:
            c.execute("select id from urls where url = ?",[url])
            row = c.fetchone()
            urlid = row[0]

        c.execute("""insert into results (urlid, status, blockedby, created)
            values (?, ?, ?, CURRENT_TIMESTAMP)""",
            [urlid, status, blockedby])
        c.close()
        self.conn.commit()


