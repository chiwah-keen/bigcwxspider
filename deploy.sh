#! /bin/bash

source ~/env2/bin/activate

ps aux | grep bigcwxspider | awk '{print $2}' | xargs kill
sleep 1

nohup python `pwd`/app.py &
nohup python `pwd`/webservice.py &
