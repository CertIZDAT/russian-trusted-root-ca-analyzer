import multiprocessing as mp
from typing import Callable


def process_batch(target_func: Callable, batch: list[str], batch_idx: int, total_batch: int) -> list:
    results: list = []
    THREAD_MULTIPLIER: int = 8
    with mp.Pool(mp.cpu_count() * THREAD_MULTIPLIER) as pool:
        for i, link in enumerate(batch):
            results.append(pool.apply_async(
                target_func, (link, i + 1, batch, batch_idx, total_batch)))
        pool.close()
        pool.join()
    return results
