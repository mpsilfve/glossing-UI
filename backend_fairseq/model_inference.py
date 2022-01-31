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

    # TODO: Debug
    print(new_job_data)

    # check for options
    n_best = int(new_job_data['nbest'])

    if new_job_data['input_type'] == 'text':
        text_input = new_job_data['text']

        # convert text stream into a list of sentences
        sentences = []
        txt_lines = re.split('\n', text_input)
        for txtl in txt_lines:
            sent_lines = re.split('[.!?] ', txtl)
            for sl in sent_lines:
                sentences.append(sl)

    elif new_job_data['input_type'] == 'eaf_file':
        eaf_data = new_job_data['eaf_data']

        # each annotation is considered a sentence
        sentences = []
        annotation_list = []
        for annotation in eaf_data:
            annotation_value = annotation['annotation_text']
            annotation_id = annotation['annotation_id']

            sentences.append(annotation_value)
            annotation_list.append(annotation_id)

        # overwrite job file with a list of annotations
        new_job_data['annotation_list'] = annotation_list
        with open(job_path, 'w') as out_file:
            out_file = json.dump(new_job_data, out_file)

    # Save file, send to the wrapper
    # TODO: save where?
    txt_path = '/data/inputs/fairseq_{}.sents'.format(job_id)
    with open(txt_path, 'w') as outpt:
        for sline in sentences:
            outpt.write(sline + '\n')

    # find task
    if new_job_data['task'] == 'gloss':
        call_glossing_model(txt_path, n_best, '/data/results/output_inference_json-{}.std.out'.format(job_id))
    elif new_job_data['task'] == 'morphseg':
        call_morphseg_model(txt_path, n_best, '/data/results/output_inference_json-{}.std.out'.format(job_id))
