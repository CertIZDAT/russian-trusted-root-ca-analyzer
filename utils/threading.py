import multiprocessing as mp


def process_batch(target_func, batch, timeout, batch_idx, total_batch):
    results = []
    thread_multiplier = 8
    with mp.Pool(mp.cpu_count() * thread_multiplier) as pool:
        for i, link in enumerate(batch):
            results.append(pool.apply_async(
                target_func, (link, i+1, batch, timeout, batch_idx, total_batch)))
        pool.close()
        pool.join()
    return results
