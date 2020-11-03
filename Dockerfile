FROM ubuntu:latest
ENV DEBIAN_FRONTEND=noninteractive

# Create app directory
WORKDIR /app

# Install app dependencies

RUN apt-get update && apt-get install -y \
    wget \
    python3-pip \
    software-properties-common \
    build-essential \
    libssl-dev \
    libffi-dev \
    python3-dev \
    firefox

RUN wget https://github.com/mozilla/geckodriver/releases/download/v0.27.0/geckodriver-v0.27.0-linux64.tar.gz
RUN tar -xvzf geckodriver*
RUN chmod +x geckodriver
RUN mv geckodriver /usr/local/bin/
RUN rm geckodriver-v0.27.0-linux64.tar.gz

COPY requirements.txt ./

RUN pip3 install -r requirements.txt --no-cache-dir

# Bundle app source
COPY . /app

# Entrypoint
CMD [ "python3", "-m", "pvmon" ]
