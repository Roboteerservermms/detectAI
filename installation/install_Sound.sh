sudo apt-get install python3.7-pip python3.7-dev python-pip python-dev -y
sudo apt-get install llvm-7 -y
sudo ln -s /usr/bin/llvm-config-7 /usr/bin/llvm-config
curl https://bootstrap.pypa.io/get-pip.py | python3.7

sudo apt-get install gfortran libopenblas-dev liblapack-dev -y
sudo apt-get install libbz2-dev libatlas-base-dev libgfortran5 liblzma-dev pybind11-dev -y
sudo apt install libatlas3-base libgfortran5 -y

sudo LLVM_CONFIG=/usr/bin/llvm-config python3.7 -m pip install llvmlite==0.29.0
sudo apt-get install build-essential python3.7 cmake unzip pkg-config gcc-6 g++-6 screen libxmu-dev libxi-dev libglu1-mesa libglu1-mesa-dev libjpeg-dev libpng-dev libtiff-dev libavcodec-dev libavformat-dev libswscale-dev libv4l-dev libxvidcore-dev libx264-dev libopenblas-dev libatlas-base-dev liblapack-dev gfortran libhdf5-serial-dev python3-dev python3-tk python-imaging-tk libgtk-3-dev -y
sudo apt-get install build-essential cmake unzip pkg-config gcc-6 g++-6 screen libxmu-dev libxi-dev libglu1-mesa libglu1-mesa-dev libjpeg-dev libpng-dev libtiff-dev libavcodec-dev libavformat-dev libswscale-dev libv4l-dev libxvidcore-dev libx264-dev libopenblas-dev libatlas-base-dev liblapack-dev gfortran libhdf5-serial-dev python3.7-dev python3.7-tk python-imaging-tk libgtk-3-dev -y
sudo LLVM_CONFIG=/usr/bin/llvm-config python3.7 -m pip install llvmlite==0.29.0
sudo python3.7 -m pip install Cython 
sudo LLVM_CONFIG=/usr/bin/llvm-config python3.7 -m pip install librosa
sudo python3.7 -m pip install numpy==1.17.3
sudo python3.7 -m pip install https://github.com/lhelontra/tensorflow-on-arm/releases/download/v2.4.0/tensorflow-2.4.0-cp37-none-linux_aarch64.whl

sudo apt-get install portaudio19-dev python-pyaudio -y
sudo python3.7 -m pip install pyaudio
sudo python3.7 -m pip install matplotlib
sudo python3.7 -m pip install pandas

