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
        elif s[0] in "=:><+":
            return SYMB
        elif s[0] in [';']:
            return CMDEND
        elif s[0] in ['"','\'']:
            return QUOTE
        else: return NO

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
        if (prev_type == current_type):
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
machine = [MACHINE_DEFAULT]

NO, START, VAR1, VAR2, PRINT, IF, ASSIGN, STRING, EXPR1, EXPR2, \
    OPEREND, CTRLEND = range(12)
T_NO, T_IF, T_PRINT, T_VAR, T_NUMBER, T_STRING, T_OPEREND, T_CTRLEND, T_EQ = range(9)
T_PLUS, T_MINUS, T_MUL, T_DIV = range(9, 13)
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
         OPEREND: (None, T_OPEREND),
         CTRLEND: (None, T_CTRLEND),
        }

def typeof(t):
    if t.isalpha():
        if (t == 'if'):
            return T_IF
        elif (t == 'print'):
            return T_PRINT
        else: return T_VAR
    elif t.isdigit():
        return T_NUMBER
    elif t in "=":
        return T_EQ
    elif t in "+":
        return T_PLUS
    else:
        return T_NO

def m_default():
    def istypeeq(token_type, state_type):
        if state_type == None:
            return True
        else:
            return token_type == links[state_type][1]

    ptype = START
    waitfor = links[ptype][0]

    while True:
        token = (yield)
        print token
        ctype = typeof(token)
        if ctype == T_NO:
            raise ParserError("Unknown token '%s'" % token)

        possibles = []
        if len(waitfor) == 1: #single transition
            # if istypeeq(typeof(token), waitfor[0]):
            possibles.append(waitfor[0])
            # else:
            #     raise ParserError("Unexpected token '%s'" % token)
        else:
            for possible in waitfor:
                if istypeeq(typeof(token), possible):
                    possibles.append(possible)
        if len(possibles) > 1:
            raise ParserError("Syntax error: Ambiguity")
        if len(possibles) == 0:
            raise ParserError("Syntax error")


        ptype = possibles[0]
        #print ctype
        waitfor = links[ptype][0]

        


        if ptype in [EXPR1, EXPR2]:
            machine.append(MACHINE_EXPR)

def m_expressions():
    #TODO
    stack = []
    while True:
        token = (yield)
        token_type = typeof(token)
        if token_type == T_VAR:
            stack.append(token)
        print "e:%s" % token

def synt(lex):
    def_machine = m_default()
    expr_machine = m_expressions()
    #INIT
    def_machine.next()
    expr_machine.next()

    for token in lex:
        print token,machine,
        if machine[-1] == MACHINE_DEFAULT:
            def_machine.send(token)
        elif machine[-1] == MACHINE_EXPR:
            expr_machine.send(token)

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