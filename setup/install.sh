# sudo apt update -y
# sudo apt upgrade -y
# cd /home/pi || exit
# git clone https://github.com/n1klasD/MagicController.git
cd /home/pi/MagicController || exit

# install docker if not already installed
docker_installed=$(which docker)

if [ ! -n "$docker_installed" ]
then
  echo Docker is not installed! Installing now...
  sudo curl -s https://get.docker.com | bash
  sudo usermod -aG docker pi
else
  echo Docker is already installed!
fi

# sleep is needed for docker service to start
sleep 5

# pull docker image
echo Pulling image from DockerHub
sudo docker pull 1646552/magic-controller:latest

# create the file /etc/udev/rules.d/99-camera.rules with content: SUBSYSTEM=="vchiq",MODE="0666"
echo Setting up the camera
sudo cp setup/99-camera.rules /etc/udev/rules.d/99-camera.rules

# Add to autostart
echo Enabling autostart
sudo cp /home/pi/MagicController/setup/magicmirror.service /etc/systemd/system/magicmirror.service
sudo chmod 644 /etc/systemd/system/magicmirror.service
sudo chmod +x /home/pi/MagicController/setup/autostart.sh  # In case the git chmod flag doesn't work
sudo systemctl daemon-reload
sudo systemctl enable magicmirror.service
sudo systemctl start magicmirror.service
echo Finished
