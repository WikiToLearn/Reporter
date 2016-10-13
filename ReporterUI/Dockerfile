FROM python:3.6

RUN pip3 install requests==2.11.1
RUN pip3 install flask==0.11
RUN pip3 install pymongo==3.3.0

COPY . /app
WORKDIR /app
EXPOSE 5000
ENTRYPOINT python run.py
