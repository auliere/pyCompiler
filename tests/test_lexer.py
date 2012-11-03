from utils.lexer import lex
from utils import ParserError

from nose.tools import assert_equal, raises, nottest

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
        s = ' v 1; "1  10 2" \nx=10;'
        assert_equal(lex(s), ['v', '1',';', '"1  10 2"','x','=','10',';'])

    def test_quotes(self):
        s = '"x;  123"'
        assert_equal(lex(s), [s])

    def test_comment_in_quotes(self):
        s = '"x; # 10"'
        assert_equal(lex(s), [s])

    @raises(ParserError)
    def test_unclosed_quotes(self):
        s = 'x "text\n'
        lex(s)

    def test_comment(self):
        s = 'x #text\n 1'
        assert_equal(lex(s), ['x','1'])

    @nottest
    def test_combined_vars(self):
        s = 'x1 = 1 + y2'
        assert_equal(lex(s), ['x1', '=', '1', '+', 'y2'])
