#!/usr/bin/env python
# -*- coding: utf-8 -*-

import xml.etree.ElementTree as ET
from glob import iglob
from db import Address, Host, Event, Session, Base


def main():

    Base.metadata.drop_all()
    Base.metadata.create_all()

    files = iglob('logs/*.xml')

    for fname in files:
        session = Session()
        with open(fname) as infile:
            root = ET.fromstring(infile.read())

        timestamp = int(root.attrib['start'])

        hosts = []
        for host in root.findall('host'):
            status = host.find('status')
            if not status.attrib['state'] == 'up':
                continue

            hostname_node = host.find('hostnames').find('hostname')
            if hostname_node is None:
                continue
            hostname = Host(hostname=hostname_node.attrib['name'])

            addresses = []
            address_nodes = host.findall('address')
            for node in address_nodes:
                addrtype = node.attrib['addrtype']
                addr = node.attrib['addr']
                a = Address(type=addrtype, address=addr)
                addresses.append(a)
            hostname.addresses = addresses
            hosts.append(hostname)

        event = Event(timestamp=timestamp, hosts=hosts)
        session.add(event)
        session.commit()


if __name__ == '__main__':
    main()
