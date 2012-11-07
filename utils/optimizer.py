
from utils.const import *
from utils.gen import PseudoAsm

def optimize(pseudo):
    pseudo = PseudoAsm(pseudo)
    
    text = pseudo.text
    text = optimize_push_pop(text)
    text = optimize_mov(text)
    text = optimize_mov_push(text)
    
    pseudo.text = text
    return pseudo

def optimize_push_pop(text):
    " reduce push and pop sequences "
    stack = []
    result = []
    for i,op in enumerate(text):
        if op[0] == C_PUSH:
            stack.append(op)
        elif op[0] == C_POP:
            if len(stack) > 0:
                v = stack.pop()
                result.append( (C_MOV, [C_OPT_NO, v[1]], (op[2],v[2])) )
            else:
                result.append(op)
        elif op[0] == C_COMMENT:
            result.append(op)
        else:
            result += stack
            stack = []
            result.append(op)
    result += stack
    return result

def optimize_mov(text):
    " reduce mov twice (mov eax, 5; mov ebx, eax)"
    prev_mov = None
    result = []
    for i,op in enumerate(text):
        if op[0] == C_MOV:
            if prev_mov is not None:
                v = prev_mov
                if (v[2][0] == op[2][1]) and (v[1][0] == op[1][1]):
                    result.append( (C_MOV, [op[1][0], v[1][1]], (op[2][0], v[2][1])) )
                    prev_mov = None
                else:
                    result.append(prev_mov)
                    prev_mov = op
            else:
                prev_mov = op
        elif op[0] == C_COMMENT:
            result.append(op)
        else:
            if prev_mov is not None:
                result.append(prev_mov)
            prev_mov = None
            result.append(op)
    if prev_mov is not None:
        result += prev_mov
    return result

def optimize_mov_push(text):
    " reduce mov before push (mov eax, 5; push eax) "
    prev_mov = None
    result = []
    for i,op in enumerate(text):
        if op[0] == C_MOV:
            prev_mov = op
        elif op[0] == C_PUSH:
            if prev_mov is not None:
                v = prev_mov
                if (v[2][0] == op[2]) and (v[1][0] == op[1]):
                    result.append( (C_PUSH, v[1][1], v[2][1] ) )
                else:
                    result.append(prev_mov)
                    result.append(op)
            else:
                result.append(op)
            prev_mov = None
        elif op[0] == C_COMMENT:
            result.append(op)
        else:
            if prev_mov is not None:
                result.append(prev_mov)
            prev_mov = None
            result.append(op)
    if prev_mov is not None:
        result += prev_mov
    return result