ARG CUDA="9.0"
ARG CUDNN="7"

FROM nvidia/cuda:${CUDA}-cudnn${CUDNN}-devel-ubuntu16.04

RUN echo 'debconf debconf/frontend select Noninteractive' | debconf-set-selections

# install basics
RUN apt-get update -y \
 && apt-get install -y apt-utils git curl ca-certificates bzip2 cmake tree htop bmon iotop g++ \
 && apt-get install -y libglib2.0-0 libsm6 libxext6 libxrender-dev

# Install Miniconda
RUN curl -so /miniconda.sh https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh \
 && chmod +x /miniconda.sh \
 && /miniconda.sh -b -p /miniconda \
 && rm /miniconda.sh

ENV PATH=/miniconda/bin:$PATH

RUN mkdir /app
COPY ./environment_gpu.yml /app

RUN conda env create -f /app/environment_gpu.yml
ENV CONDA_DEFAULT_ENV=fr_gpu
ENV CONDA_PREFIX=/miniconda/envs/$CONDA_DEFAULT_ENV
ENV PATH=$CONDA_PREFIX/bin:$PATH
ENV CONDA_AUTO_UPDATE_CONDA=false

RUN /bin/bash -c "source activate $(head -1 environment_gpu.yml | cut -d' ' -f2)"

ARG FORCE_CUDA="1"
ENV FORCE_CUDA=${FORCE_CUDA}


COPY . /app
COPY ../FRCommon /app/FRCommon
WORKDIR /app/
CMD ["python", "run_es_worker.py" ]