class ParserError(Exception): pass

import os, sys

from const import *

def typeof(t):
    if t == None:
        return T_NO

    if t.isalpha():
        if t in RESERVED_WORDS:
            return RESERVED_WORDS[t]
        else: return T_VAR
    elif t.isdigit():
        return T_NUMBER
    elif t in SYMB_DICT:
        return SYMB_DICT[t]
    elif t[0] == '"' and t[-1] == '"':
        return T_STRING
    elif t.isalnum():
        return T_VAR
    else:
        return T_NO

def verbose_output(func):
    """ 
    Suppresses output if --verbose was not set
    """
    def _verbose_output(*pargs, **kwargs):
        args = pargs[0]
        old_stdout = sys.stdout
        if not args.verbose:
            null_output = open(os.devnull, 'w')
            sys.stdout = null_output
        try:
          ret = func(*pargs, **kwargs)
          if not args.verbose:
                sys.stdout = old_stdout
        except:
            #fallback
            if not args.verbose:
                sys.stdout = old_stdout
            raise
        return ret
    return _verbose_output