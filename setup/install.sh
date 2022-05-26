sudo cp /home/pi/MagicController/setup/magicmirror.service /etc/systemd/system/magicmirror.service
sudo chmod 644 /etc/systemd/system/magicmirror.service
sudo chmod +x /home/pi/MagicController/setup/autostart.sh
sudo systemctl enable magicmirror.service
sudo systemctl start magicmirror.service