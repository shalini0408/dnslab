FROM debian:stable-slim

RUN apt-get update && \
    apt-get install -y bind9 dnsutils && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /etc/bind

COPY named.conf .
COPY named.conf.local .
COPY db.victim.local .
COPY entrypoint.sh .

RUN chmod +x /etc/bind/entrypoint.sh && \
    chown -R bind:bind /etc/bind && \
    chmod -R 775 /etc/bind

EXPOSE 53/udp 53/tcp

CMD ["/etc/bind/entrypoint.sh"]

