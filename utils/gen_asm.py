from __future__ import print_function

from time import strftime, gmtime

from utils.const import *
from utils import ParserError

def gen_real_asm(pseudo, src_file):
    res = []
    res.append("; Source file: %s" % src_file)
    res.append("; Generated %s" % strftime("%Y-%m-%d %H:%M:%S", gmtime()))
    res.append("")
    res.append("SECTION .data")
    res.append("")
    for command in pseudo.data:
        res += nasm_gen(command)
    res.append("")
    res.append("SECTION .text")
    res.append("")
    for command in pseudo.text:
        res += nasm_gen(command)

    return res

def operand(x, t):
    if t == C_OPT_NO:
        return x
    elif t == C_OPT_ADDR:
        return "[%s]" % x

def nasm_gen(l):
    cmd = None
    if l[0] == C_PUSH:
        cmd = ["push dword %s" % operand(l[2], l[1])]
    elif l[0] == C_POP:
        cmd = ["pop dword %s" % l[2]]
    elif l[0] == C_CALL:
        cmd = ["call  %s" % l[2]]
    elif l[0] == C_INT:
        cmd = ["int %s" % l[2]]
    elif l[0] == C_MOV:
        cmd = ["mov dword %s, %s" % (operand(l[2][0], l[1][0]),
                              operand(l[2][1], l[1][1]))]
    elif l[0] == C_ADD:
        cmd = ["add %s, %s" % (operand(l[2][0], l[1][0]),
                              operand(l[2][1], l[1][1]))]
    elif l[0] == C_IMUL: #
        cmd = ["imul %s" % l[2]]
    elif l[0] == C_IDIV: #
        cmd = ["idiv %s" % l[2]]
    elif l[0] == C_SUB:
        cmd = ["sub %s, %s" % (operand(l[2][0], l[1][0]),
                              operand(l[2][1], l[1][1]))]
    elif l[0] == C_CMP:
        cmd = ["cmp %s,%s" % (l[2][0], l[2][1])]
    elif l[0] == C_COMMENT:
        if l[2] is None:
            cmd=[""]
        else:
            cmd = ["; %s" % l[2]]
    elif l[0] == C_EQU:
        cmd = ["%s: equ %s" % (l[1], l[2])]
    elif l[0] == C_EQU_F:
        cmd = ["%s: equ $-%s" % (l[1], l[2])]
    elif l[0] == C_DB:
        cmd = ["%s: db %s" % (l[1],l[2])]
    elif l[0] == C_DD:
        cmd = ["%s: dd %s" % (l[1],l[2])]
    elif l[0] == C_GLOBL:
        cmd = ["global %s" % l[2]]
    elif l[0] == C_EXTRN:
        cmd = ["extern %s" % l[2]]
    elif l[0] == C_LABEL:
        cmd = ["%s:" % l[2]]
    elif l[0] == C_JMP:
        if l[1] is None:
            cmd = ["jmp %s" % l[2]]
        else:
            cmd = ["%s %s" % (l[1],l[2])]
    else:
        raise ParserError("Can't translate %d command" % l[0])

    return cmd