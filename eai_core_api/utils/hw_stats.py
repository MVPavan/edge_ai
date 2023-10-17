def time_mem_it(func):
    @wraps(func)
    def time_mem_it_wrapper(*args, **kwargs):
        process = psutil.Process(os.getpid())
        start_memory = process.memory_info().rss
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        # result, total_frames = func(*args, **kwargs)
        end_time = time.perf_counter()
        total_time = end_time - start_time
        # time_per_frame = total_time/total_frames
        end_memory = process.memory_info().rss
        ram_changed = (end_memory - start_memory)/(2**30)

        # cpu_percent = process.cpu_percent(interval=1)  # interval=1 means average over 1 second
        cpu_percent = 0
        # Get the number of CPU cores the process can run on
        # per_core_cpu_percent = psutil.cpu_percent(interval=1, percpu=True)
        # cpu_percent=0
        # for i, percent in enumerate(per_core_cpu_percent):
        #     cpu_percent += percent
        
        # print(f'Function {func.__name__} Took {total_time:.6f} seconds and time per frame: {time_per_frame}')
        # print(f'Function {func.__name__} Took {total_time:.6f} seconds')
        # print(f"Function {func.__name__} RAM usage: {ram_changed:.4f} GB")
        # print(f"Function {func.__name__} CPU usage: {cpu_percent:.4f}%")
        # print(f"Function {func.__name__} CPU usage: {cpu_percent:.4f}/{len(per_core_cpu_percent)}%")

        time_mem_stats = TimeMemStats()
        time_mem_stats.total_time= total_time
        time_mem_stats.ram_changed = ram_changed
        time_mem_stats.cpu_usage = cpu_percent
        return result, time_mem_stats
    return time_mem_it_wrapper