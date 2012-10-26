#!/usr/bin/python2

import sys


class ParserError(Exception): pass

def lex(text):
    import string

    assert len(text)>0


    NO, ALPHA, NUM, SYMB, CMDEND, QUOTE, QUOTE_end = range(7)
        
    def typeof(s):
        if s[0].isalpha():
            return ALPHA
        elif s[0].isdigit():
            return NUM
        elif s[0] in "=:><+*(){}":
            return SYMB
        elif s[0] in [';']:
            return CMDEND
        elif s[0] in ['"','\'']:
            return QUOTE
        elif s.strip() == "":
            return NO
        else:
            raise ParserError("Unknown symbol")

    def symb_check(t,s):
        COMBINATIONS = (':=', '**', )
        return (string.strip(string.join(t, ''))+s) in COMBINATIONS

    all_tokens = []
    token = []
    prev_type = current_type = typeof(text[0])
    string_token = ""

    for s in text:
        current_type = typeof(s)
        if prev_type == QUOTE:
            if current_type != QUOTE:
                string_token += s
            else:
                all_tokens.append(string_token)
                string_token = ""
                prev_type = QUOTE_end
                token = []
            continue
        if (prev_type == current_type) and (current_type == SYMB and symb_check(token, s)):
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
A_NO, A_ASSIGN, A_IF, A_POPEN, A_BEGIN, A_END, A_OPEREND, A_CTRLEND = range(8)
links = {
         START: ((VAR1, PRINT, IF, ), None),
         VAR1: ((ASSIGN, ), T_VAR),
         ASSIGN: ((EXPR1, ), T_EQ),
         EXPR1: ((OPEREND, ), None),
         PRINT: ((VAR2, STRING, ), None),
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
            print "Parsed expression: %s" % (res)
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
    gres.append(A_BEGIN)

    while True:
        token = (yield)
        ctype = typeof(token)
        if ctype == T_NO and token != None:
            raise ParserError("Unknown token '%s'" % token)

        #Process state
        if ctype == T_BEGIN:
            gres.append(A_BEGIN)
            continue
        
        if ctype == T_END:
            group = []
            assert len(gres)>0
            while True:
                last = gres.pop()
                if last != A_BEGIN:
                    group.append(last)
                else:
                    break
            gres.append(tuple(group))
            continue

        if ctype == T_OPEREND:
            operation = stack.pop()
            if operation == T_EQ:
                if ptype == EXPR1:
                    op = (EXPR1, [gres.pop(), global_stack.pop()])
                    gres.append(op)
                    ptype = START
            ptype = START
            waitfor = links[ptype][0]
            continue

        if ctype == T_VAR:
            gres.append(token)

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

def main():
    try:
        fl = sys.argv[1]
    except IndexError:
        print "ERROR: No file argument"
        return
    try:
        print synt(lex(file(fl).read()))
    except IOError:
        print "ERROR: File not found"
        return

if __name__ == '__main__':
    main()