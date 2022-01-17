"""
Passes a job through Fairseq.

Creates a job_id.dev file, which is passed to the Python wrapper for the pre-trained models.
"""

import json, re
from pretrained_models.run_fairseq import *

def process_file(job_id):
    """
    Converts a job json file into an input for the model wrapper.
    Passes it to the model.
    """

    # TODO: just write the files to backend_fairseq for now
    job_path = '/data/inputs/fairseq_{}.txt'.format(job_id)
    with open(job_path, 'r') as new_job:
        new_job_contents = new_job.read()

    new_job_data = json.loads(new_job_contents)

    if new_job_data['input_type'] == 'text':
        text_input = new_job_data['text']

        # convert text stream into a list of sentences
        sentence_list = []
        txt_lines = re.split('\n', text_input)
        for txtl in txt_lines:
            sent_lines = re.split('[.!?] ', txtl)
            for sl in sent_lines:
                sentence_list.append(sl)

        # Save file, send to the wrapper
        # TODO: save where?
        txt_path = '/data/inputs/fairseq_{}.sents'.format(job_id)
        with open(txt_path, 'w') as outpt:
            for sline in sentence_list:
                outpt.write(sline + '\n')

        call_default_model(txt_path, 4, '/data/results/output_inference_json-{}.std.out'.format(job_id))
