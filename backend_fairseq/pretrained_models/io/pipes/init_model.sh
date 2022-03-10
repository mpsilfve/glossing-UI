#!/bin/bash

# ARGS
# 1: pipe path
# 2: checkpoint path
# 3: nbest
# 4: preprocessing path
# 5: out file path

# Returns the process pid

tail -f $1 | fairseq-interactive --path $2 --beam 5 --nbest $3 --source-lang src --target-lang trg $4 > $5 &
echo $!