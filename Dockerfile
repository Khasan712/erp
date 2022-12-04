FROM python:3.10-alpine

ENV PYTHONUNBUFFERED 1

COPY . /erp_pro
WORKDIR /erp_pro
RUN pip install --upgrade pip && \
    pip install -r requirements.txt
