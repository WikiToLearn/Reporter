FROM python:3.5

RUN pip3 install requests==2.11.1
RUN pip3 install flask==0.11
RUN pip3 install pymongo

COPY . /app
WORKDIR /app

RUN git clone https://github.com/WikiToLearn/ReportsSettings.git /app/reports_settings

ENTRYPOINT python data_aggregator.py
