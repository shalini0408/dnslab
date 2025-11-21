FROM debian:stable-slim

RUN apt-get update && \
    apt-get install -y unbound dnsutils && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /etc/unbound

COPY unbound.conf .
COPY entrypoint.sh .

RUN chmod +x /etc/unbound/entrypoint.sh

EXPOSE 53/udp 53/tcp

CMD ["/etc/unbound/entrypoint.sh"]

