# compile the Fairseq model
pwd
cd fairseq && pip install ./ && pip install --upgrade numpy
pwd
cd .. && python3 -u listen_fairseq.py