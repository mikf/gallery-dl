FROM python:alpine
RUN python3 -m pip install -U gallery-dl
RUN python3 -m pip install -U youtube_dl
RUN apk update
RUN apk add ffmpeg
ENTRYPOINT [ "gallery-dl" ]