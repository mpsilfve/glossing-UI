mkdir dynet-base 
cd dynet-base
git clone https://github.com/mpsilfve/dynet.git
mkdir eigen 
cd eigen
wget https://github.com/clab/dynet/releases/download/2.1/eigen-b2e267dc99d4.zip
unzip eigen-b2e267dc99d4.zip 
cd ../dynet
mkdir build
cd build
cmake .. -DEIGEN3_INCLUDE_DIR=../../eigen -DPYTHON=`which python`
make -j 2 
cd python
python2.7 ../../setup.py build --build-dir=.. --skip-build install 
export LD_LIBRARY_PATH=/path/to/dynet/build/dynet/:$LD_LIBRARY_PATH
cd ../../../..
