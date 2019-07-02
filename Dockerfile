FROM python:3.7.3-alpine3.9

RUN mkdir /dnslistmaint
COPY dnsvalidator /dnsvalidator/dnsvalidator.py
COPY requirements.txt /dnsvalidator/requirements.txt

RUN pip install -r /dnsvalidator/requirements.txt

RUN chmod +x /dnslistmaint/dnslistmaint.py

ENTRYPOINT ["/dnslistmaint/dnslistmaint.py"]
