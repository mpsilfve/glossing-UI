FROM python:3.9
WORKDIR /backend_fairseq
RUN apt-get update && apt-get install -y \
            python3.9\
            python3-pip\
            cython3\
            && apt-get clean && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

CMD /backend_fairseq/entrypoint.sh
