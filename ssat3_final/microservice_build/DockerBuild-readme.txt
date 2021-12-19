# Build and run commands, take note of volume mounts, also ensure OS user lpuser, UID/GID 2000:2000 owns actual storage on OS.

sudo docker build -t ssat3_controller-main:2.2.1 -f ssat3_controllerClientV2_2.Dockerfile  .

sudo docker run -h controller-main --name controller-main-22   --env-file .env_controller  -v /opt/storage/conf/priv:/opt/storage/conf/priv -v /opt/storage/logs:/opt/storage/logs  --add-host=mqbroker.qtemp.local:10.100.200.3 --add-host=appdb.qtemp.local:10.100.200.3  -it  ssat3_controller-main:2.2.1

# Build commands for manode
sudo docker build -t ssat3_manode:2.0 -f ssat3_manodeV2_0.Dockerfile  .