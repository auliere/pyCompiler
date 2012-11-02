# import utils
from utils.lexer import lex
from utils import ParserError

from nose.tools import assert_true, assert_equal, raises, nottest

class TestLexer(object):
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
        str = ' v 1; "1  10 2" \nx=10;'
        assert_equal(lex(str), ['v', '1',';', '"1  10 2"','x','=','10',';'])

    def test_quotes(self):
        str = '"x;  123"'
        assert_equal(lex(str), [str])

    def test_comment_in_quotes(self):
        str = '"x; # 10"'
        assert_equal(lex(str), [str])

    @raises(ParserError)
    def test_unclosed_quotes(self):
        str = 'x "text\n'
        lex(str)

    def test_comment(self):
        str = 'x #text\n 1'
        assert_equal(lex(str), ['x','1'])

    @nottest
    def test_combined_vars(self):
        str = 'x1 = 1 + y2'
        assert_equal(lex(str), ['x1', '=', '1', '+', 'y2'])
