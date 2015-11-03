#!/usr/bin/env python
# -*- coding: utf-8 -*-

import xml.etree.ElementTree as ET
from glob import iglob
import db
import json
import argparse
import logging


logging.basicConfig(
    level='INFO', format='[%(asctime)s] %(levelname)8s %(message)s')
logger = logging.getLogger('extract.py')


def build_combines_list(mapping):
    reverse = {}
    for target in mapping:
        hosts = mapping[target]
        for host in hosts:
            if host in reverse and reverse[host] != target:
                raise RuntimeError(
                    'Multiple differing entries found for host %s: [%s, %s]' %
                    (
                        host, reverse[host], target))
            reverse[host] = target
    return reverse


def check_for_renames(hostname, combines):
    return combines.get(hostname, hostname)


def main(args):
    with open(args.config) as infile:
        config = json.load(infile)

    combines = build_combines_list(config.get('hosts_to_combine', {}))

    files = iglob('{logsdir}/*.xml'.format(logsdir=args.logsdir))
    database = db.Database(args.database).clear_db().initialise_db()

    for fname in files:
        logger.info('Extracting from %s', fname)

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

            hostname = check_for_renames(hostname_node.attrib['name'],
                                         combines=combines)
            host_id = database.add_host(hostname=hostname, event_id=event_id, )

            address_nodes = host.findall('address')
            for node in address_nodes:
                addrtype = node.attrib['addrtype']
                addr = node.attrib['addr']

                database.add_address(
                    address=addr,
                    type=addrtype,
                    host_id=host_id)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('logsdir')
    parser.add_argument('-d', '--database',
                        required=False,
                        default='db.sqlite')
    parser.add_argument('-c', '--config',
                        required=False,
                        default='config.json')
    main(parser.parse_args())
