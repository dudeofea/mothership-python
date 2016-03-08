all:
	gcc -shared -o engine_runner.so -fPIC engine_runner.c -Wall -I/usr/include/python2.7 -lpython2.7
