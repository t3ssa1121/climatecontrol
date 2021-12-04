ARG OSVERSION=20.04
FROM  ubuntu:${OSVERSION}
RUN apt-get update && apt-get install -y \
iputils-ping \
iproute2 \
tcpdump \
python3 \
python3-pip \
wget \
curl \
&& apt-get clean
RUN mkdir /opt/storage