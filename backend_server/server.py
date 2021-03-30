import flask, sys
from flask import request, jsonify


app = flask.Flask(__name__) # create the Flask application object 
app.config["DEBUG"] = True # in debugger mode you see specific errors 

# Create some test data for our catalog in the form of a list of dictionaries.
books = [
    {'id': 0,
     'title': 'A Fire Upon the Deep',
     'author': 'Vernor Vinge',
     'first_sentence': 'The coldsleep itself was dreamless.',
     'year_published': '1992'},
    {'id': 1,
     'title': 'The Ones Who Walk Away From Omelas',
     'author': 'Ursula K. Le Guin',
     'first_sentence': 'With a clamor of bells that set the swallows soaring, the Festival of Summer came to the city Omelas, bright-towered by the sea.',
     'published': '1973'},
    {'id': 2,
     'title': 'Dhalgren',
     'author': 'Samuel R. Delany',
     'first_sentence': 'to wound the autumnal city.',
     'published': '1975'}
]


@app.route('/', methods=['GET']) # we have mapped / path to home. whatever is mapped to / just gets displayed to browser right away. this is called routing 
# get requests are to the user, post requests are from the user. 
def home():
    return "<h1>Distant Cuddling Archive</h1><p>This site is a prototype API for distant reading of science fiction novels.</p>"
# instead of returning HTML, model server will return data in the form af JSON file. 

# A route to return all of the available entries in our catalog.
@app.route('/api/v1/resources/books/all', methods=['GET'])
def api_all():
    return jsonify(books)

@app.route('/api/v1/resources/books', methods=['GET'])
def api_id():
    # Check if an ID was provided as part of the URL.
    # If ID is provided, assign it to a variable.
    # If no ID is provided, display an error in the browser.
    if 'id' in request.args: # what are request args? those are the query parameter : after "?"
        id = int(request.args['id'])
    else:
        return "Error: No id field provided. Please specify an id."

    # Create an empty list for our results
    results = []

    # Loop through the data and match results that fit the requested ID.
    # IDs are unique, but other fields might return many results
    for book in books:
        if book['id'] == id:
            results.append(book)

    # Use the jsonify function from Flask to convert our list of
    # Python dictionaries to the JSON format.
    return jsonify(results)

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
                const response = await fetch(url, {
                    method: 'POST', // *GET, POST, PUT, DELETE, etc.
                    credentials: 'include', // include, *same-origin, omit
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(data) // body data type must match "Content-Type" header
                });
                return response.json(); // parses JSON response into native JavaScript objects
            }
            </script>
        """
    else:
        json_data = request.json
        print(json_data["text"], file=sys.stderr)
        return "<h1>Post request</h1>"

if __name__ == '__main__': # distinguish between running directly vs flask
    app.run() # one of methods of app object, runs the application server