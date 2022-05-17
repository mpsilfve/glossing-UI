import math
import re

"""
Tools for evaluating a Fariseq output with recall@n
"""


def read_targets(path):
    # Read a target file and capture every line
    return [line for line in open(path).readlines()]


def read_predictions(path, nbest, string=False):
    # get the n-best predictions from a file, clean Fairseq formatting
    if string:
        pred_file = re.split('\n', path)
    else:
        pred_file = [line for line in open(path).readlines()]
    hypotheses = []
    for i in range(len(pred_file)):
        hypothesis = re.search('^H-', pred_file[i])
        if hypothesis:
            # Collect the prediction scores
            score = float(re.search(r'-?\d*\.\d*', pred_file[i]).group())
            hypotheses.append((re.sub(r'H-\d\d?\d?\d?[ \t]-?\d*\.\d*\t', '', pred_file[i]), score))

    return create_tuples(hypotheses, nbest)


def create_tuples(results, nbest):
    # take a list of predictions and divide into a list of tuples of nbest
    # results_indv is list of strings, nbest is int
    # if nbest == 1:
    #     return results

    divide_by_nbest = []
    grouper = []
    for i in range(len(results)):
        grouper.append(results[i])
        if (i+1) % nbest == 0:
            divide_by_nbest.append(tuple(grouper))
            grouper = []

    return divide_by_nbest


def recall_at_n(sys, golds, raw_n=False, verbose=False):
    # returns the accuracy of a model with n choices: sys is a list of tuples, golds is a list of strings,
    # total number of times the model was correct with one of its predictions divided by total number of gold words/sentences
    # if raw_n = True, returns a tuple of recall and # of correct word forms

    assert len(sys) == len(golds)

    n_correct = 0
    if type(sys[0]) == tuple:
        for i in range(len(golds)):
            # predicts = [s[0] for s in sys[i]]
            if golds[i] in sys[i]:
                n_correct += 1
            elif verbose:
                print('GOLD:', golds[i])
                print('SYS:', sys[i])
                print()
    else:
        for i in range(len(golds)):
            if golds[i] == sys[i][0]:
                n_correct += 1
            elif verbose:
                print('GOLD:', golds[i])
                print('SYS:', sys[i][0])
                print()

    if raw_n:
        return n_correct / len(golds), n_correct
    else:
        return n_correct / len(golds)


# def normalized_ed(sys, gold):
#     # ED(sys, gold) / len(gold)
#     return edit_distance(sys, gold) / len(gold)


# def avg_normalized_ed(sys, golds):
#     # return the average normalized edit distance of the entire dataset
#     # for results_indv with n choices, the smallest edit distance of the n hypotheses is used
#     assert len(sys) == len(golds)

#     total_min_neds = 0

#     for i in range(len(golds)):
#         if type(sys[i]) == tuple:
#             min_ned = min([normalized_ed(s[0], golds[i]) for s in sys[i]])
#         else:
#             min_ned = normalized_ed(sys[i][0], golds[i])
#         total_min_neds += min_ned

#     return total_min_neds / len(golds)


# def avg_ed(sys, golds):
#     # return the average edit distance, not accounting for length
#     # for results_indv with n choices, the smallest edit distance of the n hypotheses is used
#     assert len(sys) == len(golds)

#     total_min_eds = 0

#     for i in range(len(golds)):
#         if type(sys[i]) == tuple:
#             min_ed = min([edit_distance(s[0], golds[i]) for s in sys[i]])
#         else:
#             min_ed = edit_distance(sys[i][0], golds[i])
#         total_min_eds += min_ed

#     return total_min_eds / len(golds)


def divide_by_word(elem, is_type_char):
    # divide a single line by words, depending on the type
    # is_type_char is a bool: True if using char-line dataset, False if using lc-line
    if is_type_char:
        return elem.split(' _ ')
    else:
        return elem.split(' ')


def n_correct_words(sys_elem, gold_elem, is_type_char):
    # for the line-based models. is_type_char is a bool for the dataset type
    sys_words = list(set(divide_by_word(sys_elem, is_type_char)))
    gold_words = list(set(divide_by_word(gold_elem, is_type_char)))

    n_correct =  sum([1 for word in sys_words if word in gold_words])
    return n_correct


def avg_from_words(sys, golds, is_type_char):
    # evaluate the accuracy based on how many of the total words from a line the model correctly predicted
    assert len(sys) == len(golds)

    total_percentages = 0
    # total_words = 0
    for i in range(len(golds)):
        num_words = len(divide_by_word(golds[i], is_type_char))
        # total_words += num_words
        if type(sys[i]) == tuple:
            n_predictions = [n_correct_words(pred[0], golds[i], is_type_char) for pred in sys[i]]
            total_percentages += max(n_predictions) / num_words
        else:
            correct_n = n_correct_words(sys[i][0], golds[i], is_type_char)
            total_percentages += correct_n / num_words

    return total_percentages / len(golds)


def get_guess_lists(all_preds):
    # re-arrange the initializations' predictions
    rearranged = []
    for i in range(len(all_preds[0])):
        rearranged.append([p[i] for p in all_preds])
    return rearranged


def scored_majority_vote(inits_sys, k):
    # from a group of predictions, find the k predictions with the highest scores

    sys = []
    for s in inits_sys:
        sys += s

    scores_dict = {}
    for s in sys:
        print('S:', inits_sys)
        if s[0] in scores_dict:
            scores_dict[s[0]] += math.exp(s[1])
        else:
            scores_dict[s[0]] = math.exp(s[1])

    sorted_scores = sorted(scores_dict, key=scores_dict.get, reverse=True)
    return tuple(sorted_scores[:k])
