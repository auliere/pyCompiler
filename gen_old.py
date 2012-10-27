def m_default():
    weights = {
                A_BEGIN: 0,
                A_END: 1,
                A_OPEREND: -9000,
                A_CTRLEND: -9000,
                A_ASSIGN: 500,
              }

    tweights = {
                T_BEGIN: 0,
                T_END: 1,
                T_OPEREND: -9000,
                T_CTRLEND: -9000,
                T_EQ: 500,
              }

    def istypeeq(token_type, state_type):
        if state_type == None:
            return True
        else:
            return token_type == links[state_type][1]

    ptype = START
    waitfor = links[ptype][0]

    stack = []

    while True:
        token = (yield)
        ctype = typeof(token)

        if ctype == T_NO and token != None:
            raise ParserError("Unknown token '%s'" % token)

        if ctype == T_BEGIN:
            stack.append(A_BEGIN)
            continue

        if ctype == T_OPEREND:
            if stack[-1] in [EXPR1, EXPR2]:
                if ptype == EXPR1:
                    op = (EXPR1, [gres.pop(), global_stack.pop()])
                    gres.append(op)
                    ptype = START
            continue

        if ctype == T_VAR:
            gres.append(token)

        if ctype == T_EQ:
            stack.append(ASSIGN)

        # while (len(stack) != 0) and (tweights[ctype] <= weights[stack[-1]]):
        #     # op = (stack[-1], gres[-2:])
        #     # del gres[-2:]
        #     # stack.pop()
        #     # gres.append(op)
        #     if stack[-1] in [A_ASSIGN, ]:
        #         gres.append( (A_ASSIGN, gres[-2:]) )
        #         del gres[-2:]
        #         stack.pop()

        if ctype in [T_END, ]:
            stack.pop()
            continue

        print token, ctype, ptype
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