#!/bin/bash

java -jar /app.jar &
sleep 3m
# /bin/python3 /app/keep_alive.py 
/bin/python3 /app/monitorfolder.py 