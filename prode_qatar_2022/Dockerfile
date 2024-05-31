# pull official base image
FROM python:3.10.11-slim-buster

# set work directory
WORKDIR /usr/src/prode_qatar_2022

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install -r requirements.txt

# copy project
COPY . .