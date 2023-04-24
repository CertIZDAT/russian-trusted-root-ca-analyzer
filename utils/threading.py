import multiprocessing as mp


def process_batch(target_func, batch, batch_idx, total_batch) -> list:
    results: list = []
    thread_multiplier: int = 8
    with mp.Pool(mp.cpu_count() * thread_multiplier) as pool:
        for i, link in enumerate(batch):
            results.append(pool.apply_async(
                target_func, (link, i+1, batch, batch_idx, total_batch)))
        pool.close()
        pool.join()
    return results
