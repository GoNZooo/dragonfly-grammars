from dragonfly import (Choice)


def letter_choice(name="letter"):
    return Choice(name, {
        'air': 'a',
        'bat': 'b',
        'cap': 'c',
        'drum': 'd',
        'each': 'e',
        'fine': 'f',
        'gust': 'g',
        'harp': 'h',
        'sit': 'i',
        'jim': 'j',
        'kick': 'k',
        'look': 'l',
        'made': 'm',
        'near': 'n',
        'on': 'o',
        'pit': 'p',
        'quench': 'q',
        'red': 'r',
        'sun': 's',
        'trap': 't',
        'urge': 'u',
        'vest': 'v',
        'whale': 'w',
        'plex': 'x',
        'yank': 'y',
        'zip': 'z',

        'ship air': 'A',
        'ship bat': 'B',
        'ship cap': 'C',
        'ship drum': 'D',
        'ship each': 'E',
        'ship fine': 'F',
        'ship gust': 'G',
        'ship harp': 'H',
        'ship sit': 'I',
        'ship jim': 'J',
        'ship kick': 'K',
        'ship look': 'L',
        'ship made': 'M',
        'ship near': 'N',
        'ship on': 'O',
        'ship pit': 'P',
        'ship quench': 'Q',
        'ship red': 'R',
        'ship sun': 'S',
        'ship trap': 'T',
        'ship urge': 'U',
        'ship vest': 'V',
        'ship whale': 'W',
        'ship plex': 'X',
        'ship yank': 'Y',
        'ship zip': 'Z',

        'zero': '0',
        'one': '1',
        'two': '2',
        'three': '3',
        'four': '4',
        'five': '5',
        'six': '6',
        'seven': '7',
        'eight': '8',
        'nine': '9',

        'space': 'space',
        'tabby': 'tab',

        'backtick': 'backtick',
        'pipe': 'bar',

        # vim functionality symbols
        'colon': 'colon',
        'slash': 'slash',
        'hat': 'caret',
        'dollar': 'dollar',

        # more or less important symbols for code
        'spamma': 'comma',
        'assign': 'equal',
        'bang': 'exclamation',

        # quotes
        'dub': 'dquote',
        'sing': 'squote',

        '(underscore | score)': 'underscore',
        'quest': 'question',

        'ampersand': 'ampersand',
        '(apostrophe | post)': 'apostrophe',
        '(asterisk | starling)': 'asterisk',
        'at sign': 'at',
        'backslash': 'backslash',
        '(dot|period|prick)': 'dot',
        'hashtag': 'hash',
        'hyphen': 'hyphen',
        'minus': 'minus',
        '(modulo|purse)': 'percent',
        'plus': 'plus',
        'semicolon': 'semicolon',
        'tilde': 'tilde',

        # parens
        'lice': 'lparen',
        'rice': 'rparen',

        # angle brackets
        'langle': 'langle',
        'rangle': 'rangle',

        # curly braces
        'lace': 'lbrace',
        'race': 'rbrace',

        # square brackets
        'lack': 'lbracket',
        'rack': 'rbracket',

        # simple composite comparison operators
        'seek': 'slash,equal',
        'eek': 'equal,equal',
        'beak': 'exclamation,equal',

        # editing
        'backspace': 'backspace',
        '(escape|okay)': 'escape',
        'slap': 'enter'
    })
