#! /bin/bash
sudo modprobe bcm2835-v4l2

(
   while : ; do
       python /home/pi/RpiRover/server.py >> /var/log/rover.log 2>&1
       sleep 2
   done
) &
