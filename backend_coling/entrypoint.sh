# compiles the c file in the coling model lib
# and runs listen.py script
pwd 
ls
cd coling2018-neural-transition-based-morphology/lib && make
pwd
cd ../.. && python listen.py