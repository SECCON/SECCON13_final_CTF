all:
	luac -o main.luac main.lua
	gcc -L/home/ptr/.anyenv/envs/luaenv/versions/5.4.6/lib \
      -I/home/ptr/.anyenv/envs/luaenv/versions/5.4.6/include \
      main.c -o ../files/prog-5 -llua -lm -static
	rm main.luac

weak:
	gcc -O3 weak.c -o weak-5

ans:
	gcc -O3 -mavx2 ans.c -o ans-5
