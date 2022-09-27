# https://www.tensorflow.org/install/source?hl=ja#tested_build_configurations
# 英語版のページに最新の対応表がある
FROM nvidia/cuda:11.2.2-cudnn8-devel-ubuntu20.04

WORKDIR /work

RUN apt-get update && \
    apt-get install -y python3 python3-pip libsndfile1 vim && \
    rm -rf /var/lib/apt/lists/* && \
    python3 -m pip install --upgrade pip

COPY req.train.txt .
RUN pip install -r req.train.txt

# /work/train が外界との窓口になる
COPY src-training .

ENTRYPOINT ["python3"]
CMD ["test.py"]
