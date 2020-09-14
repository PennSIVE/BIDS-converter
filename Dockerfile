FROM python:3
COPY main.py /
ENTRYPOINT [ "python", "/main.py" ]
