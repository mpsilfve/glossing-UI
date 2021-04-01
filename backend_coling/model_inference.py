# parse the input file, extract the dictionary, make a id.dev file, 
# write python command, run the model against the dev file, then move the 
# then. move the file from the results folder into the data folder, where the server will listen to the data. 


# file watch 
# dynet_seed = 42  # Load that from the JSON
# run_command([
#     "python", "run_transducer.py",
#     "--dynet-seed", dynet_seed,
#     "--dynet-mem", "1000"
# ])
import json, os

def process_file(job_id): 
    # look up the file in jobs folder
    job_path = './jobs/coling_{}.txt'.format(job_id)
    with open(job_path, "r") as new_job:
        new_job_contents = new_job.read()

    new_job_data = json.loads(new_job_contents)  # converts string dictionary into dictionary

    # extract the text into a dev file and store it in model_inputs
    text_input = new_job_data["text"]
    # text_input = process_text(text_input)
    with open('./model_inputs/{}.dev'.format(job_id), 'w') as outfile:
        outfile.write(text_input.encode('utf-8'))
    # determine the python command 
    train_path = "../data_Ming/trainFiles/gitksan.train"
    input_path = "/backend_coling/model_inputs/{}.dev".format(job_id)
    model_path = "../results_inference/Both/Word_dumb"
    output_path = "/backend_coling/results/output_inference{}.std.out".format(job_id)


    python_script = "cd /backend_coling/coling2018-neural-transition-based-morphology/lib && python2.7 run_transducer.py --dynet-seed 47 --dynet-mem 1000 --dynet-autobatch 0  --transducer=haem --sigm2017format  --input=100 --feat-input=20 --action-input=100 --pos-emb  --enc-hidden=200 --dec-hidden=200 --enc-layers=1 --dec-layers=1   --mlp=0 --nonlin=ReLU --alpha=1   --dropout=0.5 --optimization=ADADELTA --batch-size=1 --decbatch-size=25  --patience=10 --epochs=60   --align-dumb --iterations=150 --mode=eval --beam-width=8 --beam-widths=10,10  --pretrain-epochs=0 --sample-size=20 --scale-negative=1  \"../data_Ming/trainFiles/gitksan.train\" {} \"../results_inference/Both/Word_dumb\" 2>&1 > {} ".format(input_path, output_path) 
    # run the command 
    os.system(python_script)
    print("Command is done")
    

