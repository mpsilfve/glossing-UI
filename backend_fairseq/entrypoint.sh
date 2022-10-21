#!/bin/bash

# install Fairseq
pwd
if [[ ! -x "$(command -v fairseq)" ]]; then
    git clone https://github.com/mpsilfve/fairseq.git
    cd fairseq && pip install ./ && pip install --upgrade numpy
    pwd
    cd ..
fi
pwd
cd pretrained_models

# download the checkpoints
if [[ ! -f data/gloss/checkpoint_best.pt ]]
then
    cd data/gloss
    wget -O checkpoint_best.pt https://github.com/mpsilfve/glossing-UI/releases/download/v0.2/checkpoint_best_gloss.pt
    cd ../..
    expectedMD5gloss=`md5sum data/gloss/checkpoint_best.pt`
    python3 md5_check.py "fairseq_gloss" $expectedMD5gloss
fi



if [[ ! -f data/morphseg/lstm/checkpoint_best.pt ]]
then
    cd data/morphseg/lstm
    wget -O checkpoint_best.pt https://github.com/mpsilfve/glossing-UI/releases/download/v0.2/checkpoint_best_seg.pt
    cd ../../..
    expectedMD5seg=`md5sum data/morphseg/lstm/checkpoint_best.pt`
    python3 md5_check.py "fairseq_seg" $expectedMD5seg
fi

pwd

# create named pipes for the models
PIPE_DIR=io/pipes
if [[ -p $PIPE_DIR/glossPipe ]] 
then
    rm $PIPE_DIR/glossPipe
fi
mkfifo $PIPE_DIR/glossPipe

if [[ -p $PIPE_DIR/glossOut ]]
then
    rm $PIPE_DIR/glossOut
fi
mkfifo $PIPE_DIR/glossOut

if [[ -p $PIPE_DIR/morphSegPipe ]]
then
    rm $PIPE_DIR/morphSegPipe
fi
mkfifo $PIPE_DIR/morphSegPipe

# init the fairseq-interactive processes
OUT_DIR=io/outputs
rm $OUT_DIR/gloss_out.txt
rm $OUT_DIR/morph_seg_out.txt

#time head -n 1 dev_small.txt | fairseq-interactive --path data/gloss/checkpoint_best.pt --beam 5 --nbest 1 --source-lang src --target-lang trg data/gloss/gloss_preprocess > out.txt

# tail -f $PIPE_DIR/glossPipe | fairseq-interactive --path data/gloss/checkpoint_best.pt --beam 5 --nbest 4 \
#     --source-lang src --target-lang trg data/gloss/gloss_preprocess > $OUT_DIR/gloss_out.txt &

# tail -f $PIPE_DIR/morphSegPipe | fairseq-interactive --path data/morphseg/lstm/checkpoint_best.pt --beam 5 --nbest 4 \
#     --source-lang src --target-lang trg data/morphseg/lstm/lstm_preprocess > $OUT_DIR/morph_seg_out.txt &

# init the listener
cd .. && python3 -u listen_fairseq.py