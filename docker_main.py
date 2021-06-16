'''
docker run 
    --gpus all 
    --network=fr_network 
    --env-file=../fd.env 
    -v /home/pavanmv/Pavan/HW/FR/FR_MS/FRDockers/FRData:/app/Data 
    -v /home/pavanmv/Pavan/HW/FR/FR_MS/FRDockers/FRData_DB:/app/FRModule/FRFeatures/DB 
    -it fr_es:v2
'''

# import docker
# client = docker.from_env()
# for image in client.images.list():
#   print (image.tags[0])


import subprocess
from multiprocessing import get_context

# with open("./output.log", "a") as output:
#     subprocess.call("docker run -d --gpus all --network=fr_network --env-file=fr.env -v /home/pavanmv/Pavan/HW/FR/FR_MS/FRDockers/FRData:/app/Data -it fr_fd:v2", shell=True, stdout=output, stderr=output)


class PySubProcess:
    def __init__(self):
        self.docker_cmds = {
            "run":"docker run --gpus all --network=fr_network --env-file=fr.env -v /home/pavanmv/Pavan/HW/FR/FR_MS/FRDockers/FRData:/app/Data -it",
            "run_db":"docker run --gpus all --network=fr_network --env-file=fr.env -v /home/pavanmv/Pavan/HW/FR/FR_MS/FRDockers/FRData:/app/Data -v /home/pavanmv/Pavan/HW/FR/FR_MS/FRDockers/FRData_DB:/app/FRModule/FRFeatures/DB -it"
        }
        self.container_v2 = {
            "fd":"fr_fd:v2",
            "fe":"fr_fe:v2",
            "es":"fr_es:v2"
        }

    def _execute_subproc(self,cmd):
        popen = subprocess.Popen(cmd,shell=True, stdout = subprocess.PIPE, universal_newlines=True)
        for stdout_line in iter(popen.stdout.readline,""):
            yield stdout_line
        popen.stdout.close()
        return_code = popen.wait()
        if return_code:
            raise subprocess.CalledProcessError(return_code,cmd)


    def exec_subproc(self,cmd):
        # for _line in self._execute_subproc(cmd):
        #     print(_line,"\n")
        with open("./output_{}.log".format(cmd[0][-8:-3]), "a") as output:
            subprocess.call(cmd, shell=True, stdout=output, stderr=output)
        print("Finished Processing!!!")


def runDockers(cont_map):
    pysub = PySubProcess()
    pcount,cmd_list = 0,[]
    for key,value in cont_map.items():
        pcount+=value
        if key != "es":
            cmd = [pysub.docker_cmds["run"]+" "+pysub.container_v2[key]]
        else:
            cmd = [pysub.docker_cmds["run_db"]+" "+pysub.container_v2[key]]
        for i in range(value):
            cmd_list.append(cmd)
    with get_context("spawn").Pool(processes=pcount) as Pool:
        result = Pool.map(pysub.exec_subproc,cmd_list)
        print(result)


if __name__ == "__main__":
    cont_map = {
        "fd":1,
        "fe":1,
        "es":1
    }
    runDockers(cont_map)

