FROM python:slim

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
RUN pip install gunicorn

COPY .env .env
COPY credentials.py credentials.py
COPY app app
COPY migrations migrations
COPY main.py config.py boot.sh ./
RUN chmod a+x boot.sh

ENV FLASK_APP main.py

EXPOSE 5000
ENTRYPOINT ["./boot.sh"]
