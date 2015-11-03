#!/usr/bin/env python
# -*- coding: utf-8 -*-

from collections import defaultdict
import db
import pandas as pd
import matplotlib.pyplot as plt
import json
import datetime

if __name__ == '__main__':

    with open('config.json') as infile:
        config = json.load(infile)

    database = db.Database('db.sqlite')

    # unique_hosts = {host.hostname for host in session.query(Host)}
    unique_hosts = database.unique_hosts()
    timeseries = defaultdict(list)
    x = []
    for event in database.get_events():
        x.append(event.timestamp)
        observed_hostnames = {hostname for hostname in
                              database.get_hosts(event)}
        for hostname in unique_hosts:
            if hostname in observed_hostnames:
                timeseries[hostname].append(1)
            else:
                timeseries[hostname].append(0)

    df = pd.DataFrame(timeseries, index=pd.to_datetime(x, unit='s'))
    df = df.drop(config['hosts_to_ignore'], axis=1)
    df = df.rename(columns=config['host_rename_mapping'])

    now = datetime.datetime.now()
    beginning = now - datetime.timedelta(days=1)
    fig, axis = plt.subplots()
    df.resample('H').plot(ax=axis)
    axis.set(xlabel='Time', ylabel='Up', xlim=(beginning, now),
             ylim=(0, 1.1))
    fig.tight_layout()
    plt.show()
