FROM python:3.10

ENV PYTHONUNBUFFERED 1

COPY . /app
WORKDIR /app
RUN apt-get install -y libxml2-dev libxslt1-dev build-essential python3-lxml zlib1g-dev
RUN pip3 install --upgrade pip && \
    pip3 install -r requirements.txt
EXPOSE 8001
CMD ["gunicorn", "--bind", ":8001", "--workers", "3", "config.wsgi"]
