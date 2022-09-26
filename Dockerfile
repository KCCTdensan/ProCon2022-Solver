FROM nvidia/cuda:11.2.2-cudnn8-devel-ubuntu20.04

WORKDIR /work

RUN apt-get update && \
  apt-get install -y python3 python3-pip libsndfile1

COPY req.train.txt .
RUN pip install -r req.train.txt

# /work/train が外界との窓口になる
COPY src-training .

ENTRYPOINT ["python3"]
CMD ["train.py"]
