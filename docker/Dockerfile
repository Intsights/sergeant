FROM python:latest

RUN mkdir --parents /sergeant
WORKDIR /sergeant

COPY requirements.txt requirements.txt
RUN pip3 install --user --upgrade --requirement requirements.txt

COPY tests tests
COPY sergeant sergeant
COPY pyproject.toml pyproject.toml
