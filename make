#!/bin/bash

python2 myl.py $1
[ $? -eq 0 ] && nasm -f elf "`basename $1 .src`.asm" && echo "Compiled successful"
[ $? -eq 0 ] && ld -s -lc -o "`basename $1 .src`.bin" "`basename $1 .src`.o" -dynamic-linker /lib/ld-linux.so.2 && echo "Linked successful"
