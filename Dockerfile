FROM python:3.10-alpine

# Installing system libraries for python modules (if pip can't handle it)
# Установка системных библиотек для модулей питона (если pip не справляется)
RUN apk update && \
    apk add --virtual build-deps gcc libpq-dev musl-dev

ENV PYTHONUNBUFFERED=true
WORKDIR /contract_constructor
COPY ./src ./src
COPY requirements.txt ./
COPY pandoc ./pandoc
RUN python -m pip install -r requirements.txt
EXPOSE 8000
WORKDIR /contract_constructor/src
ENV PATH="${PATH}:/contract_constructor"
