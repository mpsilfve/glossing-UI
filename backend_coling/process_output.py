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




def process_output(current_job):
    """ processes model output with current_job job id

    Parameters
    ----------
    current_job: number 
        the id of the job which result is to be processed
    """
    # read the results document into a string 
    # NOTE: the file to read as output can be changed. 
    results_path = 'coling2018-neural-transition-based-morphology/results_inference/Both/Word_dumb/f.beam10.dev.predictions'
    with open(results_path, "r") as new_result:
        new_result_contents = new_result.read()

    # make the results into a list
    result_by_line = new_result_contents.split('\n')
    print(result_by_line)
    # for each line, split by space (assumes there is only 
    # one n best result for now)
    # TODO consider splitting in the case where there is more than one n-best result
    result_by_line_split = []

    for line in result_by_line:
        #ignore blank lines
        if not line:
            # the word 'continue' finishes current iteration 
            # in a loop or exits an if-statement
            continue
        # split each line into tokens
        line_list = line.split()
        # remove the TRANS dummy variable
        # TODO add the line below back when needed
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
        result_by_line_split.append(line_dict)

    # create a JSON object, add indents for JSON readability
    result_json = json.dumps(result_by_line_split, indent = 4)

    # write JSON object into a file and save 
    with open('/data/results/output_inference_json-{}.std.out'.format(current_job), 'w') as outfile:
        outfile.write(result_json)






