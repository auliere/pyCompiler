NO, START, VAR1, VAR2, PRINT, IF, ASSIGN, STRING, EXPR1, EXPR2, \
    OPEREND, CTRLEND, ELSE, ENDIF = range(14)
T_NO, T_IF, T_PRINT, T_READ, T_VAR, T_NUMBER, T_STRING, T_OPEREND, T_CTRLEND, T_EQ, \
    T_PLUS, T_MINUS, T_MUL, T_DIV, T_POPEN, T_PCLOSE, T_BEGIN, T_END, \
    T_LT, T_GT, T_GE, T_LE, T_ELSE, T_ENDIF = range(24)
A_NO, A_ASSIGN, A_IF, A_BLOCK, A_PRINT, A_ELSE, A_READ = range(7)

EXPRESSIONS_TOKENS = [T_VAR, T_NUMBER, T_STRING, T_EQ, \
                      T_PLUS, T_MINUS, T_MUL, T_DIV, T_LT, T_GT, T_GE, T_LE]

NAMES = {
         A_NO: "<no>",
         A_ASSIGN: "=",
         A_IF: "if",
         A_BLOCK: "{block}",
         A_PRINT: "print",
         A_READ: "read",
        }

START_LIST = (VAR1, PRINT, IF, ELSE, ENDIF)
RANGES_LIST = (T_BEGIN, T_END)
LINE_END = (CTRLEND, OPEREND)
links = {
         START: (START_LIST, None),
         VAR1: ((ASSIGN, ), (T_VAR,)),
         ASSIGN: ((EXPR1, ), (T_EQ,)),
         EXPR1: ((OPEREND, ), None),
         PRINT: ((VAR2, STRING, ), (T_PRINT, T_READ)),
         VAR2: ((OPEREND, ), (T_VAR,)),
         STRING: ((OPEREND, ), (T_STRING,)),
         IF: ((EXPR2, ), (T_IF,)),
         EXPR2: ((CTRLEND, ), None),
         OPEREND: (START_LIST, (T_OPEREND,)),
         CTRLEND: (START_LIST, (T_CTRLEND,)),
         ELSE: ((CTRLEND,), (T_ELSE,)),
         ENDIF: ((OPEREND,), (T_ENDIF,)),
        }

SYMB_DICT = {
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

RESERVED_WORDS = {
              'if': T_IF,
              'print': T_PRINT,
              'read': T_READ,
              'else': T_ELSE,
              'endif': T_ENDIF,
            }