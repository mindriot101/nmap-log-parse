FROM debian:wheezy

MAINTAINER Simon Walker <s.r.walker101@googlemail.com>

RUN apt-get update && apt-get install -y \
        python \
        python-matplotlib \
        python-pandas

RUN mkdir -p /logs
WORKDIR /logs
CMD ["python", "plot.py", "db.sqlite"]
