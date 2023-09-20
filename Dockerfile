FROM python:3.9

WORKDIR /app
RUN pip install wheel
RUN pip install uwsgi
ADD ./requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt
ADD ./src /app

CMD ["uwsgi", "--ini", "/app/app.ini"]