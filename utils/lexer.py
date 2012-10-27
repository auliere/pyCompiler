import string

from utils import ParserError

def lex(text):
    assert len(text)>0


    NO, ALPHA, NUM, SYMB, CMDEND, QUOTE, QUOTE_end, COMMENT = range(8)
        
    def typeof(s, string=False):
        if s[0].isalpha():
            return ALPHA
        elif s[0].isdigit():
            return NUM
        elif s[0] in "=:><+-*/(){}":
            return SYMB
        elif s[0] in [';']:
            return CMDEND
        elif s[0] in ['"','\'']:
            return QUOTE
        elif s[0] in ['#']:
            return COMMENT
        elif s.strip() == "":
            return NO
        else:
            if not string:
                raise ParserError("Unknown symbol")

    def symb_check(t,s):
        COMBINATIONS = (':=', '**', )
        return (string.strip(string.join(t, ''))+s) in COMBINATIONS

    all_tokens = []
    token = []
    prev_type = current_type = typeof(text[0])
    string_token = ""
    inline_comment = False

    for s in text:
        if inline_comment:
            if s == '\n':
                inline_comment = False
            continue

        current_type = typeof(s, prev_type == QUOTE)

        if current_type == COMMENT:
            inline_comment = True
            continue

        if prev_type == QUOTE:
            if current_type != QUOTE:
                string_token += s
            else:
                all_tokens.append("\"%s\"" % string_token)
                string_token = ""
                prev_type = QUOTE_end
                token = []
            continue
        if (prev_type == current_type) and (current_type != SYMB or symb_check(token, s)):
            token.append(s)
        else:
            if prev_type != NO:
                clear_token = string.strip(string.join(token, ''))
                if len(clear_token)>0:
                    all_tokens.append(clear_token)
            prev_type = current_type
            token = [s]

    clear_token = string.strip(string.join(token, ''))
    if len(clear_token)>0:
        all_tokens.append(clear_token)
    return all_tokens