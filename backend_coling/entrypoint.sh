# download the models
pwd
cd models_and_results
if [[ ! -f Word_cls/f.model ]]
then
    pip install gdown
    cd Word_cls
    gdown "https://drive.google.com/uc?id=1rbsl-bjOpNct5e2tYX8qXwIahoklj5KN"
    cd ..
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