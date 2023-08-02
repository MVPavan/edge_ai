
from imports import (
    subprocess, signal, time, faust
)


# Start a Faust worker
def start_worker(app_name, worker_port):
    worker = subprocess.Popen(["faust", "-A", app_name, "worker", "-l", "info", "--web-port", worker_port])
    print(f"Started worker {worker_port} with PID {worker.pid}")
    return worker

# Stop a Faust worker
def stop_worker(worker):
    worker.send_signal(signal.SIGINT)
    worker.wait()  # Wait for process to terminate
    print(f"Stopped worker with PID {worker.pid}")

# Example usage:

# Start two workers
worker1 = start_worker("test_codes.faust_1:test_app", "6000")
worker2 = start_worker("test_codes.faust_1:test_app", "6001")

# Do some work...
time.sleep(10)

# Stop the workers
stop_worker(worker1)
stop_worker(worker2)