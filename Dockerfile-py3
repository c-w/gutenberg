ARG PYTHON_VERSION=3.6
FROM python:${PYTHON_VERSION}

RUN apt-get update \
 && apt-get install -y libdb-dev

ENV BERKELEYDB_DIR=/usr

WORKDIR /app

ADD requirements-dev.pip /app/requirements-dev.pip
RUN pip install -r /app/requirements-dev.pip

ADD . /app
RUN pip install .

ENV GUTENBERG_DATA=/data

CMD ["nose2"]
