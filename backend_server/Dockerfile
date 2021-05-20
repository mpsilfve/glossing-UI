FROM python:3.8-alpine
WORKDIR /backend_server
COPY requirements.txt /backend_server/
# RUN pip install -r requirements.txt --no-cache-dir
# COPY . /code/

# tell flask which python file is the server
ENV FLASK_APP server.py
# to set Flask to autoreload
ENV FLASK_ENV development 
# CMD flask run --host=0.0.0.0
# CMD pip install -r requirements.txt --no-cache-dir

# entrypoint script installs requirements and runs flask
CMD  /backend_server/entrypoint.sh 
