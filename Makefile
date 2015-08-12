PREFIX = /usr
CC = gcc
COPTIONS = -Wall -g -O4
CLIBS = -luvc -ljpeg -lpng -lm -I/usr/X11R6/include/ -L/usr/X11R6/lib/ -lXext -lX11


gugusse: gugusse.o x_lowlevel.o
	$(CC) $(COPTIONS) -o gugusse gugusse.o x_lowlevel.o $(CLIBS)

gugusse.o: gugusse.c x_lowlevel.h stills2dv.h
	$(CC) $(COPTIONS) -c gugusse.c

x_lowlevel.o: x_lowlevel.c x_lowlevel.h stills2dv.h
	$(CC) $(COPTIONS) -c x_lowlevel.c


clean:
	rm -f *~ *.o gugusse

