sudo rm -rf /var/lib/dpkg/lock-frontend
sudo rm -rf /var/lib/dpkg/lock
sudo apt-get update
sudo apt-get -y upgrade
sudo apt-get install python3.7
sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.7 2
## install edgetpu deb package
echo "deb https://packages.cloud.google.com/apt coral-edgetpu-stable main" | sudo tee /etc/apt/sources.list.d/coral-edgetpu.list
	curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key add -

	sudo apt-get update
	sudo apt-get install libedgetpu1-std -y
	sudo apt-get install  xubuntu-desktop -y

## install tensorFlow Lite and run a model
	sudo apt update
	sudo apt install python3-opencv -y
	sudo apt install libjpeg8-dev zlib1g-dev libtiff-dev libfreetype6 libfreetype6-dev libwebp-dev libopenjp2-7-dev libopenjp2-7-dev cython python3-numpy python3-pil python3-edgetpu -y
	sudo LLVM_CONFIG=/usr/bin/llvm-config pip3 install Cython 
	sudo LLVM_CONFIG=/usr/bin/llvm-config pip3 install numpy
	sudo LLVM_CONFIG=/usr/bin/llvm-config pip3 install Pillow --global-option="build_ext" --global-option="--enable-zlib" --global-option="--enable-jpeg" --global-option="--enable-tiff" --global-option="--enable-freetype" --global-option="--enable-webp" --global-option="--enable-webpmux" --global-option="--enable-jpeg2000"
	sudo apt-get install git
	pip3 install https://dl.google.com/coral/python/tflite_runtime-2.1.0.post1-cp37-cp37m-linux_aarch64.whl
	cd ~
	git clone https://github.com/google-coral/tflite.git
	cd tflite/python/examples/classification
	bash install_requirements.sh
	python3 classify_image.py \
	--model models/mobilenet_v2_1.0_224_inat_bird_quant_edgetpu.tflite \
	--labels models/inat_bird_labels.txt \
	--input images/parrot.jpg

## startup setting and encrypt shell script
	cd ~
	sudo chmod 644 /etc/systemd/system/detect.service
	sudo chmod -R 775 ~/detection_gpio.sh
	sudo systemctl enable detect.service
	sudo systemctl start detect.service
	sudo cp autologin.conf /etc/lightdm/lightdm.conf.d/

