ARG OSVERSION=20.04
FROM  ubuntu:${OSVERSION}
#
LABEL com.ssat3.version="2.0.0-test"
LABEL com.ssat3.name="Monitoring-Actuator-Node-tester_v2"
LABEL com.ssat3.description="QTemp MA-Node for IOT climate control - Actuator pub-sub tester"
LABEL com.ssat3.build-date="2021-19-014T25:00:30.00Z"
#
# Leaving network diagnostics packages in place for troubleshooting
RUN apt-get update && apt-get install -y \
python3 \
python3-pip \
iputils-ping \
iproute2 \
tcpdump \
&& apt-get clean
# create a directories for persistent storage ( )
#RUN mkdir /opt/storage && \
#mkdir /opt/storage/logs && \
#mkdir /opt/storage/conf && \
#mkdir /opt/storage/conf/priv
# Build environment
RUN mkdir /opt/qtemp && \
mkdir /opt/qtemp/manode
WORKDIR /opt/qtemp/manode
# Create custom group
RUN groupadd --gid 2000 lpuser && useradd --create-home --gid 2000 --uid 2000 lpuser
USER lpuser
# Update requirements as needed
COPY ma-node_requirements.txt  /opt/qtemp/manode/requirements.txt
RUN pip install -r /opt/qtemp/manode/requirements.txt
#
#  Copy primary python script
COPY manodeClient.py /opt/qtemp/manode
#  Copy python modules
COPY controlUnit.py  /opt/qtemp/manode
COPY appEnc.py  /opt/qtemp/manode
CMD ["python3","./manodeClient.py"]