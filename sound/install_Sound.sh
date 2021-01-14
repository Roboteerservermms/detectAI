sudo apt-get install python3.7-pip python3.7-dev python-pip python-dev -y
sudo apt-get install llvm-7 -y
sudo ln -s /usr/bin/llvm-config-7 /usr/bin/llvm-config

curl https://bootstrap.pypa.io/get-pip.py | python3.7

sudo LLVM_CONFIG=/usr/bin/llvm-config python3.7 -m pip install llvmlite==0.29.0
sudo apt-get install gfortran libopenblas-dev liblapack-dev pkg-config libhdf5-100 libhdf5-dev  -y
sudo apt-get install portaudio19-dev python3-pyaudio python3-scipy -y
sudo python3.7 -m pip install pyaudio
sudo python3.7 -m pip install matplotlib
sudo python3.7 -m pip install pandas
sudo apt-get install libbz2-dev libatlas-base-dev libgfortran5 liblzma-dev -y
sudo apt install libatlas3-base libgfortran5 -y
sudo LLVM_CONFIG=/usr/bin/llvm-config python3.7 -m pip install librosa
sudo LLVM_CONFIG=/usr/bin/llvm-config python3.7 -m pip install numba==0.44.0
sudo python3.7 -m pip install https://github.com/lhelontra/tensorflow-on-arm/releases/download/v2.4.0/tensorflow-2.4.0-cp37-none-linux_aarch64.whl