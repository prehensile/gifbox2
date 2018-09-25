export GIFBOX_MEDIA=/home/pi/gifbox2/media
screen -dm bash -c 'cd ~/gifbox2/server-local; ./run-server.sh; exec sh'
## will invoke xinitrc.sh 
startx -- -nocursor