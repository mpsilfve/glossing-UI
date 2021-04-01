FROM debian:9
WORKDIR /backend_coling
RUN apt-get update && apt-get install -y \
            python2.7\
            python-pip\
            && apt-get clean && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt
# COPY coling2018-neural-transition-based-morphology .
# CMD tail -f /dev/null
# RUN cd /coling2018-neural-transition-based-morphology/lib && make
# CMD ["python","listen.py"]
CMD /backend_coling/entrypoint.sh
