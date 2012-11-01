class ParserError(Exception): pass

import os, sys

from const import *

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

def verbose_output(func):
    def _verbose_output(*pargs, **kwargs):
        args = pargs[0]
        if not args.verbose:
            null_output = open(os.devnull, 'w')
            old_stdout = sys.stdout
            sys.stdout = null_output

        ret = func(*pargs, **kwargs)

        if not args.verbose:
            sys.stdout = old_stdout
        return ret
    return _verbose_output