FROM ubuntu:latest

# Create app directory
WORKDIR /app

# Install app dependencies

RUN apt-get update && apt-get install -y \
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

RUN pip3 install -r requirements.txt

# Bundle app source
COPY . /app

# Copy any required local libraries and pip install them

# Note that you'll need to temporarily copy any required libraries into the build context on account of the design of Docker; in this case I copy the required library into a /libs/ subfolder in the main project root folder on the dev machine before pip installing it (no need to install in editable mode as the image and box are disposable)

RUN pip3 install /app/libs/liblogger

# Entrypoint
CMD [ "python", "-m", "pvmon" ]

# Uncomment this when building an image for debugging from bash
# CMD [ "/bin/bash" ]