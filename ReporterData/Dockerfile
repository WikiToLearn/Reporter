FROM python:3.5

RUN apt-get update && \
 apt-get -y install git && \
 rm -f /var/cache/apt/archives/*deb && \
 find /var/lib/apt/lists/ -type f -delete && \
 find /var/log/ -type f -delete
RUN apt-get update && \
  apt-get -y install cron && \
  rm -f /var/cache/apt/archives/*deb && \
  find /var/lib/apt/lists/ -type f -delete && \
  find /var/log/ -type f -delete

RUN pip3 install requests==2.11.1
RUN pip3 install pymongo==3.3.0

COPY ./src /opt
WORKDIR /opt

ADD ./data.cron /etc/cron.d/

ENTRYPOINT cron -f
