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

# copy entrypoint.sh
COPY docker-entrypoint.sh /usr/src/prode_qatar_2022/docker-entrypoint.sh

# ensure the entrypoint.sh has execute permission
RUN chmod +x /usr/src/prode_qatar_2022/docker-entrypoint.sh

# set entrypoint.sh as the entrypoint
ENTRYPOINT ["sh", "/usr/src/prode_qatar_2022/docker-entrypoint.sh"]