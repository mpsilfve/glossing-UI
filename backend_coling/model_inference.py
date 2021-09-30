""" Passes job file through the model

Parses the input file with a given job ID, extracts the dictionary 
and  makes a job_id.dev file, which will be the file to be passed 
throug the model. Then, it runs the model against the dev file.
"""
import json, os, string, re, sys

def process_file(job_id): 
    # TODO figure out parsing of inputs.
    """ parses the input file into appropriate format 
    and passes the data through the model
    
    Parameters
    ----------
    job_id: number 
        the id of the job to be processed with the model
    """
    # look up the file in jobs folder
    job_path = './jobs/coling_{}.txt'.format(job_id)
    with open(job_path, "r") as new_job:
        new_job_contents = new_job.read()

    # converts string dictionary into dictionary
    new_job_data = json.loads(new_job_contents)

    if new_job_data['input_type'] == 'text':
        # extract the text into a dev file and store it in model_inputs
        text_input = new_job_data["text"]
        # print(text_input)
        # make word list - split text into words 
        # TODO define a defininte list of punctuation to separate
        # TODO think - maybe to separate by spaces first, and then using a regex
        # from https://stackoverflow.com/questions/367155/splitting-a-string-into-words-and-punctuation
        word_list_input = re.findall(r"[^!#$%&()*+,.:;<=>? ]+|[!#$%&()*+,.:;<=>?@]", text_input, re.UNICODE)
        print(word_list_input)
        print("inputs")
    
        processed_input = ''
        for word in word_list_input:
            # add two dummy variables to each word using tab separated format
            # first dummy variable is the word itself, the second one is TRANS
            processed_input += word + "\t" + word + "\t" + "TRANS" + "\n" 
    
        # write the input string in to a file using utf-8 encoding   
        with open('./model_inputs/{}.dev'.format(job_id), 'w') as outfile:
            outfile.write(processed_input.encode('utf-8'))

    elif new_job_data['input_type'] == 'eaf_file':
        eaf_data = new_job_data['eaf_data']
        processed_input = ''
        annotation_list = []
        for annotation in eaf_data:
            annotation_value = annotation['annotation_text']
            annotation_token_list = re.findall(r"[^!#$%&()*+,.:;<=>? ]+|[!#$%&()*+,.:;<=>?@]", annotation_value, re.UNICODE)
            for token in annotation_token_list:
                processed_input += token + "\t" + token + "\t" + "TRANS" + "\n"
                annotation_list.append(annotation['annotation_id']) 
        
        with open('./model_inputs/{}.dev'.format(job_id), 'w') as outfile:
            outfile.write(processed_input.encode('utf-8'))
        
        # the resulting annotation list is saved in the original job file
        # so that when the output is processed it can be accessed
        # and the output token can be assigned to the annotations.
        new_job_data['annotation_list'] = annotation_list
        with open('./jobs/coling_{}.txt'.format(job_id), 'w') as outfile:
            json.dump(new_job_data, outfile)
    
    # determine the python command to run the model with, 
    # alongside with the necessary paths
    train_path = "/backend_coling/dummy_train_file/gitksan.train"
    input_path = "/backend_coling/model_inputs/{}.dev".format(job_id)
    # path that contains the model to be used
    model_path = "/backend_coling/models_and_results/Word_dumb"
    # provides path for default stdout for the model, not particularly useful
    output_path = "/backend_coling/stdout_inference/output_inference-{}.std.out".format(job_id)


    # also: implement bridging code between coling and 
    # my code that loads all data structures.
    # TODO Swap the system calls to something else. we want to run it continuosly like a server. 

    python_script = ("cd /backend_coling/coling2018-neural-transition-based-morphology/lib && python2.7 "
        "run_transducer.py --dynet-seed 47 --dynet-mem 1000 --dynet-autobatch 0  --transducer=haem --sigm2017format "
        "--input=100 --feat-input=20 --action-input=100 --pos-emb  --enc-hidden=200 --dec-hidden=200 --enc-layers=1 "
        "--dec-layers=1   --mlp=0 --nonlin=ReLU --alpha=1   --dropout=0.5 --optimization=ADADELTA --batch-size=1 "
        "--decbatch-size=25  --patience=10 --epochs=60   --align-dumb --iterations=150 --mode=eval --beam-width=8 "
        "--beam-widths=10,10  --pretrain-epochs=0 --sample-size=20 --scale-negative=1  "
        "{trainpath} {devpath} {resultspath} 2>&1 > {outpath}").format(trainpath=train_path, devpath=input_path, resultspath=model_path, outpath=output_path)


    # run the command
    os.system(python_script)

    

