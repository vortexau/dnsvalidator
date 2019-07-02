FROM python:3.7.3-alpine3.9

RUN mkdir /dnslistmaint
COPY dnslistmaint/dnslistmaint.py /dnslistmaint/dnslistmaint.py
COPY requirements.txt /dnslistmaint/requirements.txt

RUN pip install -r /dnslistmaint/requirements.txt

RUN chmod +x /dnslistmaint/dnslistmaint.py

ENTRYPOINT ["/dnslistmaint/dnslistmaint.py"]
