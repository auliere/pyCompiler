#!/usr/bin/python2

from __future__ import print_function

import sys
import string
import os

from utils.lexer import lex
from utils.syntax import synt
from utils.gen import find_vars, gen_code
from utils.const import NAMES

def print_tree(t, n=0, f=sys.stdout):
    if isinstance(t,list):
        for x in reversed(t):
            print_tree(x, n, f=f)
    elif isinstance(t,tuple):
        if t[0] in NAMES:
            print("--"*n, NAMES[t[0]], file=f)
        else:
            print("--"*n, t[0], file=f)
        print_tree(t[1], n=n+1, f=f)
    else:
        print("--"*n,t, file=f)

def main():
    try:
        fl = sys.argv[1]
    except IndexError:
        print("ERROR: No file argument", file=sys.stderr)
        sys.exit(-1)

    parts = fl.split('.')
    parts[-1] = 'lex'
    lex_file = string.join(parts,'.')

    parts[-1] = 'synt'
    tree_file = string.join(parts,'.')

    parts[-1] = 'asm'
    asmfile_name = string.join(parts,'.')

    try:
        print("Lexical analysis: ", end="")
        lex_l = lex(file(fl).read())
        print(lex_l, file=open(lex_file, 'w'))
        print("Done")
        
        print("Syntax analysis: ", end="")
        tree = synt(lex_l)
        tree_f = open(tree_file, 'w')
        print(tree, file=tree_f)
        print_tree(tree, f=tree_f)
        print("Done")

        print("Find variables and strings: ", end="")
        stat = find_vars(tree)
        print("vars =", stat.vars, file=tree_f)
        print("strs =", stat.strs, file=tree_f)
        print("Done")

        print("Generate NASM code: ", end="")
        asmfile = open(asmfile_name, 'w')
        gen_code(tree, os.path.basename(fl), stat, f=asmfile)
        print("Done")

    except IOError:
        print("ERROR: File not found", file=sys.stderr)
        sys.exit(-1)

if __name__ == '__main__':
    main()