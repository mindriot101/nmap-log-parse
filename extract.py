#!/usr/bin/env python
# -*- coding: utf-8 -*-

import xml.etree.ElementTree as ET
from glob import iglob
import db
import json

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
def check_for_renames(hostname):
    return combines.get(hostname, hostname)


def main():

    files = iglob('logs/*.xml')
    database = db.Database('db.sqlite').clear_db().initialise_db()

    for fname in files:
        with open(fname) as infile:
            root = ET.fromstring(infile.read())

        timestamp = int(root.attrib['start'])
        event_id = database.add_event(timestamp)

        hosts = []
        for host in root.findall('host'):
            status = host.find('status')
            if not status.attrib['state'] == 'up':
                continue

            hostname_node = host.find('hostnames').find('hostname')
            if hostname_node is None:
                continue


            hostname = check_for_renames(hostname_node.attrib['name'])
            host_id = database.add_host(
                hostname=hostname,
                event_id=event_id,
            )

            address_nodes = host.findall('address')
            for node in address_nodes:
                addrtype = node.attrib['addrtype']
                addr = node.attrib['addr']

                database.add_address(
                    address=addr,
                    type=addrtype,
                    host_id=host_id)


if __name__ == '__main__':
    main()
