# download the models
pwd
cd models_and_results
if [[ ! -f Word_cls/f.model ]]
then
    cd Word_cls
    gdown "https://drive.google.com/uc?id=1bmi6b5QkMQXOqwt7Qfi3cUT356Pm2HSm"
    cd ..
    expectedMD5cls=`md5sum Word_cls/f.model`
    python3 md5_check.py "coling_seg_cls" $expectedMD5cls
fi

if [[ ! -f Word_dumb/f.model ]]
then
    cd Word_dumb
    gdown "https://drive.google.com/uc?id=1AVeR7Zqs7tKg6PFVMmlmlU6fAJRjjldp"
    cd ..
    expectedMD5dumb=`md5sum Word_dumb/f.model`
    python3 md5_check.py "coling_seg_dumb" $expectedMD5dumb
fi

if [[ ! -f Word_smart/f.model ]]
then
    cd Word_smart
    gdown "https://drive.google.com/uc?id=1XU_bpSZMT16wN5z3axOsJ0ru__FIbph2"
    cd ..
    expectedMD5smart=`md5sum Word_smart/f.model`
    python3 md5_check.py "coling_seg_smart" $expectedMD5smart
fi

pwd
cd ..

# compiles the c file in the coling model lib
# and runs listen.py script
pwd 
ls
cd coling2018-neural-transition-based-morphology/lib && make
pwd
#  -u is for unnbuffered binary stdout and stder
cd ../.. && python -u listen.py