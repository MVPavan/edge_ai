# Use an official Python runtime as a parent image
FROM python:3.9-slim-buster

# Set the working directory to /core_api
WORKDIR /core_api

COPY ./requirements.txt /core_api/requirements.txt

# Install any needed packages specified in requirements.txt
RUN pip install --trusted-host pypi.python.org -r requirements.txt

# Copy the current directory contents into the container at /core_api
COPY . /core_api

# Run app.py when the container launches
CMD ["python", "main.py"]