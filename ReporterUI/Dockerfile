FROM python:3.5

RUN pip3 install requests==2.11.1
RUN pip3 install flask==0.11
RUN pip3 install pymongo

COPY . /app
WORKDIR /app
ENTRYPOINT python run.py
