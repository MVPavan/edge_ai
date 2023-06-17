from imports import (
    io, time, urljoin, pathname2url, 
    Path, wraps, logger
)

VIDEO_EXT = [".mp4",".h264",".avi"]

def timeit(func):
    @wraps(func)
    def timeit_wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        total_time = end_time - start_time
        logger.info(f'Function {func.__name__} Took {total_time:.6f} seconds')
        return result
    return timeit_wrapper


def get_label_names_from_file(filepath):
    """ Read a label file and convert it to string list """
    assert filepath is not None,"filepath cannot be empty"
    f = io.open(filepath, "r")
    labels = f.readlines()
    labels = [elm[:-1] for elm in labels]
    f.close()
    return labels


def path_to_uri(uri_str:str):
    file_path = Path(uri_str)
    if file_path.suffix in VIDEO_EXT:
        uri_str = urljoin('file:',pathname2url(file_path.as_posix()))
    return uri_str