from dragonfly import (Choice, Function, MappingRule, Grammar, CompoundRule, Dictation, Text)
from vim.rules.letter import (snake_case)
from macro_utilities import (replace_in_text, execute_with_dictation)


class BarneyEnabler(CompoundRule):
    spec = "enable Barney"

    def _process_recognition(self, node, extras):
        barney_bootstrap.disable()
        barney_grammar.enable()
        print("Barney grammar enabled!")


class BarneyDisabler(CompoundRule):
    spec = "disable Barney"

    def _process_recognition(self, node, extras):
        barney_grammar.disable()
        barney_bootstrap.enable()
        print("Barney grammar disabled")


type_name_choice_map = {
    "short": "short",
    "integer": "int",
    "long": "long",
    "unsigned short": "unsigned short",
    "unsigned integer": "unsigned int",
    "unsigned long": "unsigned long",
    "character": "char",
    "boolean": "bool",
    "void": "void",
    "bite": "byte",
    "string": "std::string",
    "string view": "std::string_view",
    "unique_pointer": "std::unique_ptr",
    "shared_pointer": "std::shared_ptr",
    "standard vector": "std::vector",
    "you eight": "uint8_t",
    "you sixteen": "uint16_t",
    "you thirty two": "uint32_t",
    "you sixty four": "uint64_t",
    "unsigned eight": "uint8_t",
    "unsigned sixteen": "uint16_t",
    "unsigned thirty two": "uint32_t",
    "unsigned sixty four": "uint64_t",
    "i eight": "int8_t",
    "i sixteen": "int16_t",
    "i thirty two": "int32_t",
    "i sixty four": "int64_t",
    "signed eight": "int8_t",
    "signed sixteen": "int16_t",
    "signed thirty two": "int32_t",
    "signed sixty four": "int64_t",
    "size": "size_t",
}


def type_name_choice(name="type_name"):
    return Choice(name, type_name_choice_map)


def output_value(value_name, type_name=None, is_constant=False):
    constant_prefix = "const " if is_constant else ""

    if type_name is not None:
        execute_with_dictation(
            value_name,
            lambda n: replace_in_text(
                "%s%s %s = $;" % (constant_prefix, type_name, format_value_name(n))
            ),
            lambda n: replace_in_text("%s%s $ = _;" % (constant_prefix, type_name))
        )


def output_type_annotation(value_name, type_name=None, is_constant=False):
    constant_prefix = "const " if is_constant else ""

    if type_name is not None:
        execute_with_dictation(
            value_name,
            lambda n: Text(
                "%s%s %s" % (constant_prefix, type_name, format_value_name(n))
            ),
            lambda n: replace_in_text("%s%s $" % (constant_prefix, type_name))
        )


def format_value_name(name):
    return snake_case(str(name))


class BarneyUtilities(MappingRule):
    mapping = {
        "constant [<value_name>]": Function(output_value, type_name="auto", is_constant=True),
        "constant <type_name> [<value_name>]": Function(output_value, is_constant=True),
        "variable [<value_name>]": Function(output_value, type_name="auto"),
        "variable <type_name> [<value_name>]": Function(output_value),
        "<type_name> [<value_name>]": Function(output_type_annotation),
        "<type_name> [<value_name>] is constant": Function(output_type_annotation,
                                                           is_constant=True),
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
