FROM  ubu_ssa_python:1.0.0
RUN apt-get update && apt-get install -y \
sqlite3 \
&& apt-get clean
RUN 
RUN mkdir /opt/tls
COPY fakeca.crt /opt/tls