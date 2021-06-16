FROM tiangolo/uvicorn-gunicorn-fastapi:python3.7

# RUN pip install celery~=4.3 passlib[bcrypt] tenacity requests emails "fastapi>=0.16.0" uvicorn gunicorn pyjwt python-multipart email_validator jinja2 psycopg2-binary alembic SQLAlchemy

COPY . /app

WORKDIR /app/

RUN pip install -r requirements.txt

# ENTRYPOINT ["python", "run_server.py"]
CMD [ "python",  "run_server.py"]