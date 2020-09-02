from vim.rules.letter import (snake_case, proper, camel_case)
from macro_utilities import (replace_in_text)
from dragonfly import (Grammar, CompoundRule, Text, MappingRule, Dictation, Function)


def insert_function():
    return replace_in_text("fn $(_) _ {}")


class ZigEnabler(CompoundRule):
    spec = "enable zig"

    def _process_recognition(self, node, extras):
        zigBootstrap.disable()
        zigGrammar.enable()
        print "Zig grammar enabled!"


class ZigDisabler(CompoundRule):
    spec = "disable zig"

    def _process_recognition(self, node, extras):
        zigGrammar.disable()
        zigBootstrap.enable()
        print "Zig grammar disabled"


def output_test(test_name):
    if test_name == "":
        command = replace_in_text("test \"$\" {}")
    else:
        command = Text("test \"%s\" {\n" % test_name)
    command.execute()


def output_constant(value_name):
    output_value("const", value_name)


def output_variable(value_name):
    output_value("var", value_name)


def output_value(value_type, value_name):
    if value_name == "":
        command = replace_in_text("%s $ = _;" % value_type)
    else:
        # `value_name` is a dictation object
        value_name = snake_case(str(value_name))
        command = replace_in_text("%s %s = $;" % (value_type, value_name))
    command.execute()


def output_struct(type_name):
    output_type("struct", type_name)


def output_union(type_name):
    output_type("union(enum)", type_name)


def output_enumeration(type_name):
    output_type("enum", type_name)


def output_type(prelude, type_name):
    if type_name == "":
        command = Text("%s {}" % prelude)
    else:
        type_name = proper(str(type_name))
        command = replace_in_text("const %s = %s {$};" % (type_name, prelude))
    command.execute()


def output_for_loop(value_name):
    if value_name == "":
        command = replace_in_text("for ($) |_| {}")
    else:
        value_name = snake_case(str(value_name))
        command = replace_in_text("for (%s) |$| {}" % value_name)
    command.execute()


def output_while_loop(value_name):
    if value_name == "":
        command = replace_in_text("while ($) _ {}")
    else:
        value_name = snake_case(str(value_name))
        command = replace_in_text("while (%s.next()) |$| {}" % value_name)
    command.execute()


def output_if(value_name):
    if value_name == "":
        command = replace_in_text("if ($) {} _")
    else:
        value_name = snake_case(str(value_name))
        command = replace_in_text("if (%s) $ {} _" % value_name)
    command.execute()


def output_switch(value_name):
    if value_name == "":
        command = replace_in_text("switch ($) {}")
    else:
        value_name = snake_case(str(value_name))
        command = replace_in_text("switch (%s) {$}" % value_name)
    command.execute()


def output_function(function_name):
    if function_name == "":
        command = replace_in_text("fn $(_) _ {}")
    else:
        function_name = camel_case(str(function_name))
        command = replace_in_text("fn %s($) _ {}" % function_name)
    command.execute()


class ZigUtilities(MappingRule):
    mapping = {
        "if [<value_name>]": Function(output_if),
        "for loop [over <value_name>]": Function(output_for_loop),
        "while loop [over <value_name>]": Function(output_while_loop),
        "switch [on <value_name>]": Function(output_switch),

        "constant [<value_name>]": Function(output_constant),
        "variable [<value_name>]": Function(output_variable),
        "test [<test_name>]": Function(output_test),
        "public": Text("pub "),
        "external": Text("extern "),
        "function [<function_name>]": Function(output_function),
        "a sink": Text("async "),
        "await": Text("await "),
        "try": Text("try "),
        "catch": Text("catch "),
        "defer": Text("defer "),
        "import": replace_in_text("const $ = @import(\"_\");"),
        "compile time": Text("comptime "),

        "struct [<type_name>]": Function(output_struct),
        "union [<type_name>]": Function(output_union),
        "enumeration [<type_name>]": Function(output_enumeration),

        "check equal": Text(" == "),
        "check not equal": Text(" != "),
        "equals": Text(" = "),
        "arrow": Text(" => "),
        "pointer": Text("ptr"),
    }

    extras = [
        Dictation("test_name", default=""),
        Dictation("value_name", default=""),
        Dictation("type_name", default=""),
        Dictation("function_name", default="")
    ]


# The main Zig grammar rules are activated here
zigBootstrap = Grammar("zig bootstrap")
zigBootstrap.add_rule(ZigEnabler())
zigBootstrap.load()

zigGrammar = Grammar("zig grammar")
zigGrammar.add_rule(ZigUtilities())
zigGrammar.add_rule(ZigDisabler())
zigGrammar.load()
zigGrammar.disable()

# Unload function which will be called by natlink at unload time.


def unload():
    global zigGrammar
    if zigGrammar:
        zigGrammar.unload()
    zigGrammar = None
