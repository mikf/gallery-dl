FROM python

RUN apt-get update && apt-get install -y git

RUN mkdir /dl
RUN mkdir /download

WORKDIR /dl

RUN git clone https://github.com/mikf/gallery-dl.git /dl
RUN python setup.py install

WORKDIR /download

ENTRYPOINT [ "gallery-dl" ]