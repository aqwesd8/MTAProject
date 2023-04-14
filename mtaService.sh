#!/bin/bash

sudo bash -c 'pyuwsgi --http 127.0.0.1:5000 --master -p 4 -R 10 -w mta:app --stats 127.0.0.1:5001 > Logs/mtaserver.log 2>&1' &
sleep 10
sudo bash -c 'python mtatext.py --led-cols 64 -s F23 R33' &
sudo bash -c 'python PinTest/pinTest.py' &
exit 0
