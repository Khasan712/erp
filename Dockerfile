FROM python:3.10

ENV PYTHONUNBUFFERED 1

COPY . /app
WORKDIR /app
RUN pip install --upgrade pip && \
    pip install -r requirements.txt \


#EXPOSE 8001

CMD ["gunicorn", "--bind", ":8001", "--workers", "3", "config.wsgi"]
