#!/usr/bin/env python
# -*- coding: utf-8 -*-

from collections import defaultdict
from db import Session, Host, Event
import pandas as pd
import matplotlib.pyplot as plt
import json

plt.style.use('ggplot')

if __name__ == '__main__':
    session = Session()

    with open('config.json') as infile:
        config = json.load(infile)

    unique_hosts = { host.hostname for host in session.query(Host) }
    timeseries = defaultdict(list)
    x = []
    for event in session.query(Event).order_by('timestamp'):
        x.append(event.timestamp)
        observed_hostnames = { host.hostname for host in event.hosts }
        for hostname in unique_hosts:
            if hostname in observed_hostnames:
                timeseries[hostname].append(1)
            else:
                timeseries[hostname].append(0)

    df = pd.DataFrame(timeseries, index=pd.to_datetime(x, unit='s'))
    df = df.drop(config['hosts_to_ignore'], axis=1)

    fig, axis = plt.subplots()
    df.resample('H').plot(ax=axis)
    axis.set(xlabel='Time', ylabel='Up', ylim=(0, 1.1))
    fig.tight_layout()
    plt.show()
