import requests
import time
from multiprocessing import Process
import secrets
from collections import Counter


pwd = 'askjxnaslknxiasnlxka'


def agent_start(path, N):
    t = time.time()
    i = 0
    codes = Counter()
    size = 0
    while True:
        if i == N:
            break
        name = secrets.token_urlsafe(10)
        r = requests.get('http://localhost:8080/app/register?pwd={}&name={}'.format(pwd, name))
        codes[r.status_code] += 1
        size += len(r.content)
        i += 1
    passed = time.time() - t

    for line in [
        '*************',
        'Passed: {}'.format(round(passed, 5)),
        'Averege sec/request: {}'.format(round(passed / N, 5)),
        'Downloaded {} MB'.format(round(size / 1048576, 3)),
        'Averege download speed: {} MB/sec'.format(round(size / (1048576 * passed), 3)),
        'Codes: {}'.format(codes),
        'Accuracy (200s/total): {} %'.format(round(100 * codes[200] / N, 2)),
        '*************'
    ]:
        print(line)


if __name__ == '__main__':
    PATH = '/app/register?name=Dima'
    TIMES = 1000
    NUM = 2

    start = time.time()
    procs = []
    for i in range(0, NUM):
        p = Process(target=agent_start, args=(PATH, TIMES))
        procs.append(p)

    for proc in procs:
        proc.start()

    for proc in procs:
        proc.join()

    end = time.time()
    print('Passed {}'.format(round(end - start, 5)))
