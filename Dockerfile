FROM python:3

EXPOSE 443

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

RUN pip install python-telegram-bot parsedatetime

COPY . /usr/src/app

CMD [ "python", "./main.py" ]
