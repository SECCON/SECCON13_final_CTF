#!/usr/bin/env python3
from elftools.elf.elffile import ELFFile

binfile = "./MPartTimer"

st_size = None
st_value = None

symbol_name = "src"
f = open(binfile, 'rb')
elffile = ELFFile(f)
symtab = elffile.get_section_by_name(".symtab")
for symbol in symtab.iter_symbols():
    if symbol.name == symbol_name:
        st_size = symbol["st_size"]
        st_value = symbol["st_value"]
        break
if st_size is None and st_value is None:
    raise Exception("Symbol not found")

target_section = None
for section in elffile.iter_sections():
    if section.header['sh_addr'] <= st_value < (section.header['sh_addr'] + section.header['sh_size']):
        target_section = section
        break
if not target_section:
    raise Exception("Section not found")

section_offset = target_section.header["sh_offset"]
section_addr = target_section.header["sh_addr"]

file_offset = section_offset + (st_value - section_addr)

f.seek(0)
f.seek(file_offset)
data = f.read(st_size)
open("extract.mrb", "wb").write(data)
