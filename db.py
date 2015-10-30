from __future__ import division, print_function, absolute_import
from sqlalchemy import create_engine
from sqlalchemy import Column, Float, Integer, String, ForeignKey, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, backref
from sqlalchemy.exc import IntegrityError
from collections import defaultdict
import json


engine = create_engine('sqlite:///db.sqlite')
Base = declarative_base(bind=engine)
Session = sessionmaker(bind=engine)

with open('config.json') as infile:
    config = json.load(infile)


def build_combines_list(mapping):
    reverse = {}
    for target in mapping:
        hosts = mapping[target]
        for host in hosts:
            if host in reverse and reverse[host] != target:
                raise RuntimeError(
                    'Multiple differing entries found for host %s: [%s, %s]' % (
                        host, reverse[host], target))
            reverse[host] = target
    return reverse


combines = build_combines_list(config.get('hosts_to_combine', {}))


class Address(Base):
    __tablename__ = 'address'

    id = Column(Integer, primary_key=True)
    type = Column(String, nullable=False)
    address = Column(String, nullable=False)
    host_id = Column(Integer, ForeignKey('host.id'))

class Host(Base):
    __tablename__ = 'host'

    id = Column(Integer, primary_key=True)
    hostname = Column(String, nullable=False)
    event_id = Column(Integer, ForeignKey('event.id'))
    addresses = relationship('Address', backref='host')

    @classmethod
    def check_for_renames(cls, hostname):
        hostname = combines.get(hostname, hostname)
        return cls(hostname=hostname)


class Event(Base):
    __tablename__ = 'event'

    id = Column(Integer, primary_key=True)
    hosts = relationship('Host', backref='event')
    timestamp = Column(Integer, nullable=False)

    def __repr__(self):
        return '<Event timestamp={self.timestamp}>'.format(self=self)
