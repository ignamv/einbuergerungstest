FROM python:slim-bookworm

COPY requirements.txt /app/requirements.txt
COPY scrape.py /app/scrape.py
COPY output.py /app/output.py
COPY db.py /app/db.py

RUN pip install -r /app/requirements.txt

ADD entry.sh /app/entry.sh

ENTRYPOINT [ "/app/entry.sh" ]
