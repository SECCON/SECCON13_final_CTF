all:
	pyinstaller --onefile main.py
	mv dist/main ../files/prog-4
	rm -r build dist main.spec

weak-ans:
	pyinstaller --onefile weak.py
	mv dist/weak weak-4
	rm -r build dist weak.spec

ans:
	gcc ans.c -o ans-4 -O3 -lcrypto
