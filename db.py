from __future__ import division, print_function, absolute_import
from collections import defaultdict, namedtuple
import json
import sqlite3
from contextlib import contextmanager

class Transaction(object):
    def __init__(self, connection):
        self.connection = connection
        self.cursor = self.connection.cursor()

    def __enter__(self):
        return self.cursor

    def __exit__(self, *args, **kwargs):
        try:
            self.connection.commit()
        except:
            self.connection.rollback()
            raise


EventEntry = namedtuple('EventEntry', ['timestamp', 'event_id'])


class Database(object):
    tablenames = ['address', 'host', 'event']

    def __init__(self, dbname):
        self.dbname = dbname
        self.connection = sqlite3.connect(self.dbname)

    def cursor(self):
        return Transaction(self.connection)

    def clear_db(self):
        with self.cursor() as cursor:
            for name in self.tablenames:
                cursor.execute('drop table if exists {}'.format(name))
        return self


    def initialise_db(self):
        with self.cursor() as cursor:
            cursor.execute('''
                           CREATE TABLE event (
                           id INTEGER NOT NULL,
                           timestamp INTEGER NOT NULL,
                           PRIMARY KEY (id));
                           ''')

            cursor.execute('''
                           CREATE TABLE host (
                           id INTEGER NOT NULL,
                           hostname VARCHAR NOT NULL,
                           event_id INTEGER,
                           PRIMARY KEY (id),
                           FOREIGN KEY(event_id) REFERENCES event (id));
                           ''')

            cursor.execute('''
                           CREATE TABLE address (
                           id INTEGER NOT NULL,
                           type VARCHAR NOT NULL,
                           address VARCHAR NOT NULL,
                           host_id INTEGER,
                           PRIMARY KEY (id),
                           FOREIGN KEY(host_id) REFERENCES host (id));
                           ''')
        return self



    def add_event(self, timestamp):
        with self.cursor() as cursor:
            cursor.execute('insert into event (timestamp) values (?)',
                           (timestamp, ))
            return cursor.lastrowid

    def add_host(self, hostname, event_id):
        with self.cursor() as cursor:
            cursor.execute(
                'insert into host (hostname, event_id) values (?, ?)',
                (hostname, event_id))

    def add_address(self, address, type, host_id):
        with self.cursor() as cursor:
            cursor.execute(
                'insert into address (address, type, host_id) values (?, ?, ?)',
                (address, type, host_id))


    def unique_hosts(self):
        with self.cursor() as cursor:
            cursor.execute('select distinct hostname from host')
            return { row[0] for row in cursor.fetchall() }


    def get_events(self):
        with self.cursor() as cursor:
            cursor.execute(
                'select id, timestamp from event order by timestamp')
            for (event_id, timestamp) in cursor:
                yield EventEntry(event_id=event_id, timestamp=timestamp)

    def get_hosts(self, event):
        with self.cursor() as cursor:
            cursor.execute(
                '''select hostname from host
                where event_id = ?''',
                (event.event_id, ))
            for hostname, in cursor:
                yield hostname
