# download the models
pwd
cd models_and_results
if [[ ! -f Word_cls/f.model ]]
then
    cd Word_cls
    gdown "https://drive.google.com/uc?id=1bmi6b5QkMQXOqwt7Qfi3cUT356Pm2HSm"
    cd ../../../config
    pwd
    expectedMD5cls=`md5sum ../backend_coling/models_and_results/Word_cls/f.model`
    python3 md5_check.py "coling_seg_cls" $expectedMD5cls
    cd ../backend_coling/models_and_results
fi

if [[ ! -f Word_dumb/f.model ]]
then
    cd Word_dumb
    gdown "https://drive.google.com/uc?id=1AVeR7Zqs7tKg6PFVMmlmlU6fAJRjjldp"
    cd ../../../config
    pwd
    expectedMD5dumb=`md5sum ../backend_coling/models_and_results/Word_dumb/f.model`
    python3 md5_check.py "coling_seg_dumb" $expectedMD5dumb
    cd ../backend_coling/models_and_results
fi

if [[ ! -f Word_smart/f.model ]]
then
    cd Word_smart
    gdown "https://drive.google.com/uc?id=1XU_bpSZMT16wN5z3axOsJ0ru__FIbph2"
    cd ../../../config
    pwd
    expectedMD5smart=`md5sum ../backend_coling/models_and_results/Word_smart/f.model`
    python3 md5_check.py "coling_seg_smart" $expectedMD5smart
    cd ../backend_coling/models_and_results
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