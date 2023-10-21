FROM nvcr.io/nvidia/deepstream:6.3-gc-triton-devel

RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        ffmpeg \
        gnutls-bin \
        gnutls-dev \
        libarchive-dev \
        libboost-all-dev \
        libgl1-mesa-glx \
        libsm6 \
        libxext6 \
        rapidjson-dev \
        wget \
        zlib1g-dev && \
    rm -rf /var/lib/apt/lists/*

RUN apt-key del 7fa2af80 && \
    wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2004/x86_64/cuda-keyring_1.0-1_all.deb && \
    dpkg -i cuda-keyring_1.0-1_all.deb

# pip
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        build-essential \
        python-dev \
        python3-dev \
        python3-pip \
        python3-setuptools \
        python3-wheel && \
    rm -rf /var/lib/apt/lists/*

COPY install_dependencies.sh /var/tmp/install_dependencies.sh 
RUN bash /var/tmp/install_dependencies.sh


WORKDIR /opt/nvidia/deepstream/deepstream

RUN wget https://github.com/NVIDIA-AI-IOT/deepstream_python_apps/releases/download/v1.1.6/user_deepstream_python_apps_install.sh \
    -O user_deepstream_python_apps_install.sh && \
    bash user_additional_install.sh &&\
    bash user_deepstream_python_apps_install.sh --build-bindings 


ENV \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1

ENV \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 

RUN pip install poetry==1.5.1

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=0 \
    POETRY_VIRTUALENVS_CREATE=0 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

WORKDIR /eai_deepstream
COPY pyproject.toml poetry.lock ./
RUN poetry export -f requirements.txt --output requirements.txt --with=prod --without-hashes && rm -rf $POETRY_CACHE_DIR

# Install any needed packages specified in requirements.txt
RUN pip --no-cache-dir install --upgrade pip && \
    pip install --trusted-host pypi.python.org -r requirements.txt --no-cache-dir --ignore-installed pyyaml

RUN echo "/root/.local/lib/" > /etc/ld.so.conf.d/local-lib.conf
RUN ldconfig

# Run app.py when the container launches
# ENTRYPOINT ["python3", "main.py"]
