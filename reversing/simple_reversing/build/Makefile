CFLAGS += $(shell mruby-config --cflags)
LDFLAGS += $(shell mruby-config --ldflags)
LIBFLAGS += $(shell mruby-config --libs)
CC = gcc
SRC = main.c
MRBC = mrbc
MRBC_FLAG = -Bsrc
RB_SRC = src.rb
GENERATED = src.c
TARGET = simple_reversing


all: $(TARGET)
	cp $(TARGET) ../files/simple_reversing
	strip ../files/simple_reversing

$(TARGET): $(SRC) $(GENERATED)
	$(CC) $(CFLAGS) $(LDFLAGS) $(GENERATED) $(SRC) $(LIBFLAGS) -o $(TARGET)

$(GENERATED): $(RB_SRC)
	$(MRBC) $(MRBC_FLAG) -o $(GENERATED) $(RB_SRC)
	sed -i 's/0x4d,0x41,0x54,0x5a/0x58,0x58,0x58,0x58/g' $(GENERATED)


clean:
	rm -f $(TARGET) $(GENERATED)


.PHONY: all clean
