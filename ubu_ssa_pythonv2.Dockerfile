FROM  uba_ssa_python
RUN apt-get update && apt-get install -y \
sqlite3 \
&& apt-get clean