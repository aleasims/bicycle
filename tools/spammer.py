import requests
import time
import random
import os
import multiprocessing
import secrets
from collections import Counter


pwd = 'askjxnaslknxiasnlxka'


def agent_start(path, N, responses):
    t = time.time()
    i = 0
    codes = Counter()
    size = 0
    while True:
        try:
            if i == N:
                break
            name = secrets.token_urlsafe(10)
            rand_time = random.random() / 10
            time.sleep(rand_time)
            r = requests.get('http://localhost:8080/app/register?pwd={}&name={}'.format(pwd, name))
            codes[r.status_code] += 1
            size += len(r.content)
            i += 1
        except KeyboardInterrupt:
            print('Job interrupted')
            break
    passed = time.time() - t

    responses.put([
        '************* Agent {}'.format(os.getpid()),
        'Passed: {}'.format(round(passed, 5)),
        'Averege sec/request: {}'.format(round(passed / N, 5)),
        'Downloaded {} MB'.format(round(size / 1048576, 3)),
        'Averege download speed: {} MB/sec'.format(round(size / (1048576 * passed), 3)),
        'Codes: {}'.format(codes),
        'Accuracy (200s/total): {} %'.format(round(100 * codes[200] / N, 2)),
        '*************'
    ])


if __name__ == '__main__':
    PATH = '/app/register?name=Dima'
    TIMES = 10
    NUM = 10

    procs = []
    responses = multiprocessing.Queue(NUM)
    start = time.time()
    for i in range(0, NUM):
        p = multiprocessing.Process(target=agent_start,
                                    args=(PATH, TIMES, responses))
        procs.append(p)

    for proc in procs:
        proc.start()

    for proc in procs:
        proc.join()

    for i in range(0, responses.qsize()):
        resp = responses.get()
        for line in resp:
            print(line)

    end = time.time()
    print('Passed {}'.format(round(end - start, 5)))
