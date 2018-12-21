import time
import threading


def wait(func, test=lambda x: True, timeout=60, polling_time=5, **kwargs):
    fin = threading.Event()
    result = [None]
    raise_ex = True
    if 'default' in kwargs:
        raise_ex = False
        default = kwargs['default']

    def _loop():
        while True:
            if fin.is_set():
                break
            value = func()
            if test(value):
                result[0] = value
                break
            time.sleep(polling_time)

    loop = threading.Thread(target=_loop)
    loop.start()
    loop.join(timeout=timeout)

    if loop.is_alive():
        fin.set()
        if raise_ex:
            raise TimeoutError
        else:
            return default

    return result[0]


if __name__ == '__main__':
    def count2x5():
        return 7
    def test_func(val):
        return val == 10

    res = wait(count2x5, test=test_func, timeout=3, polling_time=1)
    print(res)
