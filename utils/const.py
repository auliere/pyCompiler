# Token types
T_NO, T_IF, T_PRINT, T_READ, T_VAR, T_NUMBER, T_STRING, T_OPEREND, T_CTRLEND, \
    T_EQ, T_PLUS, T_MINUS, T_IMUL, T_IDIV, T_POPEN, T_PCLOSE, T_BEGIN, T_END, \
    T_LT, T_GT, T_GE, T_LE, T_ELSE, T_ENDIF, T_WHILE, T_ENDWHILE, T_MOD,\
    T_FUNCTION, T_SEPARATOR, T_RETURN, T_ENDFUNC, T_CALL = range(32)

# Tree blocks
A_NO, A_ASSIGN, A_IF, A_BLOCK, A_PRINT, A_ELSE, A_READ, A_WHILE, A_FUNCTION, \
    A_RETURN, A_CALL = range(11)

# Asm command type
# C_EQU_F is $-label
C_NO, C_ADD, C_SUB, C_PUSH, C_POP, C_CALL, C_PRINT, C_COMMENT, C_READ, C_MOV, \
    C_CMP, C_DB, C_DD, C_EQU, C_EQU_F, C_EXTRN, C_GLOBL, C_LABEL, C_INT, C_JMP, \
    C_IMUL, C_IDIV, C_RET, C_NEG = range(24)

C_OPT_NO, C_OPT_ADDR, C_PRINT_STR, C_PRINT_VAR = range(4)


EXPRESSIONS_TOKENS = [T_VAR, T_NUMBER, T_STRING, T_EQ,
                      T_PLUS, T_MINUS, T_IMUL, T_IDIV, T_MOD,
                      T_LT, T_GT, T_GE, T_LE, T_POPEN, T_PCLOSE,
                      T_SEPARATOR, ]

NAMES = \
    {
        A_NO: "<no>",
        A_ASSIGN: "=",
        A_IF: "if",
        A_BLOCK: "{block}",
        A_PRINT: "print",
        A_READ: "read",
        A_WHILE: "while",
        A_FUNCTION: "function",
        A_RETURN: "return",
        A_CALL: "call",
    }

# line start states
START_LIST = []  # gen

RANGES_LIST = (T_BEGIN, T_END)
EXPRESSIONS_STATES = None  # gen

START_NODE = -1

links = \
    {  # gen
    }

SYMB_DICT = \
    {
        "=": T_EQ,
        "+": T_PLUS,
        "-": T_MINUS,
        "*": T_IMUL,
        "/": T_IDIV,
        "%": T_MOD,
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
        ',': T_SEPARATOR,
    }

RESERVED_WORDS = \
    {
        'if': T_IF,
        'print': T_PRINT,
        'read': T_READ,
        'else': T_ELSE,
        'endif': T_ENDIF,
        'while': T_WHILE,
        'endwhile': T_ENDWHILE,
        'function': T_FUNCTION,
        'return': T_RETURN,
        'endfunc': T_ENDFUNC,
    }

from graph import read_syntax_graph
import sys
read_syntax_graph(sys.modules[__name__])
