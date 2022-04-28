# new file: /etc/udev/rules.d/99-camera.rules
# content: SUBSYSTEM=="vchiq",MODE="0666"


# docker run -it --privileged=true -v /opt/vc:/opt/vc --env LD_LIBRARY_PATH=/opt/vc/lib --device /dev/vchiq tf-lite:0.1

xrandr --output HDMI-1 --rotate left
docker run -it --privileged=true -v /opt/vc:/opt/vc --env LD_LIBRARY_PATH=/opt/vc/lib --device /dev/vchiq --net=host mirror:latest