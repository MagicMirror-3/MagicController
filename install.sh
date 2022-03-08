# enable camera in raspi config
sudo apt update
sudo apt upgrade
sudo reboot
git clone https://github.com/n1klasD/MagicController.git
cd MagicController
git checkout PyDeploy
sudo curl -s https://get.docker.com | bash
sudo usermod -aG docker pi
create the file /etc/udev/rules.d/99-camera.rules with content: SUBSYSTEM=="vchiq",MODE="0666"

sudo docker run -it --device /dev/vchiq --env LD_LIBRARY_PATH=/opt/vc/lib -v /opt/vc:/opt/vc

# bluetooth
# in welcher Datei ? 
ExecStart=/usr/lib/bluetooth/bluetoothd -E