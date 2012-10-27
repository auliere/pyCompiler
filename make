#!/bin/bash

python2 myl.py "$1"
[ $? -eq 0 ] && nasm -f elf "`dirname $1`/`basename $1 .src`.asm" &&\
 echo "Compiled successful"
[ $? -eq 0 ] && ld -s -lc -o "`dirname $1`/`basename $1 .src`.bin" \
 "`dirname $1`/`basename $1 .src`.o" \
 -dynamic-linker /lib/ld-linux.so.2 && echo "Linked successful"
