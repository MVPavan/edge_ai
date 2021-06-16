from main import FRContainer
# from FRModule.FRCore.workers.fd_worker import FDWorker
# from FRModule.FRCore.workers.fe_worker import FEWorker
# from FRModule.FRCore.workers.es_worker import ESWorker


# def run_worker(worker_name):
#     if worker_name == "FD":
#         FDWorker()
#         print("fakljds")
#     elif worker_name == "FE":
#         FEWorker()
#     elif worker_name == "ES":
#         ESWorker()

# if __name__ == "__main__":
#     run_worker("ES")

if __name__ == "__main__":
    FRContainer().start()
