FROM python:3.10-alpine

ENV PYTHONUNBUFFERED 1

COPY . /app
WORKDIR /app
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

<<<<<<< HEAD
CMD ['uwsgi', '--socket', ':9000', 'workers', '4', '--master', '--enable-threads', '--module', 'config.wsgi']
=======
COPY ./entrypoint.sh /entrypoint.sh
ENTRYPOINT ["sh", "/entrypoint.sh"]
>>>>>>> 27ba978 (New deploy)
