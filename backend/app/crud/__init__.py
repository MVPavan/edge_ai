"""
first create analytics job in pgsql and get job id

then save all the images to disk in background using redis queue - with job id
get all paths of images - job id from redis result
save all paths & logs in mongo db
populate back all input with job id in JobTasks in pgsql


"""
