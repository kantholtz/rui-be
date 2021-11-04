# syntax=docker/dockerfile:1.0.0-experimental

FROM python:3.9-slim-buster

WORKDIR /rui-be/

COPY ./ ./

RUN apt update
RUN apt install -y g++ git
RUN mkdir -p -m 0600 ~/.ssh && ssh-keyscan git.ramlimit.de >> ~/.ssh/known_hosts
RUN --mount=type=ssh pip install .

CMD ["rui-be"]
