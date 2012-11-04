from utils.lexer import lex
from utils.syntax import synt
from utils.gen import find_vars, gen_code
from utils import ParserError

from nose.tools import assert_equal, raises, nottest

import os
import subprocess

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
        gen_code(tree, 'TEST', find_vars(tree), f=file(asm, 'w'))
        o = os.path.join(os.getcwd(), 'tests/test_set/', f_name) + '.o'
        bin = os.path.join(os.getcwd(), 'tests/test_set/', f_name) + '.bin'
        subprocess.check_call('nasm -f elf %s -o %s' % (asm, o), shell=True)
        subprocess.check_call('ld -s -dynamic-linker /lib/ld-linux.so.2 -lc %s -o %s' % (o, bin), shell=True)
        os.remove(asm)
        os.remove(o)
        return bin

    def test_smoke(self):
        bin = self.compile('t1.src')
        proc = subprocess.Popen(bin, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        stdout, stderr = proc.communicate()
        assert_equal(stdout.strip(), '63')
        os.remove(bin)

    def test_read(self):
        bin = self.compile('t2.src')
        proc = subprocess.Popen(bin, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        stdout, stderr = proc.communicate("12")
        assert_equal(stdout.strip(), '22')
        os.remove(bin)

    def test_if(self):
        bin = self.compile('t3.src')
        proc = subprocess.Popen(bin, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        stdout, stderr = proc.communicate("50")
        assert_equal(stdout.strip(), 'DEF')

        proc = subprocess.Popen(bin, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        stdout, stderr = proc.communicate("500")
        assert_equal(stdout.strip(), 'ABC')
        os.remove(bin)