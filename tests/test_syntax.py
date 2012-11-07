from utils.lexer import lex
from utils.syntax import synt
from utils.gen import find_vars
# from utils import ParserError
from utils.const import *

from nose.tools import assert_equal, assert_false, assert_true

class TestSyntax(object):
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

    def test_smoke(self):
        str = "i = 10+1;\n"\
              "j = 5*i;\n"
        tree = [(A_BLOCK, list(reversed([
                                        (A_ASSIGN, [
                                            'i', [('+', ['10','1'])]
                                                    ]
                                        ), 
                                        (A_ASSIGN, [
                                            'j', [('*', ['5','i'])]
                                                   ]
                                        ),]))
                                      ), ]
        assert_equal(synt(lex(str)), tree)
        
        stat = find_vars(tree)
        assert_equal(set(stat.vars), set(['i','j']))
        assert_false(stat.use_print)
        assert_false(stat.use_read)

    def test_print(self):
        str = 'print i;\n'
        tree = [(A_BLOCK, [ (A_PRINT, "i") ])]
        assert_equal(synt(lex(str)), tree)

        stat = find_vars(tree)
        assert_equal(set(stat.vars), set(['i']))
        assert_true(stat.use_print)
        assert_false(stat.use_read)

    def test_if(self):
        str = 'if x>0:\n'\
                  'print "1";\n'\
              'else:\n'\
                  'print "2";\n'\
              'endif;\n'
        tree = [(A_BLOCK, [ (A_IF, [[
                                ('>', ['x', '0']) ],
                                (A_BLOCK, [(A_PRINT, '"1"')]),
                                (A_BLOCK, [(A_PRINT, '"2"')])
                                   ],
                            ),]
                          ), ]

        assert_equal(synt(lex(str)), tree)

    def test_use_print(self):
        str = 'while x>0:\n'\
                  'print "1";\n'\
              'endwhile;\n'
        stat = find_vars(synt(lex(str)))
        assert_equal(set(stat.vars), set(['x']))
        assert_equal(set(stat.strs), set(['"1"']))
        assert_true(stat.use_print)
        assert_false(stat.use_read)

        str = 'if x>0:\n'\
                  'print "1";\n'\
              'else:\n'\
                  'print "2";\n'\
              'endif;\n'
        stat = find_vars(synt(lex(str)))
        assert_equal(set(stat.vars), set(['x']))
        assert_equal(set(stat.strs), set(['"1"', '"2"']))
        assert_true(stat.use_print)
        assert_false(stat.use_read)

        str = 'read i;\nprint i;'
        stat = find_vars(synt(lex(str)))
        assert_equal(set(stat.vars), set(['i']))
        assert_true(stat.use_print)
        assert_true(stat.use_read)

    def test_loop(self):
        str = 'while x>0:\n'\
                  'print "1";\n'\
              'endwhile;\n'
        tree = [(A_BLOCK, [ (A_WHILE, [[
                                ('>', ['x', '0']) ],
                                (A_BLOCK, [(A_PRINT, '"1"')]),
                                   ],
                            ),]
                          ), ]

        assert_equal(synt(lex(str)), tree)