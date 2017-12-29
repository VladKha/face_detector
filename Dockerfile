# use base python image with python 3
FROM python:3.6.4

ENV PYTHONUNBUFFERED 1

# Set working directory to /code/
COPY . /code/
WORKDIR /code

# install python dependencies
RUN pip install --no-cache-dir -r /code/requirements.txt

# create unprivileged user
RUN adduser --disabled-password --gecos '' myuser