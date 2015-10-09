from sqlalchemy import create_engine
from sqlalchemy import Column, Float, Integer, String, ForeignKey, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, backref
from sqlalchemy.exc import IntegrityError


engine = create_engine('sqlite:///db.sqlite')
Base = declarative_base(bind=engine)
Session = sessionmaker(bind=engine)


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

class Event(Base):
    __tablename__ = 'event'

    id = Column(Integer, primary_key=True)
    hosts = relationship('Host', backref='event')
    timestamp = Column(Integer, nullable=False)

    def __repr__(self):
        return '<Event timestamp={self.timestamp}>'.format(self=self)
