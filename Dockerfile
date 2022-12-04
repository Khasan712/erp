FROM python:3.10-alpine

ENV PYTHONUNBUFFERED 1

COPY . /app
WORKDIR /app
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

COPY ./entrypoint.sh /entrypoint.sh
ENTRYPOINT ["sh", "/entrypoint.sh"]
