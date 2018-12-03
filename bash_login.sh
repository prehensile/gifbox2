export GIFBOX_ROOT=/home/pi/gifbox2/

if [ `tty` = "/dev/tty1" ]; then 
    cd $GIFBOX_ROOT
    ./gifbox-startup.sh
fi;