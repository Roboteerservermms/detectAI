sudo rm -rf /var/lib/dpkg/lock*
sudo apt-get update
sudo apt-get -y upgrade

## install edgetpu deb package
echo "deb https://packages.cloud.google.com/apt coral-edgetpu-stable main" | sudo tee /etc/apt/sources.list.d/coral-edgetpu.list
	curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key add -

	sudo apt-get update
	sudo apt-get install libedgetpu1-std -y
	sudo apt-get install --no-install-recommends xubuntu-desktop -y

## install tensorFlow Lite and run a model
	sudo apt update
	sudo apt install python3-pip python3-opencv python3.7 python3-scipy python-scipy -y
	sudo apt install libjpeg8-dev zlib1g-dev libtiff-dev libfreetype6 libfreetype6-dev libwebp-dev libopenjp2-7-dev libopenjp2-7-dev cython python3-numpy python3-pil python3-edgetpu -y
	pip3 install Cython 
	pip3 install numpy
	pip3 install Pillow --global-option="build_ext" --global-option="--enable-zlib" --global-option="--enable-jpeg" --global-option="--enable-tiff" --global-option="--enable-freetype" --global-option="--enable-webp" --global-option="--enable-webpmux" --global-option="--enable-jpeg2000"
	sudo apt-get install git
	pip3 install https://dl.google.com/coral/python/tflite_runtime-2.1.0.post1-cp36-cp36m-linux_aarch64.whl
	cd ~
	git clone https://github.com/google-coral/tflite.git
	cd tflite/python/examples/classification
	bash install_requirements.sh
	python3 classify_image.py \
	--model models/mobilenet_v2_1.0_224_inat_bird_quant_edgetpu.tflite \
	--labels models/inat_bird_labels.txt \
	--input images/parrot.jpg
