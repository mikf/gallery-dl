FROM python:3.8-alpine

RUN python3 -m pip install -U gallery-dl


ENTRYPOINT ["gallery-dl"]
CMD ["gallery-dl"]

