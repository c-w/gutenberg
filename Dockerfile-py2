ARG PYTHON_VERSION=2.7
FROM python:${PYTHON_VERSION}

WORKDIR /app

ADD requirements-dev.pip /app/requirements-dev.pip
RUN pip install -r /app/requirements-dev.pip

ADD . /app
RUN pip install .

ENV GUTENBERG_DATA=/data

CMD ["nose2"]
