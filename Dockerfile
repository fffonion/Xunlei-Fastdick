FROM python:2.7

RUN apt-get update && \
    apt-get install -y net-tools

COPY swjsq.py /

CMD ["python", "/swjsq.py"]
