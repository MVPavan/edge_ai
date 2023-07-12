#
# Build image
#

FROM nvcr.io/nvidia/deepstream:6.2-triton AS DS_BUILD


RUN pip install poetry==1.5.1

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=0 \
    POETRY_VIRTUALENVS_CREATE=0 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

WORKDIR /eai_deepstream
COPY pyproject.toml poetry.lock ./
RUN poetry export -f requirements.txt --output requirements.txt --with=prod --without-hashes && rm -rf $POETRY_CACHE_DIR

#
# Prod image
#


FROM nvcr.io/nvidia/deepstream:6.2-triton AS DS_PROD

ENV \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1

ENV \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 

WORKDIR /opt/nvidia/deepstream/deepstream

RUN wget https://github.com/NVIDIA-AI-IOT/deepstream_python_apps/releases/download/v1.1.6/user_deepstream_python_apps_install.sh \
    -O user_deepstream_python_apps_install.sh && \
    bash user_additional_install.sh &&\
    bash user_deepstream_python_apps_install.sh --build-bindings 

WORKDIR /eai_deepstream

COPY --from=DS_BUILD /eai_deepstream/requirements.txt /eai_deepstream

# Install any needed packages specified in requirements.txt
RUN pip --no-cache-dir install --upgrade pip && \
    pip install --trusted-host pypi.python.org -r requirements.txt --no-cache-dir --ignore-installed pyyaml

RUN echo "/root/.local/lib/" > /etc/ld.so.conf.d/local-lib.conf
RUN ldconfig

COPY . /eai_deepstream

# Run app.py when the container launches
ENTRYPOINT ["python3", "main.py"]
