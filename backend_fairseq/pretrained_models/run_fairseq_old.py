from .nbest_model_evaluate_2 import *
from .gloss_utils import *
from time import sleep
from os import remove, path, rename
import subprocess
import re
import json

"""
A python script for running and evaluating the pre-trained Fairseq models.
"""


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


# path: string, path to the text file to preprocess
# n_context: int, context tokens
# returns: list of tuples of (list of strings, list of strings)
def preprocess_file(path, n_context, gloss=False):
    file = [line.rstrip() for line in open(path).readlines()]
    if gloss:
        file = [underlined_to_alt_chars(line) for line in file]
    return [preprocess_line(line, n_context) for line in file]


# path: string, path to the text file to preprocess and pipe
# returns: tuple of (string, string)
def build_morphseg_text_pipe(path):
    examples_1 = preprocess_file(path, 1)
    examples_2 = preprocess_file(path, 2)

    pipe_context1 = ""
    pipe_context2 = ""
    for i in range(len(examples_1)):
        pipe_context1 += '\n'.join(examples_1[i]) + '\n'
        pipe_context2 += '\n'.join(examples_2[i]) + '\n'

    return pipe_context1, pipe_context2


# path: string, path to text representations
# returns: string for piping
def build_gloss_text_pipe(path):
    examples = preprocess_file(path, 1)
    pipe_examples = []
    for line in examples:
        pipe_examples.append('\n'.join(line))

    return '\n'.join(pipe_examples)


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


# examples: string, output of build_input_text_pipe
# preprocess_path: string
# checkpoints: string
# n: int
# returns: string, output of call
def call_interactive(examples, preprocess_path, checkpoints, n):
    call = ["fairseq-interactive", "--path", checkpoints, "--beam", "5", "--nbest", str(n),
            "--source-lang", "src", "--target-lang", "trg", preprocess_path]
    output = subprocess.run(call, input=examples, capture_output=True, text=True)
    # print('stdout: ', output.stdout)
    # print('stderr:', output.stderr)
    return output.stdout


# send the examples to a background process of fairseq-interactive
def pipe_to_model_process(examples: str, last_token: int, in_pipe: str, output_path: str) -> str:
    # print('Examples:', examples)
    with open(in_pipe, 'a') as named_pipe:
        subprocess.run(['echo', examples], stdout=named_pipe)

    # search for the final line of the fairseq-interactive output
    # output_file 
    # while re.search('fairseq_cli.interactive | Total time:',
    #                (output_file := open(output_path, 'r').readlines())[-1]):
    #     sleep(1)
    #     print('same')

    # continue once there are the expected number of examples

    print('Last token:', last_token)
    last_line_not_encountered = True
    while last_line_not_encountered:
        sleep(0.5)
        output_file = open(output_path, 'r').readlines()
        if len(output_file) > 0 and re.search('^P-{}'.format(last_token), output_file[-1]):
            last_line_not_encountered = False

    # make the file blank so that the next process doesn't read this sentence's text
    with open(output_path, 'w') as out:
        out.write('')

    return ''.join(output_file)


# get the lines from the first token to the last
def get_sentence_outputs(output: list, first_token: int, last_token: int):
    sentence_lines = []
    save_flag = False

    for line in output:
        if save_flag:
            sentence_lines.append(line)
            if re.search(f'^P-{last_token+1}', line):
                save_flag = False
        elif re.search(f'S-{first_token}', line):
            sentence_lines.append(line)
            save_flag = True

    return sentence_lines


# return true if there are 4 instances of P-{last_token}
def found_last_example(output: list, last_token: int) -> bool:
    n_match = sum([1 for line in output if re.search(f'^P-{last_token}', line)])
    return n_match == 4


# send the examples to two background processes
def pipe_to_both_model_processes(gloss_examples: str, seg_examples: str, first_token: int, last_token: int, 
                                 gloss_pipe: str, gloss_out: str, seg_pipe: str, seg_out: str) -> tuple:

    # write to the two pipes
    with open(gloss_pipe, 'a') as named_pipe:
        subprocess.run(['echo', gloss_examples], stdout=named_pipe)
    
    with open(seg_pipe, 'a') as named_pipe:
        subprocess.run(['echo', seg_examples], stdout=named_pipe)

    last_gloss_not_seen = True
    last_seg_not_seen = True
    while last_gloss_not_seen or last_seg_not_seen:
        sleep(0.5)
        if last_gloss_not_seen:
            gloss_file = open(gloss_out, 'r').readlines()

            if len(gloss_file) > 0 and found_last_example(gloss_file, last_token):
                last_gloss_not_seen = False

                # make the file blank so the next process doesn't read this text
                with open(gloss_out, 'w') as out:
                    out.write('')
                #gloss_sentence = get_sentence_outputs(gloss_file, first_token, last_token)
        
        if last_seg_not_seen:
            seg_file = open(seg_out, 'r').readlines()
            if len(seg_file) > 0 and found_last_example(seg_file, last_token):
                last_seg_not_seen = False

                with open(seg_out, 'w') as out:
                    out.write('')
                #seg_sentence = get_sentence_outputs(seg_file, first_token, last_token)

    assert len(gloss_file) == len(seg_file)

    return ''.join(gloss_file), ''.join(seg_file)
        

# out_file: list, outputs of multiple fairseq-interactive calls, or list of single call
# n: int, number of best predictions
# returns: list of n-best predictions
def get_output_words(out_file, n):
    if len(out_file) == 1:
        predictions = read_predictions(out_file[0], n, string=True)
        # print('Predictions:', predictions)
        pred_text = [tuple([ex[0] for ex in t]) for t in predictions]
        pred_conf = [tuple([ex[1] for ex in t]) for t in predictions]
        return pred_text, pred_conf
    else:
        predictions = [read_predictions(p, n, string=True) for p in out_file]
        rearranged = get_guess_lists(predictions)
        # print(rearranged)
        pred_text = [scored_majority_vote(t, n) for t in rearranged]
        pred_conf = [[tuple([w[1] for w in t]) for t in p] for p in predictions]
        return pred_text, pred_conf


# predictions: tuple, output of get_output_words
# inputs: list of strings, input to model
# ensemble: bool, if the input contains multiple confidence levels
def format_json(predictions, inputs, task="morphseg"):
    # json_dict = {'predictions':[]}
    # words, confidences = predictions
    # for i in range(len(words)):
    #     word_output = {'input':inputs[i], 'outputs':[]}
    #     for j in range(len(words[i])):
    #         prediction = {'text': re.sub(' ', '', words[i][j])}
    #         if ensemble:
    #             prediction['confidence'] = {'transformer':confidences[0][i][j], 'lstm':confidences[1][i][j]}
    #         else:
    #             prediction['confidence'] = confidences[i][j]
    #         word_output['outputs'].append(prediction)
    #     json_dict['predictions'].append(word_output)
    # return json_dict

    # NEW way: in order to match up with the coling output
    token_list = []
    words, confidences = predictions
    print('Words:', words, len(words))
    print('Inputs:', inputs, len(inputs))
    assert len(words) == len(inputs)
    for i in range(len(words)):
        # input: src token, segmentation: list of n-best sys tokens
        word_dict = {'input':inputs[i], "segmentation":[]}
        for j in range(len(words[i])):
            # remove spaces between characters
            segs = re.sub(' ', '', words[i][j])
            word_dict['segmentation'].append(segs)

        # best of n-best: top of list
        word_dict['preferred_segmentation'] = word_dict['segmentation'][0]
        # no custom segmentations for now
        word_dict['custom_segmentation'] = []
        word_dict['model'] = 'fairseq'
        # make all of the tokens in sentence 1 for now
        word_dict['sentence_id'] = 1
        token_list.append(word_dict)
        # n_best: len of (words[i])
        word_dict['nbest'] = len(words[i])
        # task: morphseg or gloss
        word_dict['task'] = task
        # format: text or elan
    return token_list


# create a dictionary with results for both glossing and segmentation
def format_combined_json(gloss_output: list, morphseg_output: list, inputs: list) -> list:
    token_list = []
    gloss, _ = gloss_output
    seg, _ = morphseg_output
    print('Gloss:', [g[0] for g in gloss], len(gloss))
    print('Seg:', [s[0] for s in seg], len(seg))
    print('Input:', inputs, len(inputs))
    assert len(gloss) == len(inputs) == len(seg)
    assert len(gloss[0]) == len(seg[0])

    for i in range(len(gloss)):
        # input: src token, segmentation: list of n-best seg predictions, gloss: list of n-best gloss predictions
        word_dict = {'input':inputs[i], 'segmentation':[], 'gloss':[]}
        for j in range(len(gloss[i])):
            # remove spaces
            gtok = gloss[i][j].replace(' ', '')
            word_dict['gloss'].append(gtok)
            segtok = seg[i][j].replace(' ', '')
            word_dict['segmentation'].append(segtok)

        # zeroth prediction for both models
        word_dict['preferred_segmentation'] = word_dict['segmentation'][0]
        word_dict['preferred_gloss'] = word_dict['gloss'][0]

        # metadata
        word_dict['custom_segmentation'] = []
        word_dict['model'] = 'fairseq'
        word_dict['nbest'] = len(gloss[i])

        # make every sentence id 1 for now, replaced in a later function
        word_dict['sentence_id'] = 1

        token_list.append(word_dict)
    
    return token_list


# assign a number to each word in the input file (with sentences on every newline)
# use that to give sentence ids to output tokens
def get_sentence_ids(input_file, token_list):
    # print(token_list)
    sents_by_ids = []
    sents = [line.split(' ') for line in open(input_file, 'r').readlines()]
    tokens_w_ids = token_list

    wcount = 0
    for s in sents:
        ids = []
        for t in s:
            ids.append(wcount)
            wcount += 1
        sents_by_ids.append(ids)

    for s in sents_by_ids:
        for i in s:
            tokens_w_ids[i]["sentence_id"] = sents_by_ids.index(s) + 1
    
    return tokens_w_ids


# go through the list of tokens, add a dict value 'annotation id' corresponding to the value in annotation_seq
def get_annotation_ids(token_list: list, annotation_seq: list) -> list:
    tokens_w_annot = token_list
    for i in range(len(token_list)):
        tokens_w_annot[i]["annotation_id"] = annotation_seq[i]

    return tokens_w_annot


def format_inputs(path):
    input_sentences = [line for line in open(path, 'r').readlines()]
    input_tokens = []
    for s in input_sentences:
        for t in s.split(' '):
            input_tokens.append(t)
    return input_tokens


# def call_single_model(path, arch, n):
#     input = build_input_text_pipe(path)
#     if arch == 'transformer':
#         input = input[0]
#         preprocess = "/backend_fairseq/pretrained_models/data/transformer/transformer_preprocess"
#         checkpoint = '/backend_fairseq/pretrained_models/data/transformer/checkpoint_best.pt'
#     elif arch == 'lstm':
#         input = input[1]
#         preprocess = "/backend_fairseq/pretrained_models/data/lstm/lstm_preprocess"
#         checkpoint = "/backend_fairseq/pretrained_models/data/lstm/checkpoint_best.pt"
#     else:
#         raise ValueError("Unrecognized architecture.")

#     output = call_interactive(input, preprocess, checkpoint, n)
#     return get_output_words([output], n)


# def call_random_model(path, arch, n):
#     input = build_input_text_pipe(path)
#     if arch == "transformer":
#         input = input[0]
#         preprocess = "data/transformer/transformer_preprocess"
#         checkpoints = ["data/transformer/{}_best.pt".format(i) for i in range(1, 11)]
#     elif arch == "lstm":
#         input = input[1]
#         preprocess = "data/lstm/lstm_preprocess"
#         checkpoints = ["data/lstm/{}_best.pt".format(i) for i in range(1, 11)]
#     else:
#         raise ValueError("Unrecognized architecture.")

#     outputs = []
#     for c in checkpoints:
#         print('Calling {} of {}'.format(checkpoints.index(c) + 1, len(checkpoints)))
#         outputs.append(call_interactive(input, preprocess, c, n))
#     return get_output_words(outputs, n)


def call_morphseg_model(path, n, out_path, annotations=None):
    input = build_morphseg_text_pipe(path)

    preprocess_transf = "/backend_fairseq/pretrained_models/data/morphseg/transformer/transformer_preprocess"
    checkpoint_transf = "/backend_fairseq/pretrained_models/data/morphseg/transformer/checkpoint_best.pt"

    preprocess_lstm = "/backend_fairseq/pretrained_models/data/morphseg/lstm/lstm_preprocess"
    checkpoint_lstm = "/backend_fairseq/pretrained_models/data/morphseg/lstm/checkpoint_best.pt"

    outputs = [call_interactive(input[0], preprocess_transf, checkpoint_transf, n),
               call_interactive(input[1], preprocess_lstm, checkpoint_lstm, n)]

    wordlist = get_output_words(outputs, n)
    token_list = format_json(wordlist, format_inputs(path))
    token_list = get_sentence_ids(path, token_list)
    jobject = json.dumps(token_list, indent=4)
    with open(out_path, 'w') as out_json:
        out_json.write(jobject)


def call_glossing_model(path, n, out_path, annotations=None):
    print(annotations)

    input = build_gloss_text_pipe(path)

    preprocess = "/backend_fairseq/pretrained_models/data/gloss/gloss_preprocess"
    checkpoint = "/backend_fairseq/pretrained_models/data/gloss/checkpoint_best.pt"

    output = call_interactive(input, preprocess, checkpoint, n)
    output_cleaned = [alt_to_underline_chars(output)]

    wordlist = get_output_words(output_cleaned, n)
    token_list = format_json(wordlist, format_inputs(path), task='gloss')
    token_list = get_sentence_ids(path, token_list)
    if annotations:
        token_list = get_annotation_ids(token_list, annotations)
    jobject = json.dumps(token_list, indent=4)
    with open(out_path, 'w') as out_json:
        out_json.write(jobject)


# submit text to the background process of fairseq_interactive
def submit_glossing_text(sent: str, last_token: int, n: int, sent_id: int, out_path: str, annotation_id=None) -> None:
    input = sentence_to_gloss_input(sent)
    in_pipe = '/backend_fairseq/pretrained_models/io/pipes/glossPipe'
    temp_file = '/backend_fairseq/pretrained_models/io/outputs/gloss_out.txt'

    output = pipe_to_model_process(input, last_token, in_pipe, temp_file)
    print('Output:', output)
    output_cleaned = [alt_to_underline_chars(output)]

    save_single_pipe_output(output_cleaned, sent, n, sent_id, out_path, 'gloss', annotation_id)


# submit text to the background segmentation process
def sumbit_morphseg_text(sent: str, last_token: int, n: int, sent_id: int, out_path: str, annotation_id=None) -> None:
    input = sentence_to_seg_input(sent)
    in_pipe = '/backend_fairseq/pretrained_models/io/pipes/morphSegPipe'
    temp_file = '/backend_fairseq/pretrained_models/io/outputs/morph_seg_out.txt'

    output = [pipe_to_model_process(input, last_token, in_pipe, temp_file)]
    print('Output:', output)

    save_single_pipe_output(output, sent, n, sent_id, out_path, 'morphSeg', annotation_id)


# submit text to both the glossing and segmentation processes, save to one JSON
def submit_text(sent: str, first_token: int, last_token: int, n: int, sent_id: int, out_path: str, annotation_id=None) -> None:
    gloss_in = sentence_to_gloss_input(sent)
    seg_in = sentence_to_seg_input(sent)

    in_folder = '/backend_fairseq/pretrained_models/io'
    gloss_pipe = path.join(in_folder, 'pipes/glossPipe')
    seg_pipe = path.join(in_folder, 'pipes/morphSegPipe')
    gloss_out = path.join(in_folder, 'outputs/gloss_out.txt')
    seg_out = path.join(in_folder, 'outputs/morph_seg_out.txt')

    gloss_output, seg_output = pipe_to_both_model_processes(gloss_in, seg_in, first_token, last_token, gloss_pipe, gloss_out, seg_pipe, seg_out)
    gloss_output = [alt_to_underline_chars(gloss_output)]
    seg_output = [seg_output]

    save_both_pipe_output(gloss_output, seg_output, sent, n, sent_id, out_path, annotation_id)


# convert pipe output into a saveable JSON file
def save_single_pipe_output(output: list, raw_sent: str, n: int, sent_id: int, out_path: str, task: str, annotation_id=None) -> None:
    wordlist = get_output_words(output, n)
    token_list = format_json(wordlist, raw_sent.split(' '), task=task)
    
    save_pipe_output(token_list, sent_id, out_path, annotation_id)


# convert two pipe outputs into a saveable JSON file
def save_both_pipe_output(gloss_out: list, seg_out: list, raw_sent: str, n: int, sent_id: int, out_path: str, annotation_id=None) -> None:
    gloss_list = get_output_words(gloss_out, n)
    seg_list = get_output_words(seg_out, n)
    token_list = format_combined_json(gloss_list, seg_list, raw_sent.split(' '))

    save_pipe_output(token_list, sent_id, out_path, annotation_id)


def save_pipe_output(token_list: list, sent_id: int, out_path: str, annotation_id=None) -> None:
    for w in token_list:
        w['sentence_id'] = sent_id

    if annotation_id:
        for w in token_list:
            w['annotation_id'] = annotation_id

    jobject = json.dumps(token_list, indent=4)
    with open(out_path, 'w') as out_json:
        out_json.write(jobject)


# Next step: call input text on both models at the same time.
# We'll have the interactive models listen in on the same pipe, and save output to different text files
# Have one saved JSON file  of the form:
"""
{
    [
        {
            input: str, input token
            segmentation: [list of n-best morphseg predictions]
            preferred_segmentation: prediction 0
            custom_segmentation: []
            gloss: [list of n-best gloss predictions]
            preferred_gloss: prediction 0
            custom_gloss = []
            sentence_id: int
            annotation_id: string
            n_best: int
        }
    ]
}
"""


if __name__ == "__main__":
    # inputs = format_inputs('text_file')
    # model_outputs = call_default_model('text_file', 4)

    # with open('test.json', 'w') as jfile:
    #     json.dump(format_json(model_outputs, inputs, True), jfile)

    """
    {
        input token:
        output tokens: {
                {
                text:
                confidence:
                }
            }
        }
    }
    """

    pass