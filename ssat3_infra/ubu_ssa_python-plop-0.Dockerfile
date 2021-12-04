ARG OSVERSION=20.04
FROM  ubuntu:${OSVERSION}
#
LABEL com.ssat3.version="1.0.3-dev"
LABEL com.ssat3.name="manode_v0.1"
LABEL com.ssat3.description="Monitoring & Actuator Node for IOT climate control"
LABEL com.ssat3.build-date="2021-12-04T04:54:30.00Z"
#
RUN apt-get update && apt-get install -y \
python3 \
python3-pip \
iputils-ping \
iproute2 \
tcpdump \
vim \
&& apt-get clean
# create a directory for persistent storage
RUN mkdir /opt/storage
# Build environment
RUN mkdir /opt/qtemp
WORKDIR /opt/qtemp
RUN useradd --create-home lpuser
USER lpuser
# Update requirements as needed
COPY ma-node_requirements.txt  /opt/src/requirements.txt
RUN pip install -r /opt/src/requirements.txt
#
#  Copy python scripts
COPY manodeTestClient.py /opt/src
# change to starting python on startup once 
CMD ["bash"]