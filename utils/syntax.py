from utils import ParserError
from const import *

MACHINE_DEFAULT, MACHINE_EXPR = range(2)
machine = []

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
