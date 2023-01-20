FROM quay.io/ansible/ubuntu2204-test-container:main
# ubuntu2204 comes with mariadb-client-10.6

# iproute2                     # To grab docker network gateway address
RUN apt update -y && \
    DEBIAN_FRONTEND=noninteractive apt upgrade -y --no-install-recommends && \
    DEBIAN_FRONTEND=noninteractive apt install -y --no-install-recommends \
    python3.10 \
    mariadb-client \
    iproute2

RUN python3.10 -m pip install --disable-pip-version-check --no-cache-dir pymysql==0.9.3

ENV container=docker
CMD ["/sbin/init"]
