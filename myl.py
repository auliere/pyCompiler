#!/usr/bin/python2

from __future__ import print_function

import sys
import string
import os
from time import gmtime, strftime

class ParserError(Exception): pass

def lex(text):
    assert len(text)>0


    NO, ALPHA, NUM, SYMB, CMDEND, QUOTE, QUOTE_end, COMMENT = range(8)
        
    def typeof(s, string=False):
        if s[0].isalpha():
            return ALPHA
        elif s[0].isdigit():
            return NUM
        elif s[0] in "=:><+-*/(){}":
            return SYMB
        elif s[0] in [';']:
            return CMDEND
        elif s[0] in ['"','\'']:
            return QUOTE
        elif s[0] in ['#']:
            return COMMENT
        elif s.strip() == "":
            return NO
        else:
            if not string:
                raise ParserError("Unknown symbol")

    def symb_check(t,s):
        COMBINATIONS = (':=', '**', )
        return (string.strip(string.join(t, ''))+s) in COMBINATIONS

    all_tokens = []
    token = []
    prev_type = current_type = typeof(text[0])
    string_token = ""
    inline_comment = False

    for s in text:
        if inline_comment:
            if s == '\n':
                inline_comment = False
            continue

        current_type = typeof(s, prev_type == QUOTE)

        if current_type == COMMENT:
            inline_comment = True
            continue

        if prev_type == QUOTE:
            if current_type != QUOTE:
                string_token += s
            else:
                all_tokens.append("\"%s\"" % string_token)
                string_token = ""
                prev_type = QUOTE_end
                token = []
            continue
        if (prev_type == current_type) and (current_type != SYMB or symb_check(token, s)):
            token.append(s)
        else:
            if prev_type != NO:
                clear_token = string.strip(string.join(token, ''))
                if len(clear_token)>0:
                    all_tokens.append(clear_token)
            prev_type = current_type
            token = [s]

    clear_token = string.strip(string.join(token, ''))
    if len(clear_token)>0:
        all_tokens.append(clear_token)
    return all_tokens



MACHINE_DEFAULT, MACHINE_EXPR = range(2)
machine = []

NO, START, VAR1, VAR2, PRINT, IF, ASSIGN, STRING, EXPR1, EXPR2, \
    OPEREND, CTRLEND = range(12)
T_NO, T_IF, T_PRINT, T_VAR, T_NUMBER, T_STRING, T_OPEREND, T_CTRLEND, T_EQ, \
    T_PLUS, T_MINUS, T_MUL, T_DIV, T_POPEN, T_PCLOSE, T_BEGIN, T_END = range(17)
A_NO, A_ASSIGN, A_IF, A_BLOCK, A_PRINT = range(5)
NAMES = {
         A_NO: "<no>",
         A_ASSIGN: "=",
         A_IF: "if",
         A_BLOCK: "{block}",
         A_PRINT: "print",
        }

links = {
         START: ((VAR1, PRINT, IF, ), None),
         VAR1: ((ASSIGN, ), T_VAR),
         ASSIGN: ((EXPR1, ), T_EQ),
         EXPR1: ((OPEREND, ), None),
         PRINT: ((VAR2, STRING, ), T_PRINT),
         VAR2: ((OPEREND, ), T_VAR),
         STRING: ((OPEREND, ), T_STRING),
         IF: ((EXPR2, ), T_IF),
         EXPR2: ((CTRLEND, ), None),
         OPEREND: ((VAR1, PRINT, IF, ), T_OPEREND),
         CTRLEND: ((VAR1, PRINT, IF, ), T_CTRLEND),
        }

def typeof(t):
    if t == None:
        return T_NO
    symb_dict = {
                  "=": T_EQ,
                  "+": T_PLUS,
                  "-": T_MINUS,
                  "*": T_MUL,
                  "/": T_DIV,
                  ";": T_OPEREND,
                  ":": T_CTRLEND,
                  '(': T_POPEN,
                  ')': T_PCLOSE,
                  '{': T_BEGIN,
                  '}': T_END,
                }
    word_dict = {
                  'if': T_IF,
                  'print': T_PRINT,
                }
    if t.isalpha():
        if t in word_dict:
            return word_dict[t]
        else: return T_VAR
    elif t.isdigit():
        return T_NUMBER
    elif t in symb_dict:
        return symb_dict[t]
    elif t[0] == '"' and t[-1] == '"':
        return T_STRING
    else:
        return T_NO

global_stack = []
gres = []
global_lex = []

labelNum = 0

def m_expressions():
    global global_lex
    stack = []
    res = []

    weights = {
                T_POPEN: 0,
                T_PCLOSE: 1,
                T_PLUS: 10,
                T_MINUS: 10,
                T_MUL: 20,
                T_DIV: 20,
                T_OPEREND: -9000,
              }

    while True:
        token = (yield)
        if token == None:
            continue
        token_type = typeof(token)
        if token_type in [T_VAR, T_NUMBER]:
            res.append(token)
            continue

        if token_type in [T_POPEN, ]:
            stack.append(token)
            continue

        while (len(stack) != 0) and (weights[token_type] <= weights[typeof(stack[-1])]):
            op = (stack[-1], res[-2:])
            del res[-2:]
            stack.pop()
            res.append(op)

        if token_type in [T_PCLOSE, ]:
            stack.pop()
            continue

        if len(stack)==0 or (weights[token_type] > weights[typeof(stack[-1])]):
            stack.append(token)
        
        if token_type == T_OPEREND:
            stack.pop()
            assert len(stack) == 0
            machine.pop()
#            print "Parsed expression: %s" % (res)
            global_stack.append(res)
            global_lex.append(token)

def m_default():
    global gres, global_lex
    ptype = START
    waitfor = links[ptype][0]

    def istypeeq(token_type, state_type):
        if state_type == None:
            return True
        else:
            return token_type == links[state_type][1]

    stack = []
    gres.append(A_BLOCK)

    while True:
        token = (yield)
        ctype = typeof(token)
        if ctype == T_NO and token != None:
            raise ParserError("Unknown token '%s'" % token)

        #Process state
        if ctype == T_BEGIN:
            gres.append(A_BLOCK)
            continue
        
        if ctype == T_END:
            group = []
            while True:
                if not len(gres)>0:
                    raise ParserError("Syntax error")
                last = gres.pop()
                if last != A_BLOCK:
                    group.append(last)
                else:
                    break
            gres.append((A_BLOCK, group))
            continue

        if ctype == T_OPEREND:
            operation = stack.pop()
            if operation == T_EQ:
                if ptype == EXPR1:
                    op = (A_ASSIGN, [gres.pop(), global_stack.pop()])
                    gres.append(op)

            if operation == T_PRINT:
                op = (A_PRINT, gres.pop())
                gres.append(op)

            ptype = START
            waitfor = links[ptype][0]
            continue

        if ctype == T_VAR:
            gres.append(token)

        if ctype == T_STRING:
            gres.append(token)

        if ctype == T_PRINT:
            stack.append(T_PRINT)

        #print token, ctype, ptype

        #Next state
        possibles = []

        if len(waitfor) == 1: #single transition
            possibles.append(waitfor[0])
        else:
            for possible in waitfor:
                if istypeeq(typeof(token), possible):
                    possibles.append(possible)
        if len(possibles) > 1:
            raise ParserError("Syntax error: Ambiguity")
        if len(possibles) == 0:
            raise ParserError("Syntax error")

        ptype = possibles[0]
        waitfor = links[ptype][0]

        if len(waitfor) == 1 and waitfor[0] in [EXPR1, EXPR2]:
            m = m_expressions()
            m.next()
            machine.append(m)
            stack.append(waitfor[0])
            ptype = waitfor[0]

def synt(lex):
    global global_lex
    def_machine = m_default()
    def_machine.next()
    #INIT
    machine.append(def_machine)

    global_lex = list(reversed(lex))
    while len(global_lex) > 0:
        token = global_lex.pop()
        machine[-1].send(token)

    def_machine.send('}')
    # def_machine.send(None)
    return gres

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
        vars, strs = find_vars(tree)
        print("vars =", vars, file=tree_f)
        print("strs =", strs, file=tree_f)
        print("Done")

        print("Generate NASM code: ", end="")
        asmfile = open(asmfile_name, 'w')
        gen_code(tree, os.path.basename(fl), vars, strs, f=asmfile)
        print("Done")

    except IOError:
        print("ERROR: File not found", file=sys.stderr)
        sys.exit(-1)

if __name__ == '__main__':
    main()