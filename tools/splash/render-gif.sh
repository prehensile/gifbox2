# use imagemagick to compile a gif from png files
convert -delay 2 startup/*.png startup.gif
# use gifsicle to optimise compiled gif
gifsicle --colors 8 --no-loopcount -O3 startup.gif > startup.o.gif