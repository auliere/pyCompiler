from utils.lexer import lex
from utils.syntax import synt
from utils.gen import find_vars, gen_code
from utils.gen_asm import gen_real_asm
from nose.tools import assert_equal, nottest

import os
import subprocess
import functools

def compile_src(f_name):
    def _compile(func):
        @functools.wraps(func)
        def __compile(self):
            self.bin = self.compile(f_name)
            func(self)
            os.remove(self.bin)
        return __compile
    return _compile

class TestGenerator(object):
    @classmethod
    def setup_class(klass):
        pass

    @classmethod
    def teardown_class(klass):
        pass

    def setUp(self):
        pass

    def teardown(self):
        pass

    def compile(self, f_name):
        src = file(os.path.join(os.getcwd(), 'tests/test_set/', f_name)).read()
        tree = synt(lex(src))
        asm = os.path.join(os.getcwd(), 'tests/test_set/', f_name) + '.asm'
        p = gen_code(tree, find_vars(tree))

        lines = gen_real_asm(p, 'TEST')
        
        f = file(asm, 'w')
        for line in lines:
            print>>f, line
        f.close()

        o = os.path.join(os.getcwd(), 'tests/test_set/', f_name) + '.o'
        bin = os.path.join(os.getcwd(), 'tests/test_set/', f_name) + '.bin'
        subprocess.check_call('nasm -f elf %s -o %s' % (asm, o), shell=True)
        subprocess.check_call('ld -s -dynamic-linker /lib/ld-linux.so.2 -lc %s -o %s' % (o, bin), shell=True)
        os.remove(asm)
        os.remove(o)
        return bin

    def run(self, in_data=None):
        proc = subprocess.Popen(self.bin, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        return proc.communicate(in_data)[0]

    @compile_src("t1.src")
    def test_smoke(self):
        assert_equal(self.run().strip(), '63')

    @compile_src("t2.src")
    def test_read(self):
        assert_equal(self.run("12").strip(), '22')

    @compile_src("t3.src")
    def test_if(self):
        assert_equal(self.run("50").strip(), 'DEF')
        assert_equal(self.run("500").strip(), 'ABC')

    @nottest
    @compile_src("t4.src")
    def test_mul(self):
        " mul, div and mod "
        assert_equal(self.run("12").strip(), '30\n2')

    @compile_src("t5.src")
    def test_while(self):
        " while loop "
        assert_equal(self.run("5").strip(), '50')