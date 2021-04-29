import json
import os
from os import path


# processes an output file and creates a JSON object containing a dictionary of inputs and segmentations for each token

# Example of a part of JSON output: 
# [    
#     {
#         "input": "isolated", 
#         "segmentation": "i*sekw-t"
#     }, 
#     {
#         "input": "networks", 
#         "segmentation": "networks"
#     }
# ]

def process_output():
    # read the results document into a string 
    results_path = 'coling2018-neural-transition-based-morphology/results_inference/Both/Word_dumb/f.beam10.dev.predictions'
    with open(results_path, "r") as new_result:
        new_result_contents = new_result.read()

    # make the results into a list
    result_by_line = new_result_contents.split('\n')
    print(result_by_line)
    # for each line, split by space (assumes there is only one n best result for now)
    # TODO consider splitting in the case where there is more than one n-best result
    result_by_line_split = []

    for line in result_by_line:
        #ignore blank lines
        if not line:
            # the word 'continue' finishes current iteration in a loop or exits an if-statement
            continue
        # split each line into tokens
        line_list = line.split()
        # remove the TRANS dummy variable
        line_list.pop()
        # make a python dictionary
        line_dict = {}
        line_dict["input"] = line_list[0]
        line_dict["segmentation"] = line_list[1]
        result_by_line_split.append(line_dict)

    # create a JSON object, add indents for JSON readability
    result_json = json.dumps(result_by_line_split, indent = 4)

    # write JSON object into a file and save 
    with open('/backend_coling/results/output_inference_json.std.out', 'w') as outfile:
        outfile.write(result_json)






