#! /bin/bash
(
   while : ; do
       sudo python /home/pi/RpiRover/server.py >> /var/log/rover.log 2>&1
       sleep 2
   done
) &
