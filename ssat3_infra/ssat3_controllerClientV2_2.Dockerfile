ARG OSVERSION=20.04
FROM  ubuntu:${OSVERSION}
#
LABEL com.ssat3.version="2.0.0-test"
LABEL com.ssat3.name="Controller-tester_v2"
LABEL com.ssat3.description="QTemp Controller for IOT climate control - Controller pub-sub tester"
LABEL com.ssat3.build-date="2021-15-02T02:00:30.00Z"
#
# Leaving network diagnostics packages in place for troubleshooting
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
mkdir /opt/storage/conf && \
mkdir /opt/storage/conf/priv
# Build environment
RUN mkdir /opt/qtemp && \
mkdir /opt/qtemp/priv
WORKDIR /opt/qtemp
# Create custom group
RUN groupadd --gid 2000 lpuser && useradd --create-home --gid 2000 --uid 2000 lpuser
USER lpuser
# Update requirements as needed
COPY controller_requirements.txt  /opt/src/requirements.txt
RUN pip install -r /opt/src/requirements.txt
#
#  Copy primary python script
COPY controllerClientv2_2.py /opt/qtemp
#  Copy python modules
COPY appDb.py  /opt/qtemp
COPY appEnc.py  /opt/qtemp
# copy encryption records into private location
COPY manode_keypairs.csv /opt/storage/conf/priv
CMD ["python3","./controllerClientv2_2.py"]