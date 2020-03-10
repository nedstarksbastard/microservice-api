FROM python:3.7-alpine

WORKDIR /src

ADD ./requirements.txt /src/requirements.txt

RUN pip install -r requirements.txt

ADD . /src