import flask, sys, json
from datetime import datetime
from flask import request, jsonify


app = flask.Flask(__name__) # create the Flask application object 
app.config["DEBUG"] = True # in debugger mode you see specific errors 

@app.route('/')
def home():
    return flask.render_template("form.html")
 

@app.route('/api/job', methods=['POST'])
def api_job():
    # receive 
    data = request.json
    now = datetime.now()
    request_id = int(datetime.timestamp(now))
    data["id"] = request_id
    print(data["text"], file=sys.stderr)
    with open(f'/data/{request_id}.txt', 'w') as outfile:
        json.dump(data, outfile)

    return "<h1>Post request</h1>"

if __name__ == '__main__': # distinguish between running directly vs flask
    app.run() # one of methods of app object, runs the application server