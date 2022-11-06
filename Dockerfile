FROM python:3.9.15

RUN apt-get update
RUN apt-get install -y python3-pip python3-dev python3-venv autoconf libssl-dev libxml2-dev libxslt1-dev libjpeg-dev libffi-dev libudev-dev zlib1g-dev pkg-config libavformat-dev libavcodec-dev libavdevice-dev libavutil-dev libswscale-dev libavresample-dev libavfilter-dev ffmpeg

RUN git clone https://github.com/home-assistant/core.git
WORKDIR core

RUN bash ./script/setup
