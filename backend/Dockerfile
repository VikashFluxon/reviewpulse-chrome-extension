FROM --platform=linux/amd64 ubuntu:latest

# Updating apt to see and install Google Chrome
RUN apt-get -y update

RUN apt-get install -y wget unzip

RUN wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb

RUN apt install -y ./google-chrome-stable_current_amd64.deb

RUN wget -O /tmp/chromedriver.zip http://chromedriver.storage.googleapis.com/114.0.5735.90/chromedriver_linux64.zip

RUN unzip /tmp/chromedriver.zip chromedriver -d /usr/local/bin/

ENV DISPLAY=:99

RUN apt-get -y install xvfb x11-apps x11-xkb-utils libx11-6 libx11-xcb1

# Install Python and pip
RUN apt-get update -y && \
    apt-get install -y python3 python3-pip

WORKDIR /var/task
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY ./app ./app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]