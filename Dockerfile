FROM python:3.8-slim-buster

COPY . /app
COPY config.docker.ini /app/config.ini
WORKDIR /app

RUN pip install -r requirements.txt

CMD ["python", "main.py"]

EXPOSE 8283