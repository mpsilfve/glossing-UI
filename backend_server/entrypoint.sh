#!/bin/sh
# installs requirements and runs flask application
pip install -r requirements.txt --no-cache-dir
flask run --host=0.0.0.0
