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
                  ">": T_GT,
                  "<": T_LT,
                  ">=": T_GE,
                  "<=": T_LE,
                  '(': T_POPEN,
                  ')': T_PCLOSE,
                  '{': T_BEGIN,
                  '}': T_END,
                }
    word_dict = {
                  'if': T_IF,
                  'print': T_PRINT,
                  'read': T_READ,
                  'else': T_ELSE,
                  'endif': T_ENDIF,
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

def m_expressions():
    global global_lex
    stack = []
    res = []

    weights = {
                T_POPEN: 0,
                T_PCLOSE: 1,
                T_PLUS: 20,
                T_MINUS: 20,
                T_MUL: 10,
                T_DIV: 10,

                T_GT: 5,
                T_LT: 5,
                T_GE: 5,
                T_LE: 5,
                T_EQ: 5,

                T_OPEREND: -9000,
                T_CTRLEND: -9000,
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
        
        if token_type in [T_OPEREND, T_CTRLEND]:
            stack.pop()
            assert len(stack) == 0
            machine.pop()
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
            return token_type in links[state_type][1]

    def extract_block(stop):
        global gres
        group = []
        while True:
            if not len(gres)>0:
                raise ParserError("Syntax error")
            last = gres.pop()
            if last != stop:
                group.append(last)
            else:
                break
        gres.append((A_BLOCK, group))

    stack = []
    gres.append(A_BLOCK)

    while True:
        token = (yield)
        ctype = typeof(token)
        if ctype == T_NO and token != None:
            raise ParserError("Unknown token '%s' on line %d" % (token, token.line))

        #Process state
        if ctype == T_BEGIN:
            gres.append(A_BLOCK)
            continue
        
        elif ctype == T_END:
            group = []
            extract_block(A_BLOCK)
            gres.append((A_BLOCK, group))
            continue

        elif ctype == T_ELSE:
            stack.append(T_ELSE)

        elif ctype == T_ENDIF:
            stack.append(T_ENDIF)

        elif ctype == T_OPEREND:
            operation = stack.pop()
            if operation == T_EQ:
                if ptype == EXPR1:
                    op = (A_ASSIGN, [gres.pop(), global_stack.pop()])
                    gres.append(op)

            elif operation == T_PRINT:
                op = (A_PRINT, gres.pop())
                gres.append(op)

            elif operation == T_READ:
                op = (A_READ, gres.pop())
                gres.append(op)

            elif operation == T_ENDIF:
                extract_block(A_ELSE)
                elseblock = gres.pop()
                thenblock = gres.pop()
                op = (A_IF, [global_stack.pop(), thenblock, elseblock])
                gres.append(op)

            ptype = START
            waitfor = links[ptype][0]
            continue

        elif ctype == T_CTRLEND:
            operation = stack.pop()
            if operation == T_IF:
                gres.append(A_IF)

            if operation == T_ELSE:
                extract_block(A_IF) #THEN-block
                gres.append(A_ELSE)
            ptype = START
            waitfor = links[ptype][0]
            continue

        elif ctype == T_VAR:
            gres.append(token)

        elif ctype == T_STRING:
            gres.append(token)

        elif ctype in [T_PRINT, T_READ]:
            stack.append(ctype)

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
            stack.append(ctype)
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
