import time

def dump_progress(it: list, desc: str, unit: str = "it", interval_seconds: float = 5):
    print(desc, flush=True)

    t = time.time()
    n = len(it)
    n_strlen = len(str(n))

    for i, item in enumerate(it):
        if (now := time.time()) >= t + interval_seconds:
            print(f"{desc} ({i:{n_strlen}d}/{n} {unit}) [{int(100 * i / n):2d}%]", flush=True)
            t = now

        yield item

    print("Done.")
