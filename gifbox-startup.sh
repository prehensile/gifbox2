export GIFBOX_MEDIA=$GIFBOX_ROOT/media

# check wifi is connected, run wifi-connect if not
cd $GIFBOX_ROOT
./check_wifi.sh

screen -dm bash -c 'cd $GIFBOX_ROOT/server-local; ./run-server.sh; exec sh'
## will invoke xinitrc.sh 
startx -- -nocursor