# new file: /etc/udev/rules.d/99-camera.rules
# content: SUBSYSTEM=="vchiq",MODE="0666"

docker run -it --privileged=true -v /opt/vc:/opt/vc --env LD_LIBRARY_PATH=/opt/vc/lib --device /dev/vchiq tf-lite:0.1

