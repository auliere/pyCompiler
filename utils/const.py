# State machine
NO, START, VAR1, VAR2, PRINT, IF, ASSIGN, STRING, EXPR1, EXPR2, \
    OPEREND, CTRLEND, ELSE, ENDIF, WHILE, ENDWHILE, EXPR3, FUNCTION, \
    FUNCNAME, FUNCARGSSTART, FUNCARGSEND, FUNCARG, FUNCARGSEP, RETURN, \
    VAR3, ENDFUNC, IFSEND, ELSESEND, ENDIFSEND, ASSIGNSEND , RETURNSEND, \
    PRINTSEND, READ, READSEND, VAR4, ENDWHILESEND, WHILESEND, \
    ENDFUNCSEND, BEG, END = range(40)

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

NAMES = {
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
START_LIST = (VAR1, PRINT, READ, IF, ELSE, ENDIF, WHILE, ENDWHILE, \
              FUNCTION, RETURN, ENDFUNC, BEG, END)

RANGES_LIST = (T_BEGIN, T_END)
LINE_END = (CTRLEND, OPEREND)
EXPRESSIONS_STATES = (EXPR1, EXPR2, EXPR3)

links = {
         START: (START_LIST, None),
         CTRLEND: (START_LIST, (T_CTRLEND,)),
         OPEREND: (START_LIST, (T_OPEREND,)),

         BEG: (START_LIST, (T_BEGIN,)),
         END: (START_LIST, (T_END,)),

         VAR1: ((ASSIGN, ), (T_VAR,)),
         ASSIGN: ((EXPR1, ), (T_EQ,)),
         EXPR1: ((ASSIGNSEND, ), None),
         ASSIGNSEND: (START_LIST, (T_OPEREND,)),

         PRINT: ((VAR2, STRING, ), (T_PRINT,)),
         VAR2: ((PRINTSEND, ), (T_VAR,)),
         STRING: ((PRINTSEND, ), (T_STRING,)),
         PRINTSEND: (START_LIST, (T_OPEREND,)),

         READ: ((VAR4, ), (T_READ,)),
         VAR4: ((READSEND, ), (T_VAR,)),
         READSEND: (START_LIST, (T_OPEREND,)),

         IF: ((EXPR2, ), (T_IF,)),
         EXPR2: ((IFSEND, ), None),
         IFSEND: (START_LIST, (T_CTRLEND,)),
         ELSE: ((ELSESEND,), (T_ELSE,)),
         ELSESEND: (START_LIST, (T_CTRLEND,)),
         ENDIF: ((ENDIFSEND,), (T_ENDIF,)),
         ENDIFSEND: (START_LIST, (T_OPEREND,)),

         WHILE: ((EXPR3, ), (T_WHILE,)),
         EXPR3: ((WHILESEND, ), None),
         WHILESEND: (START_LIST, (T_CTRLEND,)),
         ENDWHILE: ((ENDWHILESEND,), (T_ENDWHILE,)),
         ENDWHILESEND: (START_LIST, (T_OPEREND,)),

         FUNCTION: ( (FUNCNAME,), (T_FUNCTION,) ),
         FUNCNAME: ( (FUNCARGSSTART,), (T_VAR,) ),
         FUNCARGSSTART: ( (FUNCARGSEND, FUNCARG), (T_POPEN,) ),
         FUNCARG: ( (FUNCARGSEND, FUNCARGSEP), (T_VAR,) ),
         FUNCARGSEP: ( (FUNCARG, ), (T_SEPARATOR,) ),
         FUNCARGSEND: ( (START_LIST), (T_PCLOSE,) ),
         ENDFUNC: ((ENDFUNCSEND,), (T_ENDFUNC,)),
         ENDFUNCSEND: (START_LIST, (T_OPEREND,)),

         RETURN:  ( (VAR3,), (T_RETURN,) ),
         VAR3: ((RETURNSEND, ), (T_VAR,)),
         RETURNSEND: (START_LIST, (T_OPEREND,)),
        }

SYMB_DICT = {
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

RESERVED_WORDS = {
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
