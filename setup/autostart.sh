#!/usr/bin/env sh

sleep 10  # This is ugly, but somehow the only way to make xrandr ready for rotate on startup
DISPLAY=:0 xrandr --output HDMI-1 --rotate left

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

# Wait for the container to start before opening the webpage
sleep 5

# Determine whether chromium is executed with 'chroumium' or 'chromium-browser'
is_chromium=$(which chromium)

if [ -n "$is_chromium" ]
then
  chromium --kiosk http://localhost:8080
else
  chromium-browser --kiosk http://localhost:8080
fi
