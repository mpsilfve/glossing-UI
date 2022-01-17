from .nbest_model_evaluate_2 import *
import argparse
import subprocess
import re
import json

"""
A python script for running and evaluating the pre-trained Fairseq models.
"""


# sentence: string, a line from an input file.
# returns: tuple of (list of strings, list of strings)
def preprocess_line(sentence):
    padded_tokens = ['<S>', '<S>'] + sentence.split() + ['<E>', '<E>']

    context_1 = []
    context_2 = []
    for i in range(2, len(padded_tokens) - 2):
        # get target token and two neighbors on either side
        context = padded_tokens[i-2:i+3]
        preprocessed = []
        for t in context:
            if t == '<S>' or t == '<E>':
                preprocessed.append(t)
            else:
                preprocessed.append(' '.join(list(t)))
        # add examples to collectors
        context_1.append(' _ '.join(preprocessed[1:-1]))
        context_2.append(' _ '.join(preprocessed))
    return context_1, context_2


# path: string, path to the text file to preprocess
# returns: list of tuples of (list of strings, list of strings)
def preprocess_file(path):
    file = [line.rstrip() for line in open(path).readlines()]
    return [preprocess_line(line) for line in file]


# path: string, path to the text file to preprocess and pipe
# returns: tuple of (string, string)
def build_input_text_pipe(path):
    examples = preprocess_file(path)

    pipe_context1 = ""
    pipe_context2 = ""
    for line in examples:
        pipe_context1 += '\n'.join(line[0]) + '\n'
        pipe_context2 += '\n'.join(line[1]) + '\n'

    return pipe_context1, pipe_context2


# examples: string, output of build_input_text_pipe
# preprocess_path: string
# checkpoints: string
# n: int
# returns: string, output of call
def call_interactive(examples, preprocess_path, checkpoints, n):
    call = ["fairseq-interactive", "--path", checkpoints, "--beam", "5", "--nbest", str(n),
            "--source-lang", "src", "--target-lang", "trg", preprocess_path]
    output = subprocess.run(call, input=examples, capture_output=True, text=True)
    print('stdout: ', output.stdout)
    print('stderr:', output.stderr)
    return output.stdout


# out_file: list, outputs of multiple fairseq-interactive calls, or list of single call
# n: int, number of best predictions
# returns: list of n-best predictions
def get_output_words(out_file, n):
    if len(out_file) == 1:
        predictions = read_predictions(out_file[0], n, string=True)
        pred_text = [tuple([w[0] for w in t]) for t in predictions]
        pred_conf = [tuple([w[1] for w in t]) for t in predictions]
        return pred_text, pred_conf
    else:
        predictions = [read_predictions(p, n, string=True) for p in out_file]
        rearranged = get_guess_lists(predictions)
        pred_text = [scored_majority_vote(t, 4) for t in rearranged]
        pred_conf = [[tuple([w[1] for w in t]) for t in p] for p in predictions]
        return pred_text, pred_conf


# predictions: tuple, output of get_output_words
# inputs: list of strings, input to model
# ensemble: bool, if the input contains multiple confidence levels
def format_json(predictions, inputs, ensemble):
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
    return token_list


# assign a number to each word in the input file (with sentences on every newline)
# use that to give sentence ids to output tokens
def get_sentence_ids(input_file, token_list):
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



def format_inputs(path):
    input_sentences = [line for line in open(path, 'r').readlines()]
    input_tokens = []
    for s in input_sentences:
        for t in s.split(' '):
            input_tokens.append(t)
    return input_tokens


def call_single_model(path, arch, n):
    input = build_input_text_pipe(path)
    if arch == 'transformer':
        input = input[0]
        preprocess = "/backend_fairseq/pretrained_models/data/transformer/transformer_preprocess"
        checkpoint = '/backend_fairseq/pretrained_models/data/transformer/checkpoint_best.pt'
    elif arch == 'lstm':
        input = input[1]
        preprocess = "/backend_fairseq/pretrained_models/data/lstm/lstm_preprocess"
        checkpoint = "/backend_fairseq/pretrained_models/data/lstm/checkpoint_best.pt"
    else:
        raise ValueError("Unrecognized architecture.")

    output = call_interactive(input, preprocess, checkpoint, n)
    return get_output_words([output], n)


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


def call_default_model(path, n, out_path):
    input = build_input_text_pipe(path)

    preprocess_transf = "/backend_fairseq/pretrained_models/data/transformer/transformer_preprocess"
    checkpoint_transf = "/backend_fairseq/pretrained_models/data/transformer/checkpoint_best.pt"

    preprocess_lstm = "/backend_fairseq/pretrained_models/data/lstm/lstm_preprocess"
    checkpoint_lstm = "/backend_fairseq/pretrained_models/data/lstm/checkpoint_best.pt"

    outputs = [call_interactive(input[0], preprocess_transf, checkpoint_transf, n),
               call_interactive(input[1], preprocess_lstm, checkpoint_lstm, n)]

    wordlist = get_output_words(outputs, n)
    token_list = format_json(wordlist, format_inputs(path), True)
    token_list = get_sentence_ids(path, token_list)
    jobject = json.dumps(token_list, indent=4)
    with open(out_path, 'w') as out_json:
        out_json.write(jobject)

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