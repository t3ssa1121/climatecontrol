ARG OSVERSION=20.04
FROM  ubuntu:${OSVERSION}
RUN apt-get update && apt-get install -y \
python3 \
python3-pip \
&& apt-get clean
# create a directory for persistent storage
RUN mkdir /opt/storage
# Build environment
RUN mkdir /opt/src
WORKDIR /opt/src
RUN useradd --create-home lpuser
USER lpuser
# Update requirements as needed
COPY ma-node_requirements.txt  /opt/src/requirements.txt
RUN pip install -r /opt/src/requirements.txt

# change to starting python on startup once 
CMD ["bash"]