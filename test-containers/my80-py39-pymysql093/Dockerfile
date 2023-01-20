FROM quay.io/ansible/ubuntu2004-test-container:main
# ubuntu2004 comes with mysql-client-8

# iproute2  # To grab docker network gateway address
RUN apt update -y && \
    DEBIAN_FRONTEND=noninteractive apt upgrade -y --no-install-recommends && \
    DEBIAN_FRONTEND=noninteractive apt install -y --no-install-recommends \
    python3.9 \
    mysql-client \
    iproute2

RUN python3.9 -m pip install --disable-pip-version-check --no-cache-dir pymysql==0.9.3

ENV container=docker
CMD ["/sbin/init"]
