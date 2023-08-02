import faust
import multiprocessing
import time
import os
import signal

# Define your Faust app
app = faust.App(
    'my_app_2', 
    broker='kafka://localhost:8097',
)

# Define a function to run the Faust worker
def run_worker(app, port):
    app.conf.web_port = port
    app.Worker(loglevel=20).execute_from_commandline()

# Start a worker
def start_worker(app, port):
    process = multiprocessing.Process(target=run_worker, args=(app, port))
    process.start()
    return process

# Kill a worker
def kill_worker(process):
    print("killing: ", process.pid)
    os.kill(process.pid, signal.SIGINT)

# Example usage:

# Start two workers
worker1 = start_worker(app, 6000)
worker2 = start_worker(app, 6001)

# Do some work...
time.sleep(10)

# Stop the workers
kill_worker(worker1)
worker1.join()
time.sleep(5)

kill_worker(worker2)
# Wait for the worker processes to exit
worker2.join()
time.sleep(5)
