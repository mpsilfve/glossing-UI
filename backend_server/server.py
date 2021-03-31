import flask, sys, json
from datetime import datetime
from flask import request, jsonify
import os
from os import path


app = flask.Flask(__name__) # create the Flask application object 
app.config["DEBUG"] = True # in debugger mode you see specific errors 

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
    # receive 
    data = request.json
    # is data a JSON object? 
    now = datetime.now()
    request_id = int(datetime.timestamp(now))
    data["id"] = request_id
    model = data["model"]
    # can access other dicitonary values. data is a dicitonary object
    print(data, file=sys.stderr)

    with open(f'/data/{model}_{request_id}.txt', 'w') as outfile:
        json.dump(data, outfile)

    return jsonify({"job_id":request_id})

@app.route('/api/job/<int:job_id>')
def get_job_status(job_id):
    if path.isfile(f'/data/fairseq_{job_id}.txt') or path.isfile(f'/data/coling_{job_id}.txt'):
        return jsonify({"status": True})
    else:
        return jsonify({"status": False})

if __name__ == '__main__': # distinguish between running directly vs flask
    
     # one of methods of app object, runs the application server
    app.run()
