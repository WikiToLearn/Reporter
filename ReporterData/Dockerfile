FROM wikitolearn/python35:0.1

RUN apt-get update && \
  apt-get -y install cron && \
  rm -f /var/cache/apt/archives/*deb && \
  find /var/lib/apt/lists/ -type f -delete && \
  find /var/log/ -type f -delete

RUN pip3 install requests==2.11.1
RUN pip3 install pymongo==3.3.0
RUN pip3 install PyYAML==3.12

COPY ./src/ /opt

WORKDIR /opt

ENTRYPOINT sh entrypoint.sh
