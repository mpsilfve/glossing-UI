import flask, sys, json
from datetime import datetime
from flask import request, jsonify


app = flask.Flask(__name__) # create the Flask application object 
app.config["DEBUG"] = True # in debugger mode you see specific errors 

@app.route('/api/job', methods=['POST', 'GET'])
def api_job():
    # receive 
    if request.method == 'GET':
        return """
            <h1>Get request</h1>
            <p>Please enter the text you wish to submit:</p>
            <form>
                <textarea id=input_text></textarea>
            </form>
            <button id=button onclick="button()">Press Me</button>

            <script>
            function button() {
                const inputText = document.getElementById("input_text").value;
                postData('/api/job', {text:inputText});
            }

            async function postData(url = '', data = {}) {
                // Default options are marked with *
                try {
                    const response = await fetch(url, {
                        method: 'POST', // *GET, POST, PUT, DELETE, etc.
                        credentials: 'include', // include, *same-origin, omit
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify(data) // body data type must match "Content-Type" header
                    });
                    if (!response.ok) {
                        throw new Error('Network response was not ok');
                    }
                } catch(err) {
                    alert("Could not submit a request")
                    return;
                }
                alert("Everything worked.")
                return response.json(); // parses JSON response into native JavaScript objects
            }
            </script>
        """
    else:
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