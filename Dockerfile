FROM python:2.7

RUN apt-get update && \
    apt-get install -y net-tools

COPY swjsq.py /

ENTRYPOINT ["python", "/swjsq.py"]
