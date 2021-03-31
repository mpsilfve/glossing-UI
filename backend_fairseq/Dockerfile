FROM python:3.9
WORKDIR /backend_fairseq
# RUN apt-get update && apt-get install -y \
#             python3.9\
#             python-pip3\
#             && apt-get clean && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt
# COPY fairseq ./fairseq
# COPY word_model ./word_model
# RUN cd fairseq && pip install --editable ./
#  add run commands that will install (setup) the model 
# CMD ["/bin/sh"]
CMD tail -f /dev/null
