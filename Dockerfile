FROM python:3.7-alpine
LABEL maintainer="hi@teners.me"

ENV PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1 \
    PIP_NO_CACHE_DIR=off

RUN apk add --no-cache curl gcc build-base linux-headers libffi libffi-dev \
    && curl -sSL https://raw.githubusercontent.com/sdispater/poetry/master/get-poetry.py | python

WORKDIR /app
COPY pyproject.toml poetry.lock /app/

RUN source $HOME/.poetry/env \
    && poetry config settings.virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --no-dev

COPY . /app/

CMD ["sh", "/app/run-app.sh"]

