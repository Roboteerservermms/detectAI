sudo apt-get install python3.7-pip python3.7-dev python-pip python-dev -y
sudo apt-get install llvm-7 -y
sudo ln -s /usr/bin/llvm-config-7 /usr/bin/llvm-config


sudo LLVM_CONFIG=/usr/bin/llvm-config pip3 install llvmlite==0.29.0
sudo pip3 install numpy==1.17.3
sudo LLVM_CONFIG=/usr/bin/llvm-config pip3 install numba==0.44.0
sudo apt-get install gfortran libopenblas-dev liblapack-dev -y
sudo apt-get install libbz2-dev libatlas-base-dev libgfortran5 liblzma-dev -y
sudo apt install libatlas3-base libgfortran5 -y
sudo pip3 install scipy==1.5.2
sudo LLVM_CONFIG=/usr/bin/llvm-config pip3 install librosa

wget https://github.com/lhelontra/tensorflow-on-arm/releases/tensorflow-2.4.0-cp37-none-linux_aarch64.whl
sudo pip3 install tensorflow-2.4.0-cp37-none-linux_aarch64.whl

sudo apt-get install portaudio19-dev python-pyaudio -y
sudo pip3 install pyaudio
sudo pip3 install matplotlib
sudo pip3 install pandas