FROM python:3.8.12-alpine
RUN mkdir clear_db_daemon
COPY requirements.txt /clear_db_daemon/requirements.txt
RUN pip install -r /clear_db_daemon/requirements.txt
COPY . clear_db_daemon
WORKDIR clear_db_daemon
CMD ["python", "clear_db_daemon.py"]