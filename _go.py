from dragonfly import (CompoundRule, MappingRule, Grammar, Function, Choice, Dictation, Text)
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


def output_function(name, visibility_attribute=None):
    execute_with_dictation(
        name,
        lambda n: replace_in_text("func %s($) _ {" % format_name(n, visibility_attribute)),
        lambda n: replace_in_text("func $(_) _ {")
    )


def output_type(name,  construct, visibility_attribute=None):
    execute_with_dictation(
        name,
        lambda n: Text(
            "type %s %s {" % (format_name(n, visibility_attribute), construct)
        ),
        lambda n: replace_in_text("type $ %s {" % construct)
    )


def format_name(name, visibility_attribute):
    if visibility_attribute is None or visibility_attribute == "private":
        return camel_case(str(name).replace("-", ""))
    elif visibility_attribute == "public":
        return proper(str(name).replace("-", ""))


class GoUtilities(MappingRule):
    mapping = {
        "[<visibility_attribute>] function [<name>]": Function(output_function),
        "[<visibility_attribute>] struct [<name>]": Function(output_type, construct="struct"),
        "[<visibility_attribute>] interface [<name>]": Function(output_type, construct="interface"),
    }

    extras = [
        Dictation("name", default=""),
        visibility_attribute_choice("visibility_attribute"),
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
