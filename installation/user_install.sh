sudo rm -rf /var/lib/dpkg/lock*
sudo apt-get update
sudo apt-get -y upgrade
sudo apt-get install -y python3-json* python3-urllib3 python3-pandas 
sudo apt install -y python3-gst-1.0 python3-dbus vlc-* 
sudo apt-get install -y python3-dev libsdl-image1.2-dev libsdl-mixer1.2-dev \
    libsdl-ttf2.0-dev libsdl1.2-dev python3-numpy libportmidi-dev libjpeg-dev \
    libtiff5-dev libx11-6 libx11-dev xfonts-base xfonts-100dpi xfonts-75dpi \
    xfonts-cyrillic fluid-soundfont-gm  \
    libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev
    
sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-key C99B11DEB97541F0
sudo apt-add-repository https://cli.github.com/packages
sudo apt update
sudo apt install gh

curl -fsSL https://raw.githubusercontent.com/filebrowser/get/master/get.sh | bash