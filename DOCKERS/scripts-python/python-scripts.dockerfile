FROM python:slim

WORKDIR /scripts

COPY scripts-python/ ./

CMD ["python","hello-world.py"]