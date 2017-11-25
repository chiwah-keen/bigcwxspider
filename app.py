#! /usr/bin/env python
# coding:utf-8
# author:jzh

from crawler_consumer import QueueConsumer
from crawler_producer import QueueProducer
from multiprocessing import Queue
import time
task_queue = []
queue = Queue(maxsize=100)
p = QueueProducer(queue)
p.daemon = True
p.start()
task_queue.append(p)
time.sleep(1)
for i in range(1):
    c = QueueConsumer(idx=i, queue=queue)
    c.daemon = True
    c.start()
    task_queue.append(c)

for t in task_queue:
    t.join()

