FROM python:3.8

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

RUN mkdir /fortemap_api
WORKDIR /fortemap_api

RUN apt-get update
RUN apt-get install -y python3-dev default-libmysqlclient-dev

RUN pip install pip -U
ADD requirements.txt /fortemap_api/
RUN pip install gunicorn && pip install --no-cache-dir -r requirements.txt

ADD . /fortemap_api