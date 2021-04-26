sudo rm -rf /var/lib/dpkg/lock*
sudo apt-get update
sudo apt-get -y upgrade
sudo apt-get install -y python3-json* python3-urllib3 python3-pandas 
sudo apt install -y python3-gst-1.0 python3-dbus vlc-*
curl -fsSL https://raw.githubusercontent.com/filebrowser/get/master/get.sh | bash