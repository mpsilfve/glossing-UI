from .nbest_model_evaluate_2 import *
from .gloss_utils import *
from os import path
from time import sleep
import os
import sys
import subprocess
import json


"""*******************************************************************
                  Preprocessing helper functions
*******************************************************************"""

# sentence: string, a line from an input file.
# n_context: int, the number of tokens on either side of the target
# returns: list of string examples
def preprocess_line(sentence, n_context):
    pad_s = ['<S>' for i in range(n_context)]
    pad_e = ['<E>' for i in range(n_context)]
    padded_tokens = pad_s + sentence.split(' ') + pad_e

    context_tokens = []
    for i in range(n_context, len(padded_tokens) - n_context):
        # get target token and two neighbors on either side
        context = padded_tokens[i-n_context:i+n_context+1]
        preprocessed = []
        for t in context:
            if t == '<S>' or t == '<E>':
                preprocessed.append(t)
            else:
                preprocessed.append(' '.join(list(t)))
        # add examples to collectors
        context_tokens.append(' _ '.join(preprocessed))

    return context_tokens


# convert a string into a list of examples, with a context window of 1
# convert the underline characters so that the glossing model can handle them
def sentence_to_gloss_input(sent):
    to_alt = underlined_to_alt_chars(sent)
    examples = preprocess_line(to_alt, 1)
    return '\n'.join(examples)


# convert a string into a list of examples, with a context window of 2
def sentence_to_seg_input(sent):
    examples = preprocess_line(sent, 2)
    return '\n'.join(examples)


"""*******************************************************************
                  JSON saving helper functions
*******************************************************************"""

def get_output_tokens(sentence: str, model_out: str, nbest: int) -> dict:
    inputs = sentence.split(' ')
    outputs = read_predictions(model_out, nbest, string=True)
    tokens = []
    for i in range(len(inputs)):
        predictions = [p[0].replace(' ', '') for p in outputs[i]]
        tokens.append((inputs[i], predictions))
    return tokens


def get_token_result_dict(input: str, sentence_id: int, nbest: int, gloss_res=None, 
                          seg_res=None, annotation_id=None):

    assert gloss_res or seg_res
    token_dict = {}
    token_dict['input'] = input
    token_dict['sentence_id'] = sentence_id
    token_dict['nbest'] = nbest

    if seg_res:
        token_dict['segmentation'] = seg_res
        token_dict['preferred_segmentation'] = seg_res[0]
        token_dict['custom_segmentation'] = []

    if gloss_res:
        token_dict['gloss'] = gloss_res
        token_dict['preferred_gloss'] = gloss_res[0]
        token_dict['custom_gloss'] = []

        # token_dict['segmentation'] = ['a', 'b', 'c', 'd']
        # token_dict['preferred_segmentation'] = 'DEBUG'
        # token_dict['custom_segmentation'] = []

    if annotation_id:
        token_dict['annotation_id'] = annotation_id

    return token_dict


def get_gloss_results(sentence: str, output: str, sentence_id: int, nbest:int, annotation_id=None):
    output_cleaned = alt_to_underline_chars(output)
    sentence_res = get_output_tokens(sentence, output_cleaned, nbest)
    result_dict = []

    for token, predictions in sentence_res:
        result_dict.append(get_token_result_dict(token, sentence_id, nbest, 
                                                                gloss_res=predictions, 
                                                                annotation_id=annotation_id))

    return result_dict


def get_seg_results(sentence: str, output: str, sentence_id: int, nbest:int, annotation_id=None):
    sentence_res = get_output_tokens(sentence, output, nbest)
    result_dict = []

    for token, predictions in sentence_res:
        result_dict.append(get_token_result_dict(token, sentence_id, nbest, 
                                                                seg_res=predictions, 
                                                                annotation_id=annotation_id))

    return result_dict


def get_both_results(sentence: str, seg: str, gloss: str, sentence_id: int, nbest:int, annotation_id=None):
    seg_list = get_output_tokens(sentence, seg, nbest)
    gloss_list = get_output_tokens(sentence, alt_to_underline_chars(gloss), nbest)
    assert len(seg_list) == len(gloss_list)

    results = []

    for i in range(len(seg_list)):
        token, seg_predictions = seg_list[i]
        _, gloss_predictions = gloss_list[i]
        results.append(get_token_result_dict(token, sentence_id, nbest, 
                                                                seg_res=seg_predictions,
                                                                gloss_res=gloss_predictions,
                                                                annotation_id=annotation_id))

    return results


def save_predictions(results: dict, path: str):
    jobject = json.dumps(results, indent=4)
    with open(path, 'w') as out_json:
        out_json.write(jobject)


"""*******************************************************************
                  Subprocess helper functions
*******************************************************************"""


def init_fairseq_model(task: str, nbest: int) -> str:
    data_path = path.join("/backend_fairseq", "pretrained_models", "data")
    io_path = path.join('/backend_fairseq', 'pretrained_models', 'io')

    if task == 'seg':
        pipe_path = path.join(io_path, 'pipes', 'morphSegPipe')
        out_path = path.join(io_path, 'outputs', 'morph_seg_out.txt')
        checkpoint_path = path.join(data_path, "morphseg", "lstm", "checkpoint_best.pt")
        preprocess = path.join(data_path, "morphseg", "lstm", "lstm_preprocess")
    elif task == "gloss":
        pipe_path = path.join(io_path, 'pipes', 'glossPipe')
        out_path = path.join(io_path, 'outputs', 'gloss_out.txt')
        checkpoint_path = path.join(data_path, "gloss", "checkpoint_best.pt")
        preprocess = path.join(data_path, "gloss", "gloss_preprocess")
    else:
        raise ValueError("Invalid task.")

    tail_input = subprocess.Popen(["tail", "-f", pipe_path], stdout=subprocess.PIPE)
    args = ["fairseq-interactive", "--path", checkpoint_path, "--beam", "5", "--nbest", str(nbest),
            "--source-lang", "src", "--target-lang", "trg", preprocess]
    fairseq_call = subprocess.Popen(args, bufsize=1, stdin=tail_input.stdout,
                                    stdout=open(out_path, 'w'))

    # job = subprocess.run(['sh', path.join(io_path, 'pipes', 'init_model.sh'), 
    #                      pipe_path, checkpoint_path, str(nbest), preprocess, out_path], capture_output=True)
    # print(job.stdout)
    # print('Made it?')
    return tail_input, fairseq_call


# get lines from first-token to last-token
def get_sentence_lines(lines: list, first_token: int, last_token: int):
    sentence_lines = []

    collecting_flag = False
    for line in lines:
        if re.search(f'^S-{last_token+1}\s', line):
            collecting_flag = False
        elif re.search(f'^S-{first_token}\s', line):
            collecting_flag = True

        if collecting_flag:
            sentence_lines.append(line)

    return sentence_lines


# return the output if the last token of the sentence has been processed, otherwise return false
def read_lines_so_far(out_path: str, first_token: int, last_token: int, nbest: int):
    lines = open(out_path, 'r').readlines()
    if len(lines) > 0:
        # see if the final prediction has appeared $n_best times
        n_match = sum([1 for line in lines if re.search(f'^P-{last_token}\s', line)])
        if n_match == nbest:
            return get_sentence_lines(lines, first_token, last_token)

    return False


def handle_single_pipe(sentence: str, task: str, first_token: int, last_token: int, nbest: int, pipe_path: str, out_path: str) -> str:
    if task == 'seg':
        pipe_input = sentence_to_seg_input(sentence)
    else:
        pipe_input = sentence_to_gloss_input(sentence)

    with open(pipe_path, 'a') as pipe:
        subprocess.run(['echo', pipe_input], stdout=pipe)

    last_ex_not_seen = True
    while last_ex_not_seen:
        ex_output = read_lines_so_far(out_path, first_token, last_token, nbest)
        if ex_output:
            last_ex_not_seen = False
            # with open(out_path, 'w') as out:
            #     out.write('')

    return ''.join(ex_output)


def handle_pipes(sentence: str, first_token: int, last_token: int, nbest: int, seg_pipe_path: str, seg_out_path: str,
                 gloss_pipe_path: str, gloss_out_path: str) -> tuple:

    seg_input = sentence_to_seg_input(sentence)
    gloss_input = sentence_to_gloss_input(sentence)

    with open(seg_pipe_path, 'a') as pipe:
        subprocess.run(['echo', seg_input], stdout=pipe)
    with open(gloss_pipe_path, 'a') as pipe:
        subprocess.run(['echo', gloss_input], stdout=pipe)

    last_seg_not_seen = True
    last_gloss_not_seen = True

    while last_seg_not_seen or last_gloss_not_seen:
        if last_seg_not_seen:
            seg_output = read_lines_so_far(seg_out_path, first_token, last_token, nbest)

            if seg_output:
                last_seg_not_seen = False
                # with open(seg_out_path, 'w') as out:
                #     out.write('')

        if last_gloss_not_seen:
            gloss_output = read_lines_so_far(gloss_out_path, first_token, last_token, nbest)

            if gloss_output:
                last_gloss_not_seen = False
                # with open(gloss_out_path, 'w') as out:
                #     out.write('')

    print(seg_output[-1], len(seg_output), gloss_output[-1], len(gloss_output))
    #assert len(seg_output) == len(gloss_output)
    return ''.join(seg_output), ''.join(gloss_output)


def submit_sentence(sentence: str, id: int, get_seg: bool, get_gloss: bool, 
                    first_token: int, last_token: int, nbest: int, save_path: str,
                    annotation_id=None) -> None:

    root_dir = path.join('/backend_fairseq', 'pretrained_models', 'io')
    if get_seg:
        seg_pipe_path = path.join(root_dir, 'pipes', 'morphSegPipe')
        seg_out_path = path.join(root_dir, 'outputs', 'morph_seg_out.txt')
    if get_gloss:
        gloss_pipe_path = path.join(root_dir, 'pipes', 'glossPipe')
        gloss_out_path = path.join(root_dir, 'outputs', 'gloss_out.txt')

    if get_seg and get_gloss:
        seg_out, gloss_out = handle_pipes(sentence, first_token, last_token, nbest, seg_pipe_path, seg_out_path, 
                                          gloss_pipe_path, gloss_out_path)

        # print('Seg', get_output_tokens(sentence, seg_out, nbest), len(get_output_tokens(sentence, seg_out, nbest)))
        # print('Gloss', get_output_tokens(sentence, gloss_out, nbest), len(get_output_tokens(sentence, gloss_out, nbest)))
        outputs = get_both_results(sentence, seg_out, gloss_out, id, nbest, annotation_id=annotation_id)
        print('Both predictions:', outputs)
        save_predictions(outputs, save_path)
    elif get_seg:
        seg_out = handle_single_pipe(sentence, 'seg', first_token, last_token, nbest, seg_pipe_path, seg_out_path)
        outputs = get_seg_results(sentence, seg_out, id, nbest, annotation_id=annotation_id)
        print('Seg predictions:', outputs)
        save_predictions(outputs, save_path)
    else:
        gloss_out = handle_single_pipe(sentence, 'gloss', first_token, last_token, nbest, gloss_pipe_path, gloss_out_path)
        outputs = get_gloss_results(sentence, gloss_out, id, nbest, annotation_id=annotation_id)
        print('Gloss predictions:', outputs)
        save_predictions(outputs, save_path)


def get_sentence(sentence: str, out_str: str, id: int, first_token: int, last_token: int, nbest: int, save_path: str):
    # if gout.stdout:
    #     print(gout.stdout)
    # outs = open('/backend_fairseq/pretrained_models/io/outputs/gloss_out.txt', 'r').read()
    # if re.search(f'S-{last_token}\s', outs):
    #     print('Found sentence', id)
    #     return True
    # sentence_output = read_lines_so_far('/backend_fairseq/pretrained_models/io/outputs/gloss_out.txt', first_token, last_token, nbest)
    # if sentence_output:
    #     outputs = get_gloss_results(sentence, ''.join(sentence_output), id, nbest)
    #     print(outputs)
    #     save_predictions(outputs, save_path)
    #     return True
    #print(gout.stdout)
    #print(gout.stdout.read())

    return True
   
    sent_output = read_lines_so_far(out_str, first_token, last_token, nbest)
    if sent_output:
        outputs = get_gloss_results(sentence, '\n'.join(sent_output), id, nbest)
        save_predictions(outputs, save_path)
        return True

    return False
