# syntax=docker/dockerfile:1

FROM python:3.8-slim-buster

WORKDIR /app

RUN apt-get update && apt-get install -y python-pip
RUN apt-get install -y libmariadb-dev

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .

CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0"]