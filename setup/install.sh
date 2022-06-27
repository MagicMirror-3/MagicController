sudo apt update -y
sudo apt upgrade -y
cd /home/pi || exit
# git clone https://github.com/n1klasD/MagicController.git
cd /home/pi/MagicController || exit

# install docker
# sudo curl -s https://get.docker.com | bash
# sudo usermod -aG docker pi

# pull docker image
docker pull 1646552/magic-controller:latest

# add camera rules
sudo cp setup/99-camera.rules /etc/udev/rules.d/99-camera.rules
# create the file /etc/udev/rules.d/99-camera.rules with content: SUBSYSTEM=="vchiq",MODE="0666"

# Add to autostart
sudo cp /home/pi/MagicController/setup/magicmirror.service /etc/systemd/system/magicmirror.service
sudo chmod 644 /etc/systemd/system/magicmirror.service
sudo chmod +x /home/pi/MagicController/setup/autostart.sh
sudo systemctl daemon-reload
sudo systemctl enable magicmirror.service
sudo systemctl start magicmirror.service