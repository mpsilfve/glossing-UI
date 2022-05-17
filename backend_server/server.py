""" Flask-based back end server

Allows for receiving and sending data from and to front-end
"""
from unittest import result
import flask, sys, json
from datetime import datetime
from flask import request, jsonify
import re
import os
import subprocess
from os import path
from glob import glob
from copy import deepcopy
from time import sleep
from .xml_parsing.parsing import parseTierWithTime, writeEafTier


app = flask.Flask(__name__) # create the Flask application object 
app.config["DEBUG"] = True # in debugger mode you see specific errors 

# creates directories for inputs and results in data folder
# if they do not already exist
inputs_directory = "inputs"
results_directory = "results"

parent_directory = "/data/"
inputs_path = os.path.join(parent_directory, inputs_directory)
results_path = os.path.join(parent_directory, results_directory)

if not os.path.isdir(inputs_path):
    os.mkdir(inputs_path)
if not os.path.isdir(results_path):
    os.mkdir(results_path)

# TODO figure out when to delete inputs and results from the /data directory

@app.route('/')
def home():
    return flask.render_template("react-ui-gloss.html")

@app.route('/api/job', methods=['POST'])
def api_job():
    """" Receives and saves text model input data
    Example request:
    {
        "text": "Text string containing text to be processed",
        "model": "Example_Model",
        "nbest": 1,
        "task": "example_task"
    }
    Returns
    -------
    JSON object 
        object containing job id of the received request
    """
    # retrieve data in form of Python dictionary from request
    data = request.json
    # assign input_type to data
    data['input_type'] = 'text'

    # assign request id to be the current time stamp
    now = datetime.now()
    request_id = int(datetime.timestamp(now))
    data["id"] = request_id

    # retrieve which model was requested
    model = data["model"]
    if model not in ['fairseq', 'coling']:
        flask.abort(400, 'Invalid model') 
    # TODO delete when not needed anymore
    print(data, file=sys.stderr)
    # save the request data in the data folder
    with open(f'/data/inputs/{model}_{request_id}.txt', 'w') as outfile:
        json.dump(data, outfile)
    
    return jsonify({"job_id":request_id})

@app.route('/api/job/batch', methods=['POST'])
def api_sentence_job():
    """
    Similar to the above, but receives text input data, and submits a batch job.
    Example request:
    {
        "text": "Text string containing text to be processed",
        "model": "Example_Model",
        "nbest": 1,
        "task": "example_task"
    }
    Returns
    -------
    JSON object 
        object containing job id of the first sentence in the request
    """
    
    # retrieve data in form of Python dictionary from request
    data = request.json
    # assign input_type to data
    data['input_type'] = 'text'

    # assign request id to be the current time stamp
    now = datetime.now()
    request_id = int(datetime.timestamp(now))
    data["id"] = request_id

    # retrieve which model was requested
    model = data["model"]
    if model not in ['fairseq', 'coling']:
        flask.abort(400, 'Invalid model') 

    # split the text into sentences, save the number of sentences
    text = data['text']
    lines = re.split('\r?\n', text)
    sentences = []
    for l in lines:
        split = re.split('(\.+|\?|\!)\s?', l)
        sentences += [s for s in split if s and s != "."]
    data['text'] = sentences
    data['n_sentences'] = len(sentences)

    # save the request data in the data folder
    with open(f'/data/inputs/{model}_{request_id}.txt', 'w') as outfile:
        json.dump(data, outfile)
    
    return jsonify({"job_id":request_id})

@app.route('/api/job/eaf', methods=['POST'])
def api_job_from_eaf():
    """ Creates a new job from an eaf file.
    Tier ID and model must be specified.

    Example request:
    {
        "eaf": "XML string containing the EAF XML file",
        "tier_id": "Example",
        "model": "Example_Model",
        "nbest": n_predictions,
        "task": "example_task"
    }

    Returns
    -------
    JSON object 
        object containing job id of the received request
    """
    # retrieve data in form of Python dictionary from request
    data = request.json
    # assign request id to be the current time stamp
    now = datetime.now()
    request_id = int(datetime.timestamp(now))
    # retrieve which model was requested
    model = data["model"]
    if model not in ['fairseq', 'coling']:
        flask.abort(400, 'Invalid model') 
    # TODO delete when not needed anymore

    eaf_data = parseTierWithTime(data['tier_id'], data['eaf'])
    for item in eaf_data:
        print(item, file=sys.stderr)
    # TODO split in the same way as in the model
    # eaf_model_input = ''

    # for annotation in eaf_data:
    #     eaf_model_input += annotation['annotation_text']

    # Model metadata
    nbest = data["nbest"]
    getSeg = data['getSeg']
    getGloss = data['getGloss']
    n_sentences = len(eaf_data)
    
    model_input_data = {
        'input_type': 'eaf_file',
        'eaf_data': eaf_data,
        'eaf_orig': data['eaf'],
        'model': model,
        'id': request_id,
        'nbest': nbest,
        'getSeg': getSeg,
        'getGloss': getGloss,
        'n_sentences': n_sentences
    }
    print(data, file=sys.stderr)
    # save the request data in the data folder
    with open(f'/data/inputs/{model}_{request_id}.txt', 'w') as outfile:
        json.dump(model_input_data, outfile)
    
    return jsonify({"job_id":request_id})

@app.route('/api/eaf/tier_list', methods=['POST'])
def parse_and_get_tier_ids():
    """parse n EAF file and if it's valid return tier ids
    Parameters
    ----------
    eaf_string: string
        eaf file string
    Returns
    -------
    tier_list: JSON list
        a list containing tier ids contained in the eaf file
    """
    data = request.json
    eaf_string = data['eaf_text']
    tier_list = get_tier_ids(eaf_string)
    return jsonify(tier_list)


# for status check requests
@app.route('/api/job/<int:job_id>')
def get_job_status(job_id):
    """ checks status of the request with job_id
    Parameters
    ----------
    job_id: number 
        the id of the job which status is to be obtained
    Returns
    -------
    JSON object
        object containg "status" of the request (True if it is completed)
        and the "model" used for the request
    Raises
    ------
    HTTPS 404 not found exception 
        if ther is no job file in the data with the given job id
    """
    # if path corresponding to differnet models and job id
    # exists, then check is there is a corresponding results file
    if path.isfile(f'/data/inputs/fairseq_{job_id}.txt'):
        completed = path.isfile(f'/data/results/output_inference_json-{job_id}.std.out')
        return jsonify({"status": completed, "model" : "fairseq"})
    elif path.isfile(f'/data/inputs/coling_{job_id}.txt'):
        completed = path.isfile(f'/data/results/output_inference_json-{job_id}.std.out')
        return jsonify({"status": completed, "model" : "coling"})
    else:
        flask.abort(404)

@app.route('/api/job/<int:job_id>/batch')
def get_batch_job_status(job_id):
    """ checks status of the request with job_id
    Parameters
    ----------
    job_id: number 
        the id of the job which status is to be obtained
    Returns
    -------
    JSON object
        object containg "status" of the request (True if there is at least one processed sentence),
        the "total" number of sentences, and the number of sentences "completed" so far
    Raises
    ------
    HTTPS 404 not found exception 
        if there is no job file in the data with the given job id
    """
    
    if path.isfile(f'/data/inputs/fairseq_{job_id}.txt'):
        with open(f'/data/inputs/fairseq_{job_id}.txt', 'r') as submit_file:
            submit_data = json.load(submit_file)
            total_sentences = submit_data['n_sentences']
        sentence_paths = glob(f'/data/results/sentence_{job_id}_*')
        n_sentences = len(sentence_paths)
        started = (n_sentences > 0)
        return jsonify({"status": started, "total": total_sentences, "completed": n_sentences})
    else:
        flask.abort(404)

@app.route('/api/job/<int:job_id>/download')
def download_job_result(job_id):
    """ retrieves the result of model inference on data with job_id
    Parameters
    ----------
    job_id: number
        job id of the job which result is to be retrieved
    Returns
    -------
    JSON
        object containing the result of model inference and
        meta data including model used and etc.
    Raises
    ------
    HTTPS 404 not found exception 
        if ther is no job file in the data with the given job id
    """
    # if the path corresponding to a result file with job_id exists
    # return the data of this fil
    result_path =  f'/data/results/output_inference_json-{job_id}.std.out'
    if path.isfile(result_path):
        with open(result_path, 'r') as outfile:
            result = json.load(outfile)
        return jsonify(result)
    else:
        flask.abort(404)

@app.route('/api/job/<int:job_id>/batch/download')
def download_batch_job(job_id):
    """
    Retrieves the result of a batch job request with job_id, by finding the sentences that are currently finished
    Parameters
    ----------
    job_id: number
        id of the batch job to retrieve (results will have a sentence index after the job id number)
    Returns
    -------
    JSON
        object with the job result, possibly a partial result - the combined processed sentences so far. Also, model metadata
    Raises
    ------
    HTTPS 404 not found exception
        if there are no files with the given job id
    """

    results = []
    processed_sentences = glob(f'/data/results/sentence_{job_id}_*')

    if processed_sentences:
        for i in range(len(processed_sentences)):
            with open(f'/data/results/sentence_{job_id}_{i}.std.out', 'r') as sent_file:
                sent_data = json.load(sent_file)
                results += sent_data
        return jsonify(results)
    else:
        flask.abort(404)

@app.route('/api/job/<int:job_id>/save', methods=['POST'])
def save_job_result(job_id):
    """ saves and update job data sent from front end
    Parameters:
    ----------
    job_id: number
        job id of the job to be saved
    Returns
    -------
    JSON
        a JSON object with "output" attribute with boolean value
        corresponding to True if save was successful
    Raises
    ------
    HTTPS 404 not found exception 
        if ther is no job file in the data with the given job id
    """
    # save the data from the request as a results file with job_id
    # basically overwrites the previous results file
    result_path =  f'/data/results/output_inference_json-{job_id}.std.out'
    data = request.json
    if path.isfile(result_path):
        with open(result_path, 'w') as outfile:
            json.dump(data,outfile, indent = 4)
        return {"output": True}
    else:
        flask.abort(404)


@app.route('/api/job/convert', methods=['POST'])
def convert_to_eaf():
    """ creates a new EAF file with tiers from the preferred segmentation and glosses
    Parameters:
    -----------
    id: number
        job id of the data
    tokens: dictionary
        model predictions
    models: string
        Whether to save an ELAN with the "segmentation", "gloss", or "both"
    Returns:
    --------
    JSON
        Object with the filename of the new ELAN file
    Raises:
    -------
    HTTPS 404 not found exception
        If there is no job with the input ID
    """
    # get the contents of the request
    data = request.json

    # load the job request file, which has the original ELAN data as a string
    job_id = data['id']
    request_file_path = f'/data/inputs/fairseq_{job_id}.txt'
    if path.isfile(request_file_path):
        with open(request_file_path, 'r') as in_file:
            elan_contents = in_file.read()
        elan_data = json.loads(elan_contents)
    else:
        flask.abort(404)

    # attempt to add a new tier with the glossing results
    xml_doc = elan_data['eaf_orig']
    new_data = data['tokens']
    model_type = data['models']
    save_path = f'/data/results/newEAF_fairseq_{job_id}.txt'

    if model_type == 'gloss':
        root = writeEafTier(xml_doc, new_data, model_type='gloss', save_path=save_path)
    elif model_type == 'segmentation':
        root = writeEafTier(xml_doc, new_data, model_type="segmentation", save_path=save_path)
    else:
        root = writeEafTier(xml_doc, new_data, model_type='segmentation', save_path=save_path)
        root = writeEafTier(root, new_data, model_type='gloss', save_path=save_path)

    return {'elan': xml_doc}

@app.route('/api/job/<int:job_id>/get_eaf_file')
def get_new_eaf(job_id):
    """
    Retrieves an EAF file with two new tiers written to it.
    ----------
    job_id: number
        id of the ELAN to retrieve
    Returns
    -------
    JSON
        object with the contents of the output file and its status
    Raises
    ------
    HTTPS 404 not found exception
        if there are no files with the given job id
    """
    input_path = f'/data/inputs/fairseq_{job_id}.txt'
    if not path.isfile(input_path):
        flask.abort(404)

    result_path = f'/data/results/newEAF_fairseq_{job_id}.txt'
    if path.exists(result_path):
        xml_contents = open(result_path, 'r').read()
        return {'written_elan': xml_contents, 'status': True}
    else:
        return {'status': False}

# @app.route('/api/shutdown')
# def shutdown():
#     subprocess.run(['kill', '-9', '1'])
#     return {'shutdown': True}
    

if __name__ == '__main__': # distinguish between running directly vs flask
    
     # one of methods of app object, runs the application server
    app.run()
