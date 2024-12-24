from multiprocessing import Process


def run_parallel(*funcs):
    processes = [Process(target=func) for func in funcs]
    [p.start() for p in processes]
    return processes
