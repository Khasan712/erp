FROM python:3.10

ENV PYTHONUNBUFFERED 1

COPY . /app
WORKDIR /app
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

COPY ./entrypoint.sh /entrypoint.sh
#COPY ./local-runserver.sh /local-runserver.sh
ENTRYPOINT ["sh", "/entrypoint.sh"]
