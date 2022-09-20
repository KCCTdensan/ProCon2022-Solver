FROM nvidia/cuda:11.2.2-cudnn8-devel-ubuntu20.04

RUN apt-get update && \
  apt-get install -y python3 python3-pip libsndfile1

ADD req.train.txt .
RUN pip install -r req.train.txt
