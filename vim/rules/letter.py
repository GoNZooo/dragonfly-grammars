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
    return dictation.split(' ')


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


def say_text(dictation):
    expanded_words = str(dictation).replace(".", " period").lstrip().lower()

    return Text(expanded_words).execute()


def format_text(dictation, format_type=None):
    expanded_words = str(dictation).replace(".", " period").lstrip().lower()

    if format_type == "snake":
        response = snake_case(expanded_words)
        return Text(response).execute()
    elif format_type == "camel":
        response = camel_case(expanded_words)
        return Text(response).execute()
    elif format_type == "proper":
        response = proper(expanded_words)
        return Text(response).execute()
    elif format_type == "together":
        response = together(expanded_words)
        return Text(response).execute()
    elif format_type == "lowercase":
        response = lowercase(expanded_words)
        return Text(response).execute()
    elif format_type == "uppercase":
        response = uppercase(expanded_words)
        return Text(response).execute()
    elif format_type == "barbecue":
        response = barbecue(expanded_words)
        return Text(response).execute()
    elif format_type == "Ada":
        response = ada(expanded_words)
        return Text(response).execute()


class LetterRule(MappingRule):
    mapping = {
        "<letter>": Key("%(letter)s"),

        "go [<n>] up": Key("up:%(n)s"),
        "go [<n>] down": Key("down:%(n)s"),
        "go [<n>] left": Key("left:%(n)s"),
        "go [<n>] right": Key("right:%(n)s"),

        "say <dictation>": Function(say_text),
        "<format_type> <dictation>": Function(format_text),

        "control <letter>": Key("c-%(letter)s"),
        "equals": Text(" = "),
    }

    extras = [
        letter_choice("letter"),
        formatting_choice("format_type"),
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
