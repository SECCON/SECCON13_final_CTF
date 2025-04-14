all:
	gcc main.c -o ../files/prog-2 -O0
	strip --strip-all ../files/prog-2
	upx ../files/prog-2
	python gen.py ../files/prog-2

weak:
	gcc weak.c -o weak-2 -O3

ans:
	gcc ans.c -o ans-2 -O3 -mcrc32
