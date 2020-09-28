from dragonfly import (Choice, Function, MappingRule, Grammar, CompoundRule, Dictation)
from vim.rules.letter import (snake_case)
from macro_utilities import (replace_in_text, execute_with_dictation)


class BarneyEnabler(CompoundRule):
    spec = "enable Barney"

    def _process_recognition(self, node, extras):
        barney_bootstrap.disable()
        barney_grammar.enable()
        print "Barney grammar enabled!"


class BarneyDisabler(CompoundRule):
    spec = "disable Barney"

    def _process_recognition(self, node, extras):
        barney_grammar.disable()
        barney_bootstrap.enable()
        print "Barney grammar disabled"


type_name_choice_map = {
    "integer": "int",
    "unsigned integer": "unsigned int",
    "short": "short",
    "unsigned short": "unsigned short",
    "long": "long",
    "unsigned long": "unsigned long",
    "character": "char",
    "boolean": "bool",
    "void": "void",
    "bite": "byte",
    "string": "std::string",
    "standard vector": "std::vector",
}


def type_name_choice(name="type_name"):
    return Choice(name, type_name_choice_map)


def output_constant(value_name, type_name=None):
    if type_name is not None:
        execute_with_dictation(
            value_name,
            lambda n: replace_in_text("const %s %s = $;" % (type_name, format_value_name(n))),
            lambda n: replace_in_text("const %s $ = _;" % type_name)
        )


def format_value_name(name):
    return snake_case(str(name))


class BarneyUtilities(MappingRule):
    mapping = {
        "constant [<value_name>]": Function(output_constant, type_name="auto"),
        "constant <type_name> [<value_name>]": Function(output_constant),
    }

    extras = [
        Dictation("value_name", default=""),
        type_name_choice("type_name")
    ]


# The main Barney grammar rules are activated here
barney_bootstrap = Grammar("barney bootstrap")
barney_bootstrap.add_rule(BarneyEnabler())
barney_bootstrap.load()

barney_grammar = Grammar("barney grammar")
barney_grammar.add_rule(BarneyUtilities())
barney_grammar.add_rule(BarneyDisabler())
barney_grammar.load()
barney_grammar.disable()

# Unload function which will be called by natlink at unload time.


def unload():
    global barney_grammar
    if barney_grammar:
        barney_grammar.unload()
    barney_grammar = None
