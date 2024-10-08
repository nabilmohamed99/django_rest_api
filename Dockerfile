FROM python:3.10-slim-buster

LABEL maintainer="NabilMohammed"

ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt /tmp/requirements.txt
COPY ./requirements.dev.txt /tmp/requirements.dev.txt

USER root

# Install necessary packages including PostgreSQL development packages
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        sudo \
        pkg-config \
        libicu-dev \
        gcc \
        g++ \
        postgresql-client \
        libpq-dev \
        libjpeg-dev && \
    rm -rf /var/lib/apt/lists/*

COPY ./app /app
WORKDIR /app
EXPOSE 8000

ARG DEV=false
RUN python -m venv /py && \
    /py/bin/pip install --upgrade pip && \
    /py/bin/pip install -r /tmp/requirements.txt && \
    if [ $DEV = "true" ]; \
        then /py/bin/pip install -r /tmp/requirements.dev.txt ; \
    fi && \
    rm -rf /tmp && \
    adduser \
        --disabled-password \
        --no-create-home \
        django-user && \
    mkdir -p /vol/web/media && \
    mkdir -p /vol/web/static && \
    chown -R django-user:django-user /vol && \
    chmod -R 755 /vol

ENV PATH="/py/bin:$PATH"

USER django-user
