NO, START, VAR1, VAR2, PRINT, IF, ASSIGN, STRING, EXPR1, EXPR2, \
    OPEREND, CTRLEND = range(12)
T_NO, T_IF, T_PRINT, T_VAR, T_NUMBER, T_STRING, T_OPEREND, T_CTRLEND, T_EQ, \
    T_PLUS, T_MINUS, T_MUL, T_DIV, T_POPEN, T_PCLOSE, T_BEGIN, T_END = range(17)
A_NO, A_ASSIGN, A_IF, A_BLOCK, A_PRINT = range(5)
NAMES = {
         A_NO: "<no>",
         A_ASSIGN: "=",
         A_IF: "if",
         A_BLOCK: "{block}",
         A_PRINT: "print",
        }

links = {
         START: ((VAR1, PRINT, IF, ), None),
         VAR1: ((ASSIGN, ), T_VAR),
         ASSIGN: ((EXPR1, ), T_EQ),
         EXPR1: ((OPEREND, ), None),
         PRINT: ((VAR2, STRING, ), T_PRINT),
         VAR2: ((OPEREND, ), T_VAR),
         STRING: ((OPEREND, ), T_STRING),
         IF: ((EXPR2, ), T_IF),
         EXPR2: ((CTRLEND, ), None),
         OPEREND: ((VAR1, PRINT, IF, ), T_OPEREND),
         CTRLEND: ((VAR1, PRINT, IF, ), T_CTRLEND),
        }
