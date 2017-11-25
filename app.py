#! /usr/bin/env python
# coding:utf-8
# author:jzh

from crawler_consumer import QueueConsumer
from crawler_producer import QueueProducer
from multiprocessing import Queue

task_queue = []
queue = Queue(maxsize=100)
p = QueueProducer(queue)
task_queue.append(p)
for i in range(1):
    c = QueueConsumer(idx=i, queue=queue)
    task_queue.append(c)
for t in task_queue:
    t.start()
for t in task_queue:
    t.join()

