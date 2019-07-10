FROM python:3.7.3-alpine3.9

RUN apk add --no-cache shadow bash && \
    mkdir /dnsvalidator && \
    useradd --create-home --shell /sbin/nologin dnsvalidator

COPY . /dnsvalidator/

WORKDIR /dnsvalidator/

RUN ls -laR

RUN chown -R dnsvalidator:dnsvalidator /dnsvalidator && \
    python3 setup.py install

USER dnsvalidator

RUN ls -la /usr/local/bin/dnsvalidator

ENTRYPOINT ["/usr/local/bin/dnsvalidator"]
