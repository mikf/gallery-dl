FROM python:3.14-alpine
ENV LANG=C.UTF-8

RUN : \
    && apk --no-interactive update \
    && apk --no-interactive --no-cache add ffmpeg \
    && rm -rf /var/cache/apk \
    && :

COPY ./requirements requirements/

RUN : \
    && python3 -B -m pip --no-cache-dir --no-input --disable-pip-version-check install --root-user-action ignore -U \
        --require-hashes --only-binary :all: \
        -r requirements/pip \
    && python3 -B -m pip --no-cache-dir --no-input --disable-pip-version-check install --root-user-action ignore -U \
        --require-hashes --only-binary :all: \
        -r requirements/docker \
    && python3 -B -m pip --no-cache-dir --no-input --disable-pip-version-check install --root-user-action ignore -U \
        https://codeberg.org/mikf/gallery-dl/archive/master.tar.gz \
    && python3 -B -m pip --no-cache-dir --no-input --disable-pip-version-check freeze \
    && ( rm -rf /root/.cache/pip || true ) \
    && ( find /usr/local/lib/python3.*/site-packages/setuptools -name __pycache__ -exec rm -rf {} + || true ) \
    && ( find /usr/local/lib/python3.*/site-packages/wheel      -name __pycache__ -exec rm -rf {} + || true ) \
    && :

ENTRYPOINT [ "gallery-dl" ]
