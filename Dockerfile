FROM python:3.10-alpine

ENV PYTHONUNBUFFERED 1

COPY . /app
WORKDIR /app
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

CMD ['uwsgi', '--socket', ':9000', 'workers', '4', '--master', '--enable-threads', '--module', 'config.wsgi']
