FROM python:latest

MAINTAINER InnovativeInventor

WORKDIR /usr/src/app

RUN apt-get update && apt-get install python-pip python-dev libmariadb-dev-compat libmariadb-dev -y
RUN pip3 install waitress flask Flask-Dance validators dataset pytz gitpython icalendar rapidfuzz mysqlclient PyMySQL stripe msgpack flask_cors
COPY server/ /usr/src/app/

EXPOSE 5000
CMD [ "waitress-serve", "--listen=*:5000", "--url-scheme=https", "app:app" ]
