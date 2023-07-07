# FROM nvcr.io/nvidia/deepstream:6.2-devel AS deepstream
FROM nvcr.io/nvidia/deepstream:6.2-triton AS deepstream_triton

WORKDIR /opt/nvidia/deepstream/deepstream

RUN wget https://github.com/NVIDIA-AI-IOT/deepstream_python_apps/releases/download/v1.1.6/user_deepstream_python_apps_install.sh \
    -O user_deepstream_python_apps_install.sh && \
    bash user_additional_install.sh &&\
    bash user_deepstream_python_apps_install.sh --build-bindings 


WORKDIR /eai_deepstream

COPY ./requirements.txt /eai_deepstream/requirements.txt

# Install any needed packages specified in requirements.txt
RUN pip install --trusted-host pypi.python.org -r requirements.txt

RUN echo "/root/.local/lib/" > /etc/ld.so.conf.d/local-lib.conf
RUN ldconfig

COPY . /eai_deepstream

# Run app.py when the container launches
ENTRYPOINT ["python", "main.py"]
