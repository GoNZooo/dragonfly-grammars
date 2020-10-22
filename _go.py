from dragonfly import (CompoundRule, MappingRule, Grammar, Function, Choice, Dictation, Text, Key)
from macro_utilities import (execute_with_dictation, replace_in_text)
from vim.rules.letter import (camel_case, proper)


class GoEnabler(CompoundRule):
    spec = "enable Go"

    def _process_recognition(self, node, extras):
        if go_bootstrap is not None:
            go_bootstrap.disable()
        go_grammar.enable()
        print("Go grammar enabled!")


class GoDisabler(CompoundRule):
    spec = "disable Go"

    def _process_recognition(self, node, extras):
        go_grammar.disable()
        go_bootstrap.enable()
        print("Go grammar disabled")


visibility_attribute_choice_map = {
    "public": "public",
    "private": "private",
}


def visibility_attribute_choice(name="visibility_attribute"):
    return Choice(name, visibility_attribute_choice_map)


def output_function(name, visibility_attribute=None, is_method=False):
    method_parameter_output = "_" if name == "" else "$"
    method_output = "(%s) " % method_parameter_output if is_method else ""
    parameter_output = "_" if name == "" or is_method else "$"

    execute_with_dictation(
        name,
        lambda n: replace_in_text(
            "func %s%s(%s) _ {" % (method_output, format_name(
                n, visibility_attribute), parameter_output)
        ),
        lambda n: replace_in_text("func %s$(_) _ {" % method_output)
    )


def output_type(name, construct, visibility_attribute=None):
    execute_with_dictation(
        name,
        lambda n: Text(
            "type %s %s {" % (format_name(n, visibility_attribute), construct)
        ),
        lambda n: replace_in_text("type $ %s {" % construct)
    )


comparison_choice_map = {
    "equal": "==",
    "not equal": "!=",
    "less or equal": "<=",
    "greater or equal": ">=",
    "less": "<",
    "greater": ">",
    "none": "== nil",
    "not none": "!= nil",
}


def comparison_choice(name="comparison"):
    return Choice(name, comparison_choice_map)


def output_if(name, statement_type):
    execute_with_dictation(
        name,
        on_dictation=lambda v: Text("%s %s {" % (statement_type, format_variable_name(name))),
        on_other=lambda v: replace_in_text("%s $ {" % statement_type),
    )


def output_if_comparison(name, construct, comparison=None):
    if comparison is not None:
        execute_with_dictation(
            name,
            on_dictation=lambda v: replace_in_text(
                "%s %s %s $ {" % (construct, format_variable_name(v), comparison)
            ),
            on_other=lambda v: replace_in_text("%s $ %s _ {" % (construct, comparison))
        )


def output_error_check(name):
    execute_with_dictation(
        name,
        lambda n: Text("if %s != nil {\n" % format_variable_name(n)),
        lambda n: Text("if err != nil {\n")
    )


type_name_choice_map = {
    "string": "string",
    "integer": "int",
    "boolean": "bool",
    "float": "float",
}


def type_name_choice(name="type_name"):
    return Choice(name, type_name_choice_map)


def output_make_slice(type_name=None):
    type_output = type_name if type_name is not None else "$"
    size_output = "$" if type_name is not None else "_"

    replace_in_text("make([]%s, %s)" % (type_output, size_output)).execute()


def format_variable_name(name):
    return camel_case(str(name).replace("-", ""))


def format_name(name, visibility_attribute):
    if visibility_attribute is None or visibility_attribute == "private":
        return camel_case(str(name).replace("-", ""))
    elif visibility_attribute == "public":
        return proper(str(name).replace("-", ""))


class GoUtilities(MappingRule):
    mapping = {
        "if [<name>] is <comparison>": Function(output_if_comparison, construct="if"),
        "if [<name>]": Function(output_if, statement_type="if"),

        "else if [<name>]": Function(output_if, statement_type="else if"),
        "else if [<name>] is <comparison>": Function(output_if_comparison, construct="else if"),

        "else": Text("else {") + Key("enter"),
        "error check [on <name>]": Function(output_error_check),

        "[<visibility_attribute>] function [<name>]": Function(output_function),
        "[<visibility_attribute>] method [<name>]": Function(output_function, is_method=True),
        "[<visibility_attribute>] struct [<name>]": Function(output_type, construct="struct"),
        "[<visibility_attribute>] interface [<name>]": Function(output_type, construct="interface"),

        "make [<type_name>] slice": Function(output_make_slice),
    }

    extras = [
        Dictation("name", default=""),
        visibility_attribute_choice("visibility_attribute"),
        type_name_choice("type_name"),
        comparison_choice("comparison"),
    ]


go_bootstrap = Grammar("go bootstrap")
go_bootstrap.add_rule(GoEnabler())
go_bootstrap.load()

go_grammar = Grammar("go grammar")
go_grammar.add_rule(GoUtilities())
go_grammar.add_rule(GoDisabler())
go_grammar.load()
go_grammar.disable()

# Unload function which will be called by natlink at unload time.


def unload():
    global go_grammar
    if go_grammar:
        go_grammar.unload()
    go_grammar = None