xrandr --output HDMI-1 --rotate left
docker stop $(docker container ls -q) || echo "No containers already running" # remove later
docker run -t \
  -d \
  --privileged=true \
  -v /opt/vc:/opt/vc \
  --env LD_LIBRARY_PATH=/opt/vc/lib \
  --device /dev/vchiq \
  --net=host \
  --mount type=bind,source=/home/pi/MagicController,target=/MagicController \
  1646552/magic-controller:latest
# chromium --kiosk http://localhost:8080
chromium http://localhost:8080

