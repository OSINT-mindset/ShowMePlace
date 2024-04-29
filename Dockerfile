FROM python

RUN apt update
RUN apt install -y firefox-esr

WORKDIR /showmeplace

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY showmeplace.py showmeplace.py
