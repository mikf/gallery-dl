FROM python:alpine
RUN python3 -m pip install --no-cache-dir -U pip  && \
    python3 -m pip install --no-cache-dir -U gallery-dl yt-dlp
RUN apk update && \
    apk add --no-cache ffmpeg && \
    rm -rf /var/cache/apk/*
ENTRYPOINT [ "gallery-dl" ]
