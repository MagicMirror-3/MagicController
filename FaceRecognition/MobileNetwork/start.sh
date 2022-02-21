# new file: /etc/udev/rules.d/99-camera.rules
# content: SUBSYSTEM=="vchiq",MODE="0666"

docker run -it --privileged --device /dev/vchiq -v /opt/vc:/opt/vc --env LD_LIBRARY_PATH=/opt/vc/lib tf-lite:0.1