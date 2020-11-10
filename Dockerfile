FROM python:3.9.0-alpine3.12

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY src/ .

CMD [ "python", "./main.py" ]