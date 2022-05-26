xrandr --output HDMI-1 --rotate left
sudo docker run -t -d --privileged=true -v /opt/vc:/opt/vc --env LD_LIBRARY_PATH=/opt/vc/lib --device /dev/vchiq --net=host mirror2:latest
chromium --kiosk http://localhost:8080