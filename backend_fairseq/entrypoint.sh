#!/bin/bash

# install Fairseq
pwd
cd fairseq #&& pip install ./ && pip install --upgrade numpy
pwd
cd ../pretrained_models

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