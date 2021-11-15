ARG OSVERSION=20.04
FROM  ubuntu:${OSVERSION}
RUN apt-get update && apt-get install -y \
Iputils-ping\
Iproute2\
Tcpdump\
Python3\
Python3-pip\
Git\
Wget\
curl \
&& apt-get clean