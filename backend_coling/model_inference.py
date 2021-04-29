# file watch 
# dynet_seed = 42  # Load that from the JSON
# run_command([
#     "python", "run_transducer.py",
#     "--dynet-seed", dynet_seed,
#     "--dynet-mem", "1000"
# ])
import json, os, string, re

# parses the input file with a given job ID, extract the dictionary, make a id.dev file, 
# write python command, run the model against the dev file, then move the 
# then. move the file from the results folder into the data folder, where the server will listen to the data. 

# create a list of punctuation marks (used to clean words from punctuation below)
punctuation = re.compile('[%s]' % re.escape(string.punctuation))

def process_file(job_id): 
    # look up the file in jobs folder
    job_path = './jobs/coling_{}.txt'.format(job_id)
    with open(job_path, "r") as new_job:
        new_job_contents = new_job.read()

    new_job_data = json.loads(new_job_contents)  # converts string dictionary into dictionary

    # extract the text into a dev file and store it in model_inputs
    text_input = new_job_data["text"]
    # make word list - split text into words 
    word_list_input = text_input.split()
    # remove punctuation from each word in worl_list_input
    word_list_clean = []
    for word in word_list_input:
        word_list_clean.append(punctuation.sub('', word))

    # create input string by appending each words with two dummy variables and new line characters
    processed_input = ""
    for word in word_list_clean:
        # add two dummy variables to each word using tab separated format
        # first dummy variable is the word itself, the second one is TRANS
        processed_input += word + "\t" + word + "\t" + "TRANS" + "\n" 
 
    # write the input string in to a file using utf-8 encoding   
    with open('./model_inputs/{}.dev'.format(job_id), 'w') as outfile:
        outfile.write(processed_input.encode('utf-8'))
    
    # determine the python command to run the model with, alongside with the necessary paths
    train_path = "../data_Ming/trainFiles/gitksan.train"
    input_path = "/backend_coling/model_inputs/{}.dev".format(job_id)
    model_path = "../results_inference/Both/Word_dumb"
    output_path = "/backend_coling/results/output_inference-{}.std.out".format(job_id)




    python_script = ("cd /backend_coling/coling2018-neural-transition-based-morphology/lib && python2.7 "
        "run_transducer.py --dynet-seed 47 --dynet-mem 1000 --dynet-autobatch 0  --transducer=haem --sigm2017format "
        "--input=100 --feat-input=20 --action-input=100 --pos-emb  --enc-hidden=200 --dec-hidden=200 --enc-layers=1 "
        "--dec-layers=1   --mlp=0 --nonlin=ReLU --alpha=1   --dropout=0.5 --optimization=ADADELTA --batch-size=1 "
        "--decbatch-size=25  --patience=10 --epochs=60   --align-dumb --iterations=150 --mode=eval --beam-width=8 "
        "--beam-widths=10,10  --pretrain-epochs=0 --sample-size=20 --scale-negative=1  "
        "{trainpath} {devpath} {resultspath} 2>&1 > {outpath}").format(trainpath=train_path, devpath=input_path, resultspath=model_path, outpath=output_path)

    # run the command 
    os.system(python_script)

    # now, we need to move the results to results folder.
    

