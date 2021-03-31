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
import json

def process_file(job_id): 
    # look up the file in jobs folder
    job_path = './jobs/coling_{}.txt'.format(job_id)
    with open(job_path, "r") as new_job:
            new_job_contents = new_job.read()

    new_job_data = json.loads(new_job_contents)  # converts string dictionary into dictionary

    # extract the text into a dev file and store it in model_inputs
    text_input = new_job_data["text"]
    with open('./model_inputs/{}.dev'.format(job_id), 'w') as outfile:
        json.dump(text_input, outfile)
    # determine the python command 
    
    # run the command 
    # store the results in results folder
