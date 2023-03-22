FROM python:3.10

ENV PYTHONUNBUFFERED 1

COPY . /app
WORKDIR /app
RUN pip3 install --upgrade pip && \
    pip3 install -r requirements.txt
EXPOSE 8001
<<<<<<< HEAD
CMD ["gunicorn", "--bind", ":8001", "--workers", "3", "config.wsgi"]
=======
CMD ["gunicorn", "--bind", ":8001", "--workers", "3", "config.wsgi"]
>>>>>>> ee92440 (..)
