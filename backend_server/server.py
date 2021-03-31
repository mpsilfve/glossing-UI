import flask, sys, json
from datetime import datetime
from flask import request, jsonify
import os
from os import path


app = flask.Flask(__name__) # create the Flask application object 
app.config["DEBUG"] = True # in debugger mode you see specific errors 

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
    # can access other dicitonary values. data is a dicitonary object
    print(data["text"], file=sys.stderr)
    with open(f'/data/{request_id}.txt', 'w') as outfile:
        json.dump(data, outfile)

    return jsonify({"job_id":request_id})

@app.route('/api/job/<int:job_id>')
def get_job_status(job_id):
    if path.isfile(f'/data/{job_id}.txt'):
        return jsonify({"status": True})
    else:
        return jsonify({"status": False})

if __name__ == '__main__': # distinguish between running directly vs flask
    app.run() # one of methods of app object, runs the application server