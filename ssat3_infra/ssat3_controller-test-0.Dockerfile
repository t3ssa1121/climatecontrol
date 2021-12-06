ARG OSVERSION=20.04
FROM  ubuntu:${OSVERSION}
#
LABEL com.ssat3.version="1.0.4-dev"
LABEL com.ssat3.name="Controller-tester_v0"
LABEL com.ssat3.description="QTemp Controller for IOT climate control - Controller pub-sub tester"
LABEL com.ssat3.build-date="2021-12-06T02:00:30.00Z"
#
RUN apt-get update && apt-get install -y \
python3 \
python3-pip \
iputils-ping \
iproute2 \
tcpdump \
&& apt-get clean
# create a directories for persistent storage
RUN mkdir /opt/storage && \
mkdir /opt/storage/logs && \
mkdir /opt/storage/conf
# Build environment
RUN mkdir /opt/qtemp
WORKDIR /opt/qtemp
# Create custom group
RUN groupadd --gid 2000 lpuser && useradd --create-home --gid 2000 --uid 2000 lpuser
USER lpuser
# Update requirements as needed
COPY ma-node_requirements.txt  /opt/src/requirements.txt
RUN pip install -r /opt/src/requirements.txt
#
#  Copy python scripts
COPY controllerTestClient.py /opt/qtemp
# change to starting python on startup once 
#CMD ["bash"]
CMD ["python3","./controllerTestClient.py"]