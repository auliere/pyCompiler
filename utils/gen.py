from __future__ import print_function

import sys
from utils.const import *
from time import gmtime, strftime
from utils.syntax import typeof

def find_vars(t, vars=[], strs=[]):
    if isinstance(t,list):
        for x in reversed(t):
            find_vars(x)
    elif isinstance(t,tuple):
        find_vars(t[1])
    else:
        if isinstance(t, str) and typeof(t) == T_VAR:
            if t not in vars:
                vars.append(t)
        if isinstance(t, str) and typeof(t) == T_STRING:
            if t not in strs:
                strs.append(t)
    return vars, strs

def gen_text_section(t, vars, strs, f=sys.stdout):
    global labelNum
    iterate = t
    if isinstance(t, list):
        iterate = reversed(t)
    if isinstance(t, str):
        iterate = [t]
    for node in iterate:
        if isinstance(node, str):
            tnode = typeof(node)
            if tnode == T_NUMBER:
                print("push dword %s" % node, file=f)
            elif tnode == T_VAR:
                print("push dword [v%s]" % node, file=f)
            else:
                raise ParserError("Error generating ASM code on node %s" % node)

        elif node[0] == A_BLOCK:
            gen_text_section(node[1], vars, strs, f=f)

        elif node[0] == A_PRINT:
            if typeof(node[1]) == T_STRING:
                strnum = strs.index(node[1])
                print("push dword str%d\n" % strnum +
                      "call printf\n"
                      "add esp, 4"
                    , file=f)
            elif typeof(node[1]) == T_VAR:
                print("mov eax, [v%s]\n" % node[1] +
                      "push dword eax\n"
                      "push dword numbs\n"
                      "call printf\n"
                      "add esp, 8"
                      , file=f)
            else:
                raise ParserError("Error print argument: %s" % node)

        elif node[0] == A_ASSIGN:
            var = node[1][0]
            gen_text_section(node[1][1], vars, strs, f=f)
            print("pop eax", file=f)
            print("mov [v%s], eax" % var, file=f)

        elif node[0] == '+':
            gen_text_section(node[1], vars, strs, f=f)
            print("pop eax\n"
                  "pop ebx\n"
                  "add eax,ebx\n"
                  "push dword eax"
                  , file=f)

        elif node[0] == '-':
            gen_text_section(node[1], vars, strs, f=f)
            print("pop eax\n"
                  "pop ebx\n"
                  "sub eax,ebx\n"
                  "push dword eax"
                  , file=f)

        else:
            raise ParserError("Error generating ASM code on node %s" % node)

    print("", file=f)

def clear_string(s):
    r = s
    r = "\",10,\"".join(r.split("\\n"))
    return r

def gen_code(t, srcfile, vars, strs, f=sys.stdout):
    print("; Source file: %s" % srcfile, file=f)
    print("; Generated %s" % strftime("%Y-%m-%d %H:%M:%S", gmtime()), file=f)
    print("", file=f)
    print("SECTION .data", file=f)
    
    print("\n;Strings", file=f)
    for i,vs in enumerate(strs):
        s = clear_string(vs)
        print('str%d: db %s,0' % (i,s), file=f)
        print('lstr%d: equ $-str%d' % (i,i), file=f)
    print('numbs: db \"%d\",0', file=f)

    print("\n;Variables", file=f)
    for i,vs in enumerate(vars):
        print('v%s: db 0' % vs, file=f)
    print('svD: db 0 ; symbol out', file=f)
    print('svDS: dd 0 ; numsave', file=f)

    print("", file=f)
    print("SECTION .text", file=f)
    print("global _start", file=f)
    print("extern printf", file=f)

    print("_start: ", file=f)
    print("push ebp ; setup stack frame", file=f)
    print("mov ebp,esp", file=f)

    print("", file=f)
    gen_text_section(t, vars, strs, f=f)
    
    #end
    print("mov esp, ebp ; restore stack frame", file=f)
    print("pop ebp", file=f)
    print("mov ebx, 0 ; exit code 0", file=f)
    print("mov eax, 1 ; exit command to kernel", file=f)
    print("int 0x80", file=f)