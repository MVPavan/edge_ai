FROM fr_base:v2

COPY . /app
WORKDIR /app/

ENV CONDA_DEFAULT_ENV=fr
ENV CONDA_PREFIX=/opt/conda/envs/$CONDA_DEFAULT_ENV
ENV PATH=$CONDA_PREFIX/bin:$PATH
ENV CONDA_AUTO_UPDATE_CONDA=false
RUN /bin/bash -c "source activate $(head -1 environment.yml | cut -d' ' -f2)"
CMD ["python", "run_es_worker.py" ]