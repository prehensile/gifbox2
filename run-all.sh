export GIFBOX_MEDIA=/home/pi/gifbox2/media
cd ~/gifbox2/server-local
./run-server.sh &
## will invoke xinitrc.sh 
startx -- -nocursor