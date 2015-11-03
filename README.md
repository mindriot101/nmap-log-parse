# nmap log parse

My own version of https://github.com/phiresky/nmap-log-parse

## Setup

1. add this line to your **root** crontab on your raspberry pi (or other device that is always on):

`*/10 * * * * nmap -sn $subnet -oX - >> $outputpath/logs`

where

- `$subnet` is your local network, e.g. '192.168.178.\*'
- `$outputpath` is the path where you want your log stored
    

1. copy `config.json.example` to `config.json` and pass in to the
   extract and plot scripts with the `-c/--config` argument

* `hosts_to_ignore` is a list of hostnames to ignore, e.g. the hostname
    of the machine that is collecting the logs as by default it is always
    online
* `host_name_remapping` is a map from found hostname to friendly name,
    for example android devices tend to have a long random string as a
    name. It is much nicer to give these entries nice names
* `hosts_to_combine` is a map from friendly name to a list of potential
    aliases that you wish to combine into a single entry.

**Remember this script is json so arrays and hashes cannot have trailing
commas**

1. Run the `extract.py` script on the directory containing the .xml log
   files. This creates (by default) `db.sqlite` (configurable with
    `-d/--database`).

1. Visualise with `plot.py` taking the database as an argument.

## Requirements

* python
* pandas
* matplotlib

### Ubuntu

`sudo apt-get install python python-pandas python-matplotlib`

### `pip`

`(sudo) pip install pandas matplotlib

### `conda`

`conda install pandas matplotlib`
