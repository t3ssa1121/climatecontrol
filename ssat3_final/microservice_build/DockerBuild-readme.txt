# Build and run commands, take note of volume mounts, also ensure OS user lpuser, UID/GID 2000:2000 owns actual storage on OS.

sudo docker build -t ssat3_controller-main:2.2.1 -f ssat3_controllerClientV2_2.Dockerfile  .

sudo docker run -h controller-main --name controller-main-22   --env-file .env_controller  -v /opt/storage/conf/priv:/opt/storage/conf/priv -v /opt/storage/logs:/opt/storage/logs  --add-host=mqbroker.qtemp.local:10.100.200.3 --add-host=appdb.qtemp.local:10.100.200.3  -it  ssat3_controller-main:2.2.1

# Build commands for manode
sudo docker build -t ssat3_manode:2.0 -f ssat3_manodeV2_0.Dockerfile  .

# Requires a docker network to have been created first,
# sudo docker network create --subnet=10.10.150.0/24 net150
# sudo docker network ls  -> view networks already in Docker Repository for that server 
sudo docker run --net net150 -h manode5 --ip 10.10.150.50 --name manode5 --env-file .env_node5  --add-host=mqbroker.qtemp.local:10.100.200.3  -i -t  ssat3_manode:2.0
sudo docker run --net net140 -h manode4 --ip 10.10.140.40 --name manode4 --env-file .env_node4  --add-host=mqbroker.qtemp.local:10.100.200.3  -i -t  ssat3_manode:2.0