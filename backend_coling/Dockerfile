#  coling model's environment was based on dabian:9
FROM debian:9
WORKDIR /backend_coling
#  coling model uses python 2.7
RUN apt-get update && apt-get install -y \
            python2.7\
            python-pip\
	    libfreetype6-dev\
	    libpng-dev\
	    pkg-config\
	    cmake\
	    git\
	    unzip\
	    wget\
            && apt-get clean && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN python2.7 -m pip install --no-cache-dir --upgrade pip && \
    python2.7 -m pip install --no-cache-dir Cython==0.29.21 numpy==1.14.0 && \
    python2.7 -m pip install --no-cache-dir -r requirements.txt

# Compile dynet manually because the pip package is broken.
COPY compile_dynet.sh .
RUN ./compile_dynet.sh

RUN git clone https://github.com/mpsilfve/coling2018-neural-transition-based-morphology.git && \
    cd coling2018-neural-transition-based-morphology && \
    make && \
    cd ..

COPY listen.py model_inference.py process_output.py .
CMD  python -u listen.py
