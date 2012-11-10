from __future__ import print_function

from functools import partial

from utils.const import *
from utils import ParserError, typeof

class TreeStats(object):
    def __init__(self, vars=None, strs=None, funcs=None):
        if vars is None:
            vars = []
        if strs is None:
            strs = []
        if funcs is None:
            funcs = {}

        self.vars = vars
        self.strs = strs
        self.funcs = funcs
        self.use_print = False
        self.use_read = False

def find_vars(t, stat=None, prefix=""):
    if stat == None:
        stat = TreeStats()
    if isinstance(t,list):
        for x in reversed(t):
            find_vars(x, stat=stat, prefix=prefix)
    elif isinstance(t,tuple):
        if t[0] == A_PRINT:
            stat.use_print = True
        elif t[0] == A_READ:
            stat.use_read = True
        if t[0] == A_FUNCTION:
            stat.funcs[t[1][0].name] = {'args':t[1][0].args, 
                                        'args_count': len(t[1][0].args)}
            for v in t[1][0].args:
                stat.vars.append("%s_%s" % (t[1][0].name, v))
            find_vars(t[1][1], stat=stat, prefix=t[1][0].name+"_")
        else:
            find_vars(t[1], stat=stat, prefix=prefix)
    else:
        if isinstance(t, str) and typeof(t) == T_VAR:
            if prefix+t not in stat.vars:
                stat.vars.append(prefix+t)
        if isinstance(t, str) and typeof(t) == T_STRING:
            if t not in stat.strs:
                stat.strs.append(t)
    return stat

def make_asm_node_p(p, cmd, o, v, shift=0):
    p.text.append((cmd, o, v, shift,))

class PseudoAsm(object):
    def __init__(self, p=None):
        if p is None:
            self.text = []
            self.data = []
            self.labelNum = 0
            self.ifNum = 0
            self.loopNum = 0
            self.funcNum = 0
        else:
            self.text = p.text[:]
            self.data = p.data[:]
            self.labelNum = p.labelNum
            self.ifNum = p.ifNum
            self.loopNum = p.loopNum
            self.funcNum = p.funcNum

def gen_text_section(t, stat, p=None, prefix=""):
    if p == None:
        p = PseudoAsm()

    make_asm_node = partial(make_asm_node_p, p=p, shift=(0 if len(prefix)==0 else 1 ))
    aa_push = partial(make_asm_node, cmd=C_PUSH)
    aa_pop = partial(make_asm_node, cmd=C_POP, o=None)
    aa_mov = partial(make_asm_node, cmd=C_MOV)
    aa_call = partial(make_asm_node, cmd=C_CALL, o=None)
    aa_add = partial(make_asm_node, cmd=C_ADD)
    aa_sub = partial(make_asm_node, cmd=C_SUB)
    aa_imul = partial(make_asm_node, cmd=C_IMUL, o=None)
    aa_idiv = partial(make_asm_node, cmd=C_IDIV, o=None)
    aa_cmp = partial(make_asm_node, cmd=C_CMP, o=None)
    aa_jmp = partial(make_asm_node, cmd=C_JMP)
    aa_label = partial(make_asm_node, cmd=C_LABEL, o=None)
    aa_neg = partial(make_asm_node, cmd=C_NEG, o=None)
    aa_push_num = partial(aa_push, o=C_OPT_NO)
    aa_push_addr = partial(aa_push, o=C_OPT_ADDR)
    aa_ret = partial(make_asm_node, cmd=C_RET, o=None, v=None)

    iterate = t
    if isinstance(t, list):
        iterate = reversed(t)
    if isinstance(t, (str, tuple)):
        iterate = [t]
    for node in iterate:
        p.text.append((C_COMMENT, None, None))
        if isinstance(node, str):
            tnode = typeof(node)
            if tnode == T_NUMBER:
                aa_push_num(v=node)
            elif tnode == T_VAR:
                aa_push_addr(v="v%s" % prefix+node)
            else:
                raise ParserError("Error generating ASM code on node %s" % node)

        elif node[0] == A_BLOCK:
            gen_text_section(node[1], stat, p=p, prefix=prefix)

        elif node[0] == A_FUNCTION:
            p.funcNum += 1
            p.text.append((C_COMMENT, None, None))
            p.text.append((C_COMMENT, None, "Function %s" % node[1][0].name))
            aa_jmp(o=None, v="Func%dEnd" % p.funcNum, shift=1)
            aa_label(v="Func_%s" % node[1][0].name, shift=1)
            for i,arg in enumerate(node[1][0].args):
                var = "v%s_%s" % (node[1][0].name, arg)
                aa_mov(o=[C_OPT_NO, C_OPT_ADDR], v=["eax", "esp+%d" % ((i+1)*4)], shift=1)
                aa_mov(o=[C_OPT_ADDR, C_OPT_NO], v=[var, "eax"], shift=1)
            gen_text_section(node[1][1], stat, p=p, prefix=node[1][0].name+"_")
            aa_label(v="Func%dEnd" % p.funcNum, shift=1)


        elif node[0] == A_RETURN:
            # print (node[1])
            aa_mov(o=[C_OPT_NO, C_OPT_ADDR], v=["eax", "v%s" % prefix+node[1]])
            # aa_push_num(v="eax")
            aa_ret()

        elif node[0] == A_PRINT:
            if typeof(node[1]) == T_STRING:
                strnum = stat.strs.index(node[1])

                aa_push_num(v="str%d" % strnum)
                aa_call(v="printf")
                aa_add(o=[C_OPT_NO, C_OPT_NO], v=["esp", "4"])
                aa_push_addr(v="stdout")
                aa_call(v="fflush")
                aa_add(o=[C_OPT_NO, C_OPT_NO], v=["esp", "4"])

            elif typeof(node[1]) == T_VAR:
                aa_mov(o=[C_OPT_NO, C_OPT_ADDR], v=["eax", "v%s" % prefix+node[1]])
                aa_push_num(v="eax")
                aa_push_num(v="numbs")
                aa_call(v="printf")
                aa_add(o=[C_OPT_NO, C_OPT_NO], v=["esp", "8"])
                aa_push_addr(v="stdout")
                aa_call(v="fflush")
                aa_add(o=[C_OPT_NO, C_OPT_NO], v=["esp", "4"])
            else:
                raise ParserError("Error print argument: %s" % node)

        elif node[0] == A_READ:
            assert typeof(node[1]) == T_VAR

            aa_push_num(v="v%s" % prefix+node[1])
            aa_push_num(v="numbs_in_format")
            aa_call(v="scanf")
            aa_add(o=[C_OPT_NO, C_OPT_NO], v=["esp", "8"])
            aa_call(v="getchar")

        elif node[0] == A_ASSIGN:
            var = node[1][0]
            gen_text_section(node[1][1], stat, p=p, prefix=prefix)
            aa_pop(v="eax")
            aa_mov(o=[C_OPT_ADDR, C_OPT_NO], v=["v%s" % prefix+var, "eax"])
        
        elif node[0] == A_IF:
            p.ifNum += 1
            gen_text_section(node[1][0], stat, p=p, prefix=prefix)
            aa_pop(v="eax")
            aa_cmp(o=[C_OPT_NO, C_OPT_NO], v=["eax", "0"])
            aa_jmp(o="jnz", v="llIf%dElse" % p.ifNum)
            #then
            gen_text_section(node[1][1], stat, p=p, prefix=prefix)
            aa_jmp(o=None, v="llIf%dEnd" % p.ifNum)
            #else
            aa_label(v="llIf%dElse" % p.ifNum)
            gen_text_section(node[1][2], stat, p=p, prefix=prefix)
            
            aa_label(v="llIf%dEnd" % p.ifNum)
        
        elif node[0] == '+':
            gen_text_section(node[1], stat, p=p, prefix=prefix)
            aa_pop(v="eax")
            aa_pop(v="ebx")
            aa_add(o=[C_OPT_NO, C_OPT_NO], v=["eax", "ebx"])
            aa_push_num(v="eax")

        elif node[0] in ['>=', '<=', '>', '<', '=']:
            gen_text_section(node[1], stat, p=p, prefix=prefix)
            p.labelNum += 1
            op = {'>=': 'jge',
                  '<=': 'jle',
                  '>': 'jg',
                  '<': 'jl',
                  '=': 'je',
                 }
            aa_pop(v="eax")
            aa_pop(v="ebx")
            aa_cmp(v=["eax","ebx"])
            aa_jmp(o=op[node[0]], v="ll%d" % p.labelNum)
            aa_push_num(v="1")
            aa_jmp(o=None, v="ell%d" % p.labelNum)
            aa_label(v="ll%d" % p.labelNum)
            aa_push_num(v="0")
            aa_label(v="ell%d" % p.labelNum)

        elif node[0] == '-':
            gen_text_section(node[1], stat, p=p, prefix=prefix)
            if len(node[1]) == 2:
                aa_pop(v="eax")
                aa_pop(v="ebx")
                aa_sub(o=[C_OPT_NO, C_OPT_NO], v=["eax", "ebx"])
                aa_push_num(v="eax")
            else:
                aa_pop(v="eax")
                aa_neg(v="eax")
                aa_push_num(v="eax")

        elif node[0] == '*':
            gen_text_section(node[1], stat, p=p, prefix=prefix)
            aa_pop(v="eax")
            aa_pop(v="ebx")
            aa_imul(v="ebx")
            aa_push_num(v="eax")

        elif node[0] == '/':
            gen_text_section(node[1], stat, p=p, prefix=prefix)
            aa_pop(v="eax")
            aa_pop(v="ebx")
            aa_idiv(v="ebx")
            aa_push_num(v="eax")

        elif node[0] == '%':
            gen_text_section(node[1], stat, p=p, prefix=prefix)
            aa_pop(v="eax")
            aa_pop(v="ebx")
            aa_idiv(v="ebx")
            aa_push_num(v="edx")

        elif node[0] == A_WHILE:
            p.loopNum += 1

            aa_label(v="llWhile%d" % p.loopNum)
            gen_text_section(node[1][0], stat, p=p, prefix=prefix)
            
            aa_pop(v="eax")
            aa_cmp(o=[C_OPT_NO, C_OPT_NO], v=["eax", "0"])
            aa_jmp(o="jnz", v="llWhile%dEnd" % p.loopNum)

            gen_text_section(node[1][1], stat, p=p, prefix=prefix)

            aa_jmp(o=None, v="llWhile%d" % p.loopNum)
            aa_label(v="llWhile%dEnd" % p.loopNum)

        elif node[0] == A_CALL:
            if stat.funcs[node[1]]['args_count'] != len(node[2]):
                raise ParserError("Call %s passing %d arguments. %d expected" % 
                    (node[1], len(node[2]), stat.funcs[node[1]]['args_count']))
            
            for arg in node[2]:
                gen_text_section(arg, stat, p=p, prefix=prefix)

            aa_call(v="Func_%s" % node[1])
            aa_add(o=[C_OPT_NO, C_OPT_NO], v=["esp", str(4*len(node[2]))])
            aa_push_num(v="eax")

        elif node[0] in ['/', '%']:
            raise NotImplementedError("%s operation is not implemented yet" % node[0])
        else:
            raise ParserError("Error generating ASM code on node %s" % repr(node))

def clear_string(s):
    r = s
    r = "\",10,\"".join(r.split("\\n"))
    return r

def gen_code(t, stat):
    p = PseudoAsm()

    p.data.append((C_EQU, "_kernel_", "0x80"))

    p.data.append((C_COMMENT, None, "Strings"))
    for i,vs in enumerate(stat.strs):
        s = clear_string(vs)
        p.data.append((C_DB, "str%d" % i, "%s, 0" % s))
        p.data.append((C_EQU_F, "lstr%d" % i, "str%d" % i))

    p.data.append((C_DB, "numbs", "\"%d\", 0"))
    p.data.append((C_DB, "numbs_in_format", "\"%d\",0"))

    p.data.append((C_COMMENT, None, "Variables"))
    
    for i,vs in enumerate(stat.vars):
        p.data.append((C_DD, "v%s" % vs, "0"))

    p.text.append((C_GLOBL, None, "_start"))
    
    extern = []
    if stat.use_print:
        extern.append("printf")
    if stat.use_read:
        extern.append("scanf")
        extern.append("getchar")
    if stat.use_read or stat.use_print:
        extern.append("fflush")
        extern.append("stdout")

    for e in extern:
        p.text.append((C_EXTRN, None, e))

    p.text.append((C_LABEL, None, "_start"))
    
    p.text.append((C_COMMENT, None, "setup stack frame"))
    p.text.append((C_PUSH, C_OPT_NO, "ebp"))
    p.text.append((C_MOV, [C_OPT_NO, C_OPT_NO], ["ebp", "esp"]))

    gen_text_section(t, stat, p=p)
    
    #end
    p.text.append((C_COMMENT, None, "restore stack frame"))
    p.text.append((C_MOV, [C_OPT_NO, C_OPT_NO], ["esp", "ebp"]))
    p.text.append((C_POP, None, "ebp"))
    p.text.append((C_MOV, [C_OPT_NO, C_OPT_NO], ["ebx", "0"]))
    p.text.append((C_MOV, [C_OPT_NO, C_OPT_NO], ["eax", "1"]))
    p.text.append((C_INT, None, "_kernel_"))
    
    return p