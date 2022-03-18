"""
Passes a job through Fairseq.

Creates a job_id.dev file, which is passed to the Python wrapper for the pre-trained models.
"""

from __future__ import annotations
import json, re
import os
import subprocess
import cProfile
from time import sleep, time
from pretrained_models.run_fairseq import *


class FairseqSubmitter:
    """
    Submit jobs to the background process of fairseq-interactive.
    Keeps track of the number of examples seen by fairseq-interactive so far.
    """

    def __init__(self):
        self.first_example = 0
        self.last_example = -1

    def process_text_sentence_batch(self, data):
        """
        Split the job into separate sentences, and send each of them to the background fairseq process
        """

        # model options
        jobid = data['id']
        n_best = int(data['nbest'])
        n_sentences = data['n_sentences']
        sentences = data['text']

        getSeg = data['getSeg']
        getGloss = data['getGloss']
        assert getSeg or getGloss

        # init the subprocess
        if getSeg:
            stail, seg = init_fairseq_model('seg', n_best)
        if getGloss:
            gtail, gloss = init_fairseq_model('gloss', n_best)

        for i in range(n_sentences):
            sentence = sentences[i]
            print(sentence)
            n_tokens = len(sentence.split(' '))
            save_path = f'/data/results/sentence_{jobid}_{i}.std.out'

            self.last_example += n_tokens
            submit_sentence(sentence, i, getSeg, getGloss, self.first_example, self.last_example, n_best, save_path)
            self.first_example += n_tokens

        # found_sentences = 0
        # # while found_sentences < n_sentences:
        # #     sentence, i, first, last, nbest, path = sentence_dict[found_sentences]
        # #     if get_sentence(sentence, i, first, last, nbest, path):
        # #         found_sentences += 1
        # out_path = '/backend_fairseq/pretrained_models/io/outputs/gloss_out.txt'
        # out_file = open(out_path, 'r')
        # out_file.seek(0,2)
        # out_str = ''
        # while found_sentences < n_sentences:
        #     line = out_file.readline()
        #     if line:
        #         out_str += line
        #         sentence, i, first, last, nbest, path = sentence_dict[found_sentences]
        #         if get_sentence(sentence, out_str, i, first, last, nbest, path):
        #             found_sentences += 1
        #     else:
        #         sleep(0.01)

        #out, err = gloss.communicate()

        if getSeg:
            seg.terminate()
            stail.terminate()
        if getGloss:
            gloss.terminate()
            gtail.terminate()
            
        self.first_example = 0
        self.last_example = -1

    def process_elan_annotation_batch(self, data):
        """
        Send each annotation as its own job
        """

        # model options
        jobid = data['id']
        n_best = int(data['nbest'])
        annot = data['eaf_data']

        getSeg = data['getSeg']
        getGloss = data['getGloss']
        assert getSeg or getGloss

        # init the subprocess
        if getSeg:
            stail, seg = init_fairseq_model('seg', n_best)
        if getGloss:
            gtail, gloss = init_fairseq_model('gloss', n_best)

        for i in range(len(annot)):
            text = annot[i]['annotation_text']
            n_tokens = len(text.split(' '))
            id = annot[i]['annotation_id']

            save_path = f'/data/results/sentence_{jobid}_{i}.std.out'
            self.last_example += n_tokens
            submit_sentence(text, i, getSeg, getGloss, self.first_example, self.last_example, n_best, save_path, annotation_id=id)
            self.first_example += n_tokens

        if getSeg:
            stail.terminate()
            seg.terminate()
        if getGloss:
            gtail.terminate()
            gloss.terminate()
            
        self.first_example = 0
        self.last_example = -1

    def process_batch(self, job_id):
        """
        Loads a job file from the server, and sends to the model
        """

        # get the JSON contents
        job_path = '/data/inputs/fairseq_{}.txt'.format(job_id)
        with open(job_path, 'r') as new_job:
            new_job_contents = new_job.read()
        new_job_data = json.loads(new_job_contents)

        # process based on input type
        in_type = new_job_data['input_type']
        if in_type == 'text':
            start = time()
            
            self.process_text_sentence_batch(new_job_data)

            #cProfile.run('self.process_text_sentence_batch(new_job_data)')
            end = time()
            print('Time elapsed:', end-start)
        elif in_type == "eaf_file":
            self.process_elan_annotation_batch(new_job_data)


# def process_file(job_id):
#     """
#     Converts a job json file into an input for the model wrapper.
#     Passes it to the model.
#     """

#     # TODO: just write the files to backend_fairseq for now
#     job_path = '/data/inputs/fairseq_{}.txt'.format(job_id)
#     with open(job_path, 'r') as new_job:
#         new_job_contents = new_job.read()

#     new_job_data = json.loads(new_job_contents)

#     # TODO: Debug
#     print(new_job_data)

#     # check for options
#     n_best = int(new_job_data['nbest'])

#     if new_job_data['input_type'] == 'text':
#         text_input = new_job_data['text']

#         # convert text stream into a list of sentences
#         sentences = []
#         txt_lines = re.split('\n', text_input)
#         for txtl in txt_lines:
#             sent_lines = re.split('[.!?] ', txtl)
#             for sl in sent_lines:
#                 sentences.append(sl)

#         annotation_seq = None

#     elif new_job_data['input_type'] == 'eaf_file':
#         eaf_data = new_job_data['eaf_data']

#         # each annotation is considered a sentence
#         sentences = []
#         annotation_list = []
#         annotation_seq = []
#         for annotation in eaf_data:
#             annotation_value = annotation['annotation_text']
#             annotation_id = annotation['annotation_id']
#             sentences.append(annotation_value)

#             # repeat the annotation value for each word, align in run_fairseq.py
#             for i in range(len(annotation_value.split(' '))):
#                 annotation_seq.append(annotation_id)
            
#             annotation_list.append(annotation_id)

#         # overwrite job file with a list of annotations
#         new_job_data['annotation_list'] = annotation_list
#         with open(job_path, 'w') as out_file:
#             out_file = json.dump(new_job_data, out_file)
        
#     # Save file, send to the wrapper
#     # TODO: save where?
#     txt_path = '/data/inputs/fairseq_{}.sents'.format(job_id)
#     with open(txt_path, 'w') as outpt:
#         for sline in sentences:
#             outpt.write(sline + '\n')

#     # find task
#     if new_job_data['task'] == 'gloss':
#         call_glossing_model(txt_path, n_best, '/data/results/output_inference_json-{}.std.out'.format(job_id), annotations=annotation_seq)
#         # submit_glossing_text(txt_path, n_best, '/data/results/output_inference_json-{}.std.out'.format(job_id), annotations=annotation_seq)
#         # print('Processing ', txt_path)
#     elif new_job_data['task'] == 'morphseg':
#         call_morphseg_model(txt_path, n_best, '/data/results/output_inference_json-{}.std.out'.format(job_id), annotations=annotation_seq)
