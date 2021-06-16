# Import MinIO library.
import json
from pathlib import Path
from minio import Minio

# import time
from profilehooks import profile


class Result:
    def __init__(self,):
        self.success = False
        self.response = []
        self.incomplete = False


class MinioClient:
    """
        Utility class to handle minio operations for python clients
    """

    def __init__(self, host, access_key, secret_key, secure=False):
        self._minio_client = Minio(
            host, access_key=access_key, secret_key=secret_key, secure=secure
        )

    def _mkdir(self, local_save_dir):
        Path(local_save_dir).mkdir(parents=True, exist_ok=True)

    ####################################################################################################
    ########################   BUCKET OPERATIONS  ######################################################
    ####################################################################################################

    def make_bucket(self, bucket_name):
        result = Result()
        try:
            self._minio_client.make_bucket(bucket_name)
            result.success = True
            result.response = bucket_name
        except Exception as err:
            result.response = err
        return result

    ####################################################################################################
    ########################   LIST OPERATIONS  ######################################################
    ####################################################################################################

    def list_buckets(self):
        return self._minio_client.list_buckets()

    def list_objects_iterator(self, bucket_name, prefix, recursive=True):
        return self._minio_client.list_objects(
            bucket_name, prefix=prefix, recursive=recursive
        )

    def list_objects(self, bucket_name, prefix, recursive=True):
        result = Result()
        try:
            object_iter = self.list_objects_iterator(
                bucket_name, prefix=prefix, recursive=recursive
            )
            result.response = [obj.object_name for obj in object_iter]
            if len(result.response) > 0:
                result.success = True
        except Exception as err:
            result.response = err
        return result

    ####################################################################################################
    ########################   REMOVE OPERATIONS  ######################################################
    ####################################################################################################

    def remove_bucket(self, bucket_name):
        self._minio_client.remove_bucket(bucket_name)

    def remove_object(self, bucket_name, object_name):
        result = Result()
        try:
            self._minio_client.remove_object(
                bucket_name=bucket_name, object_name=object_name
            )
            result.success = True
        except Exception as err:
            result.response = err
        return result

    def remove_objects(self, bucket_name, objects_iter):
        result = Result()
        try:
            del_err = self._minio_client.remove_objects(
                bucket_name=bucket_name, objects_iter=objects_iter
            )
            result.response = [err for err in del_err]
            if len(result.response) > 0:
                result.success = True
        except Exception as err:
            result.response = err
        return result

    def remove_objects_prefix(self, bucket_name, prefix):
        list_result = self.list_objects(bucket_name, prefix)
        result = Result()
        if list_result.success:
            remove_result = self.remove_objects(bucket_name, list_result.response)
            result = remove_result
        else:
            result = list_result
        return result

    ####################################################################################################
    ########################   PUT OPERATIONS  #########################################################
    ####################################################################################################
    def put_object(self, bucket_name, object_name, data, length, prefix=""):
        if prefix:
            object_name_ = str(Path(prefix, object_name))
        else:
            object_name_ = object_name
        result = Result()
        try:
            tag = self._minio_client.put_object(
                bucket_name, object_name=object_name_, data=data, length=length
            )
            result.success = True
            result.response = tag
        except Exception as err:
            result.response = err
        return result

    def fput_object(self, bucket_name, object_name, local_file_path, prefix=""):
        if prefix:
            object_name_ = str(Path(prefix, object_name))
        else:
            object_name_ = object_name
        result = Result()
        try:
            tag = self._minio_client.fput_object(
                bucket_name, object_name=object_name_, file_path=local_file_path
            )
            result.success = True
            result.response = tag
        except Exception as err:
            result.response = err
        return result

    # @profile(immediate=True)
    def fput_folder_objects(self, bucket_name, local_dir, tags_list=[], prefix=""):
        result = Result()
        data = []
        for file_path in Path(local_dir).iterdir():
            if file_path.suffix in tags_list:
                fput_res = self.fput_object(
                    local_file_path=file_path,
                    bucket_name=bucket_name,
                    object_name=file_path.name,
                    prefix=prefix,
                )
                data.append((file_path.name, fput_res.response))
                if not fput_res.success:
                    result.incomplete = True
        result.response = data
        if result.incomplete:
            result.success = False
        else:
            result.success = True
        return result

    def fput_fastapi_objects(
        self, bucket_name, file_upload_list, tags_list=[], prefix=""
    ):
        result = Result()
        data = []
        for in_file in file_upload_list:
            # if file_path.suffix in tags_list:
            fput_res = self.fput_object(
                bucket_name=bucket_name,
                object_name=in_file.filename,
                local_file_path=in_file.file.fileno(),
                prefix=prefix,
            )
            data.append((in_file.filename, fput_res.response))
            if not fput_res.success:
                result.incomplete = True
        result.response = data
        if result.incomplete:
            result.success = False
        else:
            result.success = True
        return result

    ####################################################################################################
    ########################   GET OPERATIONS  #########################################################
    ####################################################################################################

    def get_object(self, bucket_name, object_name, prefix=""):
        if prefix:
            object_name_ = str(Path(prefix, object_name))
        else:
            object_name_ = object_name

        result = Result()
        try:
            data = self._minio_client.get_object(bucket_name, object_name_)
            result.success = True
            result.response = data
        except Exception as err:
            # print(err)
            result.response = err

        return result

    def get_multi_object(self, bucket_name, prefix=""):
        list_res = self.list_objects(bucket_name, prefix=prefix, recursive=True)
        result = Result()
        if list_res.success:
            data = []
            try:
                for object_name in list_res.response:
                    get_result = self.get_object(bucket_name, object_name)
                    data.append((object_name, get_result.response))
                    if not get_result.success:
                        result.incomplete = True
                result.response = data
                if result.incomplete:
                    result.success = False
                else:
                    result.success = True
            except Exception as err:
                result.response = err
        else:
            result.response = list_res.response
        return result

    ####################################################################################################
    ########################   GET & SAVE OPERATIONS  ##################################################
    ####################################################################################################

    def _fget_object(self, bucket_name, object_name, local_save_dir, prefix=""):
        if prefix:
            object_name_ = str(Path(prefix, object_name))
        else:
            object_name_ = object_name

        result = Result()
        try:
            obj = self._minio_client.fget_object(
                bucket_name=bucket_name,
                object_name=object_name_,
                file_path=str(Path(local_save_dir, Path(object_name_).name)),
            )
            result.success = True
            result.response = obj
        except Exception as err:
            result.response = err
        return result

    def fget_object(self, bucket_name, object_name, local_save_dir, prefix=""):
        self._mkdir(local_save_dir)
        result = self._fget_object(bucket_name, object_name, local_save_dir, prefix)
        return result.response

    # @profile
    def fget_multi_object(self, bucket_name, local_save_dir, prefix=""):
        self._mkdir(local_save_dir)
        list_res = self.list_objects(bucket_name, prefix=prefix, recursive=True)
        result = Result()
        if list_res.success:
            data = []
            try:
                for object_name in list_res.response:
                    get_result = self._fget_object(
                        bucket_name, object_name, local_save_dir
                    )
                    data.append((object_name, get_result.response))
                    if not get_result.success:
                        result.incomplete = True
                result.response = data
                if result.incomplete:
                    result.success = False
                else:
                    result.success = True
            except Exception as err:
                result.response = err
        else:
            result.response = list_res.response
        return result

    ####################################################################################################
    ########################   BUCKET POLICY OPERATIONS  ###############################################
    ####################################################################################################

    def get_bucket_policy(self, bucket_name):
        return self._minio_client.get_bucket_policy(bucket_name)

    def set_bucket_policy(self, username):
        with open("user_policy.json", "r") as json_file:
            policy = json.load(json_file)
            resources = policy["Statement"][0]["Resource"]
            resources.append('"arn:aws:s3:::"' + str(username) + '"/*"')
            resources.append('"arn:aws:s3:::' + str(username) + '"')
            print(policy["Statement"][0]["Resource"])
        self._minio_client.set_bucket_policy(username, json.dumps(policy))


###########################################################################################################
###########################################################################################################

# if __name__ == '__main__':
#     minio_host = 'localhost:9001'
#     acc_key = 'minio'
#     sec_key = 'minio123'
#     local_dir='/home/pavanmv/Pavan/HW/FR/FR_MS/backend/data/'
#     tags_list = [".JPG"]
#     bucket_name = "pavan"
#     prefix = "honfr"
#     local_save_dir = "data_wow"

#     client = MinioClient(minio_host, acc_key, sec_key)
# #     # response = client.make_bucket("pavan")
#     remove_res = client.remove_objects_prefix(bucket_name=bucket_name,prefix=prefix)

#     # st = time.perf_counter()
#     # res_fol_up = client.fput_folder_objects(bucket_name=bucket_name,local_dir=local_dir,
#     #                                     tags_list=tags_list,prefix=prefix)

#     # # dur = time.perf_counter()-st
#     # # upload_size_mb = sum([file_path.stat().st_size for file_path in Path(local_dir).iterdir()])/(1024*1024)
#     # # upload_mbps = upload_size_mb/dur
#     # # print(dur, upload_size_mb, upload_mbps)


#     # response2=client.fget_multi_object(bucket_name=bucket_name, local_save_dir=local_save_dir, prefix=prefix)
#     # print("wow")
