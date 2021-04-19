sudo rm -rf /var/lib/dpkg/lock*
sudo apt-get update
sudo apt-get -y upgrade
pip3 install urlopen schedule playsound 
sudo apt-get install -y python3-json* python3-urllib3 python3-pandas 
pip3 install youtube-dl pafy python-vlc pyserial vlc-ctrl 
sudo apt install python3-gst-1.0 python3-dbus vlc-*
curl -fsSL https://raw.githubusercontent.com/filebrowser/get/master/get.sh | bash