from dragonfly import (Choice, MappingRule, CompoundRule, Key, IntegerRef,
                       RuleRef, Text, Repetition, Alternative, Dictation, Function)

from ..choices.letter import letter_choice

formattings = ["snake", "camel", "uppercase", "together", "proper", "barbecue", "lowercase", "Ada"]
formatting_map = {}
for f in formattings:
    formatting_map[f] = f


def formatting_choice(name="formatting"):
    return Choice(name, formatting_map)


def words(dictation):
    return str(dictation).split(' ')


def snake_case(dictation):
    response = '_'.join(words(dictation)).lower()
    return response


def camel_case(dictation):
    return ''.join([word.capitalize() if idx != 0 else word
                    for idx, word in enumerate(words(dictation))])


def proper(dictation):
    return ''.join([word.capitalize() for word in words(dictation)])


def lowercase(dictation):
    return str(dictation).lower()


def uppercase(dictation):
    return str(dictation).upper()


def together(dictation):
    return str(dictation).replace(' ', '')


def barbecue(dictation):
    response = "-".join(words(dictation))
    return response


def ada(dictation):
    response = "_".join([word.capitalize() for word in words(dictation)])
    return response


def format_text(dictation, format_type=None):
    if format_type == "snake":
        response = snake_case(dictation)
        return Text(response).execute()
    elif format_type == "camel":
        response = camel_case(dictation)
        return Text(response).execute()
    elif format_type == "proper":
        response = proper(dictation)
        return Text(response).execute()
    elif format_type == "together":
        response = together(dictation)
        return Text(response).execute()
    elif format_type == "lowercase":
        response = lowercase(dictation)
        return Text(response).execute()
    elif format_type == "uppercase":
        response = uppercase(dictation)
        return Text(response).execute()
    elif format_type == "barbecue":
        response = barbecue(dictation)
        return Text(response).execute()
    elif format_type == "Ada":
        response = ada(dictation)
        return Text(response).execute()


operator_selection_map = {}
operators = [
    "equals",
    "check equals",
    "check really equals",
    "check not equals",
    "check really not equals",
    "map",
    "apply",
    "bind",
    "fat arrow",
    "arrow",
]

for o in operators:
    operator_selection_map[o] = o


def operator_choice(name="operator"):
    return Choice(name, operator_selection_map)


def insert_operator(operator_selection):
    if operator_selection == "equals":
        return Text(" = ").execute()
    elif operator_selection == "check equals":
        return Text(" == ").execute()
    elif operator_selection == "check really equals":
        return Text(" === ").execute()
    elif operator_selection == "check not equals":
        return Text(" != ").execute()
    elif operator_selection == "check really not equals":
        return Text(" !== ").execute()
    elif operator_selection == "map":
        return Text(" <$> ").execute()
    elif operator_selection == "apply":
        return Text(" <*> ").execute()
    elif operator_selection == "bind":
        return Text(" >>= ").execute()
    elif operator_selection == "fat arrow":
        return Text(" => ").execute()
    elif operator_selection == "arrow":
        return Text(" -> ").execute()


class LetterRule(MappingRule):
    mapping = {
        "<letter>": Key("%(letter)s"),

        "go [<n>] up": Key("up:%(n)s"),
        "go [<n>] down": Key("down:%(n)s"),
        "go [<n>] left": Key("left:%(n)s"),
        "go [<n>] right": Key("right:%(n)s"),

        "say <dictation>": Text("%(dictation)s"),
        "<format_type> <dictation>": Function(format_text),

        "control <letter>": Key("c-%(letter)s"),

        "binary <operator_selection>": Function(insert_operator),
    }

    extras = [
        letter_choice("letter"),
        formatting_choice("format_type"),
        operator_choice("operator_selection"),
        IntegerRef("n", 1, 100),
        Dictation("dictation"),
    ]


letter = RuleRef(rule=LetterRule(), name='letter')

letter_sequence = Repetition(
    Alternative([letter]),
    min=1, max=12, name="letter_sequence")


class LetterSequenceRule(CompoundRule):
    spec = "<letter_sequence>"
    extras = [letter_sequence]

    def _process_recognition(self, node, extras):
        letter_sequence = extras["letter_sequence"]
        for letter in letter_sequence:
            letter.execute()
        Key("shift:up, ctrl:up").execute()
