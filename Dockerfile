FROM python:alpine
RUN python3 -m pip install -U gallery-dl yt-dlp
RUN apk update
RUN apk add ffmpeg
ENTRYPOINT [ "gallery-dl" ]
