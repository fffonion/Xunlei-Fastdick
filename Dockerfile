FROM python:2.7-alpine

COPY swjsq.py /

ENTRYPOINT ["python", "/swjsq.py"]
