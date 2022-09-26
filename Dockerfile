FROM tensorflow/tensorflow:2.10.0-gpu

WORKDIR /work

RUN apt-get update && \
    apt-get install -y libsndfile1 && \
    rm -rf /var/lib/apt/lists/* && \
    python3 -m pip install --upgrade pip

COPY req.train.txt .
RUN pip install -r req.train.txt

# /work/train が外界との窓口になる
COPY src-training .

ENTRYPOINT ["python3"]
CMD ["train.py"]
