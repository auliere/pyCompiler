#-*- coding: utf8 -*-

" Syntax analyser "

from __future__ import print_function

import sys

from utils import ParserError
from const import *
from . import typeof, FunctionCallInfo

MACHINE_DEFAULT, MACHINE_EXPR = range(2)
machine = []

DEBUG = False

def synt(lex):
    " Builds syntax tree "
    global global_lex, global_stack, gres
    global_lex = []
    global_stack = []
    gres = []
    def_machine = m_default()
    def_machine.next()
    #INIT
    machine.append(def_machine)

    global_lex = list(reversed(lex))
    while len(global_lex) > 0:
        token = global_lex.pop()
        machine[-1].send(token)

    def_machine.send('}')
    return gres

global_stack = []
gres = []
global_lex = []

def m_expressions():
    " Machine for expression analysis "
    global global_lex
    stack = []
    res = []

    weights = {
                T_POPEN: 0,
                T_CALL: 0,
                T_PCLOSE: 1,
                T_SEPARATOR: 2,
                T_PLUS: 20,
                T_MINUS: 20,
                T_IMUL: 10,
                T_IDIV: 10,
                T_MOD: 10,

                T_GT: 5,
                T_LT: 5,
                T_GE: 5,
                T_LE: 5,
                T_EQ: 5,

                T_OPEREND: -9000,
                T_CTRLEND: -9000,
              }

    current_line = -1

    while True:
        token = (yield)
        if token == None:
            continue

        if hasattr(token, 'line'):
            current_line = token.line

        token_type = typeof(token)

        if token_type not in [T_OPEREND, T_CTRLEND] + EXPRESSIONS_TOKENS:
            raise ParserError('Syntax error on line %d' % current_line)

        if token_type in [T_VAR, T_NUMBER]:
            res.append(token)
            #FIXME: replace by logging
            if DEBUG:
                print (stack, res)
            continue

        if token_type in [T_POPEN, ]: #parentheses or function call
            if (len(res) > 0) and typeof(res[-1]) == T_VAR:
                stack.append(FunctionCallInfo(res.pop(), len(res)))
            else:
                stack.append(token)
            if DEBUG:
                print (stack, res)
            continue

        while (len(stack) != 0) and \
              (weights[token_type] <= weights[typeof(stack[-1])]):
            operation = (stack[-1], res[-2:])
            del res[-2:]
            stack.pop()
            res.append(operation)

        if token_type in [T_PCLOSE, ]:
            oper = stack.pop()
            if typeof(oper) == T_CALL:
                assert isinstance(oper, FunctionCallInfo)
                #function
                args_count = len(res)-oper.args
                if DEBUG:
                    print (oper, args_count, res[-args_count:])
                if args_count > 0:
                    args = res[-args_count:]
                    del res[-args_count:]
                else:
                    args = []
                res.append( (A_CALL, oper, args) )

            if DEBUG: 
                print (stack, res)
            continue

        if len(stack)==0 or (weights[token_type] > weights[typeof(stack[-1])]):
            if token_type != T_SEPARATOR:
                stack.append(token)

        if DEBUG: 
            print (stack, res)

        if token_type not in EXPRESSIONS_TOKENS:
            stack.pop()
            assert len(stack) == 0
            machine.pop()
            global_stack.append(res)
            global_lex.append(token)

class FunctionDescription(object):
    def __init__(self):
        self.name = None
        self.args = []
        self.inner_vars = []
    def __repr__(self):
        return "%s%s" % (self.name, self.args)

def m_default():
    global gres, global_lex
    ptype = START
    waitfor = links[ptype][0]

    def istypeeq(token_type, state_type):
        if state_type == None:
            return True
        else:
            return token_type in links[state_type][1]

    def extract_block(stop):
        global gres
        group = []
        while True:
            if not len(gres)>0:
                raise ParserError("Syntax error: invalid block")
            last = gres.pop()
            if last != stop:
                group.append(last)
            else:
                break
        gres.append((A_BLOCK, group))

    stack = []
    gres.append(A_BLOCK)
    current_line = -1
    func = None

    while True:
        token = (yield)
        if hasattr(token, 'line'):
            current_line = token.line

        if ptype in EXPRESSIONS_STATES: # processed in other machine, so waiting for ';' or ':'
            waitfor = links[ptype][0]

        ctype = typeof(token)

        # check syntax errors
        possibles = reduce(lambda a,b: a+b, [[] if links[x][1] == None else list(links[x][1]) for x in waitfor])
        if possibles is None:
            possibles = []
        else:
            possibles = list(possibles)
        possibles += RANGES_LIST
        if possibles is not None and ctype not in possibles:
            raise ParserError('Syntax error on line %d' % current_line)
        if ctype == T_NO and token != None:
            # FIXME: dead code?
            raise ParserError("Unknown token '%s' on line %d" % (token, current_line))

        
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

        #Process state

        if ptype == FUNCTION:
            func = FunctionDescription()

        elif ptype == FUNCNAME:
            func.name = token

        elif ptype == FUNCARG:
            func.args.append(token)

        elif ptype == FUNCARGSEND:
            gres.append(A_FUNCTION)

        elif ptype == BEG:
            gres.append(A_BLOCK)

        elif ptype == END:
            group = []
            extract_block(A_BLOCK)
            if len(group)>0:
                gres.append((A_BLOCK, group))

        elif ptype in [VAR1, VAR2, VAR3, VAR4]:
            gres.append(token)

        elif ptype == STRING:
            gres.append(token)

        elif ptype == IFSEND:
            gres.append(A_IF)

        elif ptype == ELSESEND:
            extract_block(A_IF) #THEN-block
            gres.append(A_ELSE)

        elif ptype == ENDIFSEND:
            extract_block(A_ELSE)
            elseblock = gres.pop()
            thenblock = gres.pop()
            oper = (A_IF, [global_stack.pop(), thenblock, elseblock])
            # print (op)
            gres.append(oper)

        elif ptype == ENDFUNCSEND:
            extract_block(A_FUNCTION)
            block = gres.pop()
            op = (A_FUNCTION, [func, block])
            gres.append(op)

        elif ptype == ASSIGNSEND:
            oper = (A_ASSIGN, [gres.pop(), global_stack.pop()])
            gres.append(oper)

        elif ptype == RETURNSEND:
            oper = (A_RETURN, gres.pop())
            gres.append(oper)

        elif ptype == PRINTSEND:
            oper = (A_PRINT, gres.pop())
            gres.append(oper)

        elif ptype == READSEND:
            oper = (A_READ, gres.pop())
            gres.append(oper)

        elif ptype == WHILESEND:
            gres.append(A_WHILE)

        elif ptype == ENDWHILESEND:
            extract_block(A_WHILE)
            block = gres.pop()
            op = (A_WHILE, [global_stack.pop(), block])
            gres.append(op)
        
        waitfor = links[ptype][0]

        if len(waitfor) == 1 and waitfor[0] in EXPRESSIONS_STATES:
            m = m_expressions()
            m.next()
            machine.append(m)
            stack.append(ctype)
            ptype = waitfor[0]

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