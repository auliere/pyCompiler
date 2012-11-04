from __future__ import print_function

import sys
from time import gmtime, strftime

from utils.const import *
from utils import ParserError, typeof

class TreeStats(object):
    def __init__(self, vars=None, strs=None):
        if vars is None:
            vars = []
        if strs is None:
            strs = []

        self.vars = vars
        self.strs = strs
        self.use_print = False
        self.use_read = False

def find_vars(t, stat=None):
    if stat == None:
        stat = TreeStats()
    if isinstance(t,list):
        for x in reversed(t):
            find_vars(x, stat=stat)
    elif isinstance(t,tuple):
        if t[0] == A_PRINT:
            stat.use_print = True
        elif t[0] == A_READ:
            stat.use_read = True
        find_vars(t[1], stat=stat)
    else:
        if isinstance(t, str) and typeof(t) == T_VAR:
            if t not in stat.vars:
                stat.vars.append(t)
        if isinstance(t, str) and typeof(t) == T_STRING:
            if t not in stat.strs:
                stat.strs.append(t)
    return stat

ifNum = 0
labelNum = 0

def gen_text_section(t, stat, f=sys.stdout):
    global labelNum, ifNum
    iterate = t
    if isinstance(t, list):
        iterate = reversed(t)
    if isinstance(t, (str, tuple)):
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
            gen_text_section(node[1], stat, f=f)

        elif node[0] == A_PRINT:
            if typeof(node[1]) == T_STRING:
                strnum = stat.strs.index(node[1])
                print("push dword str%d\n" % strnum +
                      "call printf\n"
                      "add esp, 4\n"
                      "push dword [stdout]\n"
                      "call fflush\n"
                      "add esp, 4\n"
                    , file=f)
            elif typeof(node[1]) == T_VAR:
                print("mov eax, [v%s]\n" % node[1] +
                      "push dword eax\n"
                      "push dword numbs\n"
                      "call printf\n"
                      "add esp, 8\n"
                      "push dword [stdout]\n"
                      "call fflush\n"
                      "add esp, 4\n"
                      , file=f)
            else:
                raise ParserError("Error print argument: %s" % node)

        elif node[0] == A_READ:
            assert typeof(node[1]) == T_VAR
            print("push v%s\n" % node[1] +
                  "push dword numbs_in_format\n"
                  "call scanf\n"
                  "add esp, 8\n"
                  "call getchar\n"
                  , file=f)

        elif node[0] == A_ASSIGN:
            var = node[1][0]
            gen_text_section(node[1][1], stat, f=f)
            print("pop eax", file=f)
            print("mov [v%s], eax" % var, file=f)

        elif node[0] == A_IF:
            ifNum += 1
            gen_text_section(node[1][0], stat, f=f)
            print("pop eax\n"
                  "cmp eax,0\n"
                  "jnz llif%delse\n" % ifNum
                , file=f)
            gen_text_section(node[1][1], stat, f=f)
            print("jmp llif%dend\n" % ifNum +
                  "llif%delse: nop\n" % ifNum
                , file=f)
            gen_text_section(node[1][2], stat, f=f)
            print("llif%dend: nop" % ifNum
                , file=f)

        elif node[0] == '+':
            gen_text_section(node[1], stat, f=f)
            print("pop eax\n"
                  "pop ebx\n"
                  "add eax,ebx\n"
                  "push dword eax"
                  , file=f)

        elif node[0] in ['>=', '<=', '>', '<', '=']:
            gen_text_section(node[1], stat, f=f)
            labelNum += 1
            op = {'>=': 'jge',
                  '<=': 'jle',
                  '>': 'jg',
                  '<': 'jl',
                  '=': 'je',
                 }
            print("pop eax\n"
                  "pop ebx\n"
                  "cmp eax,ebx\n"
                  "%s ll%d\n" % (op[node[0]], labelNum) +
                  "push dword 1\n"
                  "jmp ell%d\n" % labelNum +
                  "ll%d: push dword 0\n" % labelNum +
                  "ell%d: nop" % labelNum
                  , file=f)

        elif node[0] == '-':
            gen_text_section(node[1], stat, f=f)
            print("pop eax\n"
                  "pop ebx\n"
                  "sub eax,ebx\n"
                  "push dword eax"
                  , file=f)

        elif node[0] in ['*','/']:
            raise NotImplementedError("%s operation is not implemented yet" % node[0])
        else:
            raise ParserError("Error generating ASM code on node %s" % repr(node))

    print("", file=f)

def clear_string(s):
    r = s
    r = "\",10,\"".join(r.split("\\n"))
    return r

def gen_code(t, srcfile, stat, f=sys.stdout):
    print("; Source file: %s" % srcfile, file=f)
    print("; Generated %s" % strftime("%Y-%m-%d %H:%M:%S", gmtime()), file=f)
    print("", file=f)
    print("SECTION .data", file=f)

    print("\n;Strings", file=f)
    for i,vs in enumerate(stat.strs):
        s = clear_string(vs)
        print('str%d: db %s,0' % (i,s), file=f)
        print('lstr%d: equ $-str%d' % (i,i), file=f)
    print('numbs: db \"%i\",0', file=f)
    print('numbs_in_format: db \"%i\"', file=f)

    print("\n;Variables", file=f)
    for i,vs in enumerate(stat.vars):
        print('v%s: db 0' % vs, file=f)

    print("", file=f)
    print("SECTION .text", file=f)
    print("global _start", file=f)
    extern = []
    if stat.use_print:
        extern.append("printf")
    if stat.use_read:
        extern.append("scanf")
        extern.append("getchar")
    if stat.use_read or stat.use_print:
        extern.append("fflush")
        extern.append("stdout")

    for e in extern:
      print("extern %s" % e, file=f)

    print("_start: ", file=f)
    print("push ebp ; setup stack frame", file=f)
    print("mov ebp,esp", file=f)

    print("", file=f)
    gen_text_section(t, stat, f=f)
    
    #end
    print("mov esp, ebp ; restore stack frame", file=f)
    print("pop ebp", file=f)
    print("mov ebx, 0 ; exit code 0", file=f)
    print("mov eax, 1 ; exit command to kernel", file=f)
    print("int 0x80", file=f)