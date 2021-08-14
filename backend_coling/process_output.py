""" Processes model results and saves in an output file

Processes an output file and creates a JSON object containing 
a dictionary of inputs and segmentations for each token.

Example of a part of JSON output: 
[    
    {
        "input": "isolated", 
        "segmentation": "i*sekw-t"
        "custom_segmentation: "i?sekw?t"
    }, 
    {
        "input": "networks", 
        "segmentation": "networks"
        "custom_segmentation: "net-works"
    }
]
"""
import json
import os
from os import path


# TODO if the current job comes from an eaf file, then split according to annotations.

def process_output(current_job):
    """ processes model output with current_job job id

    Parameters
    ----------
    current_job: number 
        the id of the job which result is to be processed
    """
    # load the job file to get information on eaf annotations if needed.
    job_path = './jobs/coling_{}.txt'.format(current_job)
    with open(job_path, "r") as new_job:
        new_job_contents = new_job.read()
    # converts string dictionary into dictionary
    new_job_data = json.loads(new_job_contents)

    # read the results document into a string 
    # NOTE: the file to read as output can be changed. 
    results_path = 'coling2018-neural-transition-based-morphology/results_inference/Both/Word_dumb/f.beam10.dev.predictions'
    with open(results_path, "r") as new_result:
        new_result_contents = new_result.read()


    # make the results into a list
    result_by_line = new_result_contents.split('\n')
    print(result_by_line)
    print("outputs")
    # for each line, split by space (assumes there is only 
    # one n best result for now)
    # TODO consider splitting in the case where there is more than one n-best result
    result_by_line_split = []

    # sentence_id to mark each sentence
    # word_id to mark a word index relative to a given sentence
    if new_job_data['input_type'] == 'text':
        sentence_id = 0
        word_id = 0
    elif new_job_data['input_type'] == 'eaf_file':
        annotation_list = new_job_data['annotation_list']

    for i in range(len(result_by_line)):
        line = result_by_line[i]
        #ignore blank lines
        if not line:
            # the word 'continue' finishes current iteration 
            # in a loop or exits an if-statement
            continue
        # split each line into tokens
        line_list = line.split()
        # remove the TRANS dummy variable
        # TODO add the line below back when needed to remove TRANS
        # line_list.pop()
        # make a python dictionary
        line_dict = {}
        line_dict["input"] = line_list[0]
        # TODO modify, when we are able to add n-best number of segmentations
        segmentation_list = []
        for x in range(1,len(line_list)):
            segmentation_list.append(line_list[x])
        line_dict["segmentation"] = segmentation_list
        # Set preferred segmentation by default to be the first n-best.
        # Users would be able to change the preferred segmentation.
        line_dict["preferred_segmentation"] = line_list[1]
        line_dict["custom_segmentation"] = []
        # TODO change to a separate section on metadata
        line_dict["model"] = "coling"


        if new_job_data['input_type'] == 'text':
            # assign sentence and word id
            line_dict["sentence_id"] = sentence_id
            # line_dict["word_id"] = word_id

            # upadate sentence and word id
            # word_id = word_id + 1
            # TODO determine a set of sentence-ending symbols
            if line_dict["input"] in [".", "!", "?"]:
                sentence_id = sentence_id + 1
                # word_id = 0

        elif new_job_data['input_type'] == 'eaf_file':
            line_dict["sentence_id"] = annotation_list[i]

        result_by_line_split.append(line_dict)

    # create a JSON object, add indents for JSON readability
    result_json = json.dumps(result_by_line_split, indent = 4)

    # write JSON object into a file and save 
    with open('/data/results/output_inference_json-{}.std.out'.format(current_job), 'w') as outfile:
        outfile.write(result_json)






