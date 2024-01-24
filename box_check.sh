#!/bin/bash

# add this  line    @/home/pi/Desktop/box_check.sh
# to the file       /etc/xdg/lxsession/LXDE-pi/autostart 

# And to the file   /etc/rc.local 
# without leading #
# sudo pigpiod
# echo "5" > /sys/class/gpio/export
# echo "6" > /sys/class/gpio/export
# echo "12" > /sys/class/gpio/export
# echo "17" > /sys/class/gpio/export
# echo "22" > /sys/class/gpio/export
# echo "23" > /sys/class/gpio/export
# echo "24" > /sys/class/gpio/export
# echo "25" > /sys/class/gpio/export
# echo "27" > /sys/class/gpio/export
# echo "out" > /sys/class/gpio/gpio5/direction
# echo "out" > /sys/class/gpio/gpio6/direction
# echo "out" > /sys/class/gpio/gpio12/direction
# echo "out" > /sys/class/gpio/gpio17/direction
# echo "out" > /sys/class/gpio/gpio22/direction
# echo "out" > /sys/class/gpio/gpio23/direction
# echo "out" > /sys/class/gpio/gpio24/direction
# echo "out" > /sys/class/gpio/gpio25/direction
# echo "out" > /sys/class/gpio/gpio27/direction
# echo "0" > /sys/class/gpio/gpio5/value
# echo "0" > /sys/class/gpio/gpio6/value
# echo "0" > /sys/class/gpio/gpio12/value
# echo "0" > /sys/class/gpio/gpio17/value
# echo "0" > /sys/class/gpio/gpio22/value
# echo "0" > /sys/class/gpio/gpio23/value
# echo "0" > /sys/class/gpio/gpio24/value
# echo "0" > /sys/class/gpio/gpio25/value
# echo "0" > /sys/class/gpio/gpio27/value



echo "Box control loop"
A=`tail -n 1 /home/pi/Desktop/box_log | cut -d " " -f 1`
while true
do
echo "Waiting 1 minute"
sleep 1m
B=`tail -n 1 /home/pi/Desktop/box_log | cut -d " " -f 1`
if [ "$A" = "$B" ]
then
echo "time $A is equal to $B, RESTART" 
echo "$A is equal to $B, RESTART" >> /home/pi/Desktop/box_err
lxterminal -e "python3 /home/pi/Desktop/box.py -f"
else
echo "time $A is not equal to $B, box is running properly"  
fi
A=$B
done
