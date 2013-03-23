
from utils.const import *
from utils.gen import PseudoAsm


def optimize(pseudo, num=2):
    text = pseudo
    for x in xrange(num):
        text = do_optimize(text)
    return text


def do_optimize(pseudo):
    pseudo = PseudoAsm(pseudo)

    text = pseudo.text
    text = optimize_push_pop(text)
    text = optimize_mov(text)
    text = optimize_mov_push(text)
    text = optimize_mov_to_self(text)
    text = optimize_clean_lines(text)

    pseudo.text = text
    return pseudo


def optimize_mov_to_self(text):
    " reduce mov (mov eax,eax) "
    result = []
    for i, op in enumerate(text):
        if op[0] == C_MOV:
            if (op[2][0] == op[2][1]) and (op[1][0] == op[1][1]):
                pass
            else:
                result.append(op)
        else:
            result.append(op)
    return result


def optimize_push_pop(text):
    " reduce push and pop sequences "
    stack = []
    result = []
    ires = []
    for i, op in enumerate(text):
        if len(op) > 3:
            offset = op[3]
        else:
            offset = 0

        if op[0] == C_PUSH:
            stack.append(op)
        elif op[0] == C_POP:
            if len(stack) > 0:
                v = stack.pop()
                can_reduce = True
                for s in ires:
                    if s[0] == C_MOV:
                        can_reduce = can_reduce and (
                            s[2][0] != v[2]) and (s[2][1] != v[2])

                if can_reduce:
                    ires.append(
                        (C_MOV, [C_OPT_NO, v[1]], (op[2], v[2]), offset))
                else:
                    ires.insert(0, v)
                    ires.append(op)
            else:
                ires.append(op)
        elif op[0] == C_COMMENT:
            result.append(op)
        else:
            result += stack
            stack = []
            result += ires
            ires = []
            result.append(op)
    result += stack
    return result


def optimize_mov(text):
    " reduce mov twice (mov eax, 5; mov ebx, eax)"
    prev_mov = None
    result = []
    comments = []
    for i, op in enumerate(text):
        if len(op) > 3:
            offset = op[3]
        else:
            offset = 0

        if op[0] == C_MOV:
            if prev_mov is not None:
                v = prev_mov
                if (v[2][0] == op[2][1]) and (v[1][0] == op[1][1]) and \
                   (not (op[1][0] == v[1][1] and op[1][0] == C_OPT_ADDR)):
                    result.append((C_MOV, [op[1][0], v[
                                  1][1]], (op[2][0], v[2][1]), offset))
                    prev_mov = None
                else:
                    result.append(prev_mov)
                    prev_mov = op
            else:
                prev_mov = op
        elif op[0] == C_COMMENT:
            comments.append(op)
        else:
            if prev_mov is not None:
                result.append(prev_mov)
            prev_mov = None
            result += comments
            comments = []
            result.append(op)
    if prev_mov is not None:
        result += prev_mov
    return result


def optimize_mov_push(text):
    " reduce mov before push (mov eax, 5; push eax) "
    prev_mov = None
    result = []
    comments = []
    ires = []
    for i, op in enumerate(text):
        if len(op) > 3:
            offset = op[3]
        else:
            offset = 0

        if op[0] == C_MOV:
            if prev_mov is not None:
                ires.append(prev_mov)
            prev_mov = op
        elif op[0] == C_PUSH:
            if prev_mov is not None:
                v = prev_mov
                if (v[2][0] == op[2]) and (v[1][0] == op[1]) and (v[1][0] != C_OPT_ADDR):
                    ires.append((C_PUSH, v[1][1], v[2][1], offset))
                else:
                    ires.append(prev_mov)
                    ires.append(op)
            else:
                ires.append(op)
            prev_mov = None
        elif op[0] == C_COMMENT:
            comments.append(op)
        else:
            if prev_mov is not None:
                ires.append(prev_mov)
            prev_mov = None
            result += comments
            comments = []
            result += ires
            ires = []
            result.append(op)
    if prev_mov is not None:
        result += prev_mov
    return result


def optimize_clean_lines(text):
    result = []
    n = 0
    for i, op in enumerate(text):
        if op[0] == C_COMMENT:
            if op[2] == None or op[2] == "":
                n += 1
                if n < 2:
                    result.append(op)
            else:
                result.append(op)
        else:
            result.append(op)
            n = 0
    return result
