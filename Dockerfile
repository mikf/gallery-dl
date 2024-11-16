FROM python:alpine
ENV LANG=C.UTF-8

RUN : \
    && apk --no-interactive update \
    && apk --no-cache --no-interactive add ffmpeg \
    && rm -rf /var/cache/apk \
    && :

RUN : \
    && python3 -B -m pip --no-cache-dir --no-input --disable-pip-version-check install -U \
        pip \
    && python3 -B -m pip --no-cache-dir --no-input --disable-pip-version-check install -U \
        https://github.com/mikf/gallery-dl/archive/refs/heads/master.tar.gz \
        yt-dlp[default] \
    && ( rm -rf /root/.cache/pip || true ) \
    && ( find /usr/local/lib/python3.*/site-packages/setuptools -name __pycache__ -exec rm -rf {} + || true ) \
    && ( find /usr/local/lib/python3.*/site-packages/wheel      -name __pycache__ -exec rm -rf {} + || true ) \
    && :

ENTRYPOINT [ "gallery-dl" ]
