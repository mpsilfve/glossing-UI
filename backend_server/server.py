""" Flask-based back end server

Allows for receiving and sending data from and to front-end
"""
import flask, sys, json
from datetime import datetime
from flask import request, jsonify
import os
from os import path


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

@app.route('/')
def home():
    return flask.render_template("form.html")
 

@app.route('/api/job', methods=['POST'])
def api_job():
    """" Receives and saves model input data
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
    data["id"] = request_id
    # retrieve which model was requested
    model = data["model"]
    # TODO delete when not needed anymore
    print(data, file=sys.stderr)
    # save the request data in the data folder
    with open(f'/data/{model}_{request_id}.txt', 'w') as outfile:
        json.dump(data, outfile)
    
    return jsonify({"job_id":request_id})

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
    if path.isfile(f'/data/fairseq_{job_id}.txt'):
        # TODO add for fairseq when fairseq exists
        return jsonify({"status": False, "model" : "fairseq"})
    elif path.isfile(f'/data/coling_{job_id}.txt'):
        completed = path.isfile(f'/data/results/output_inference_json-{job_id}.std.out')
        return jsonify({"status": completed, "model" : "coling"})
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
    

if __name__ == '__main__': # distinguish between running directly vs flask
    
     # one of methods of app object, runs the application server
    app.run()
