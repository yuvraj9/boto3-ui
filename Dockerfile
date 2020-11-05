FROM python:alpine

LABEL maintainer="yuvraj@atlan.com"

RUN mkdir /cluster
WORKDIR /cluster
COPY . /cluster

RUN pip3 install -r /cluster/requirments.txt
RUN chmod +x entrypoint.sh

ENTRYPOINT ["/bin/sh", "-c" ,"/cluster/entrypoint.sh"]