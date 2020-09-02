from vim.rules.letter import (snake_case)
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


class ZigUtilities(MappingRule):
    mapping = {
        "if": replace_in_text("if ($) {} _"),
        "for loop": replace_in_text("for ($) |_| {}"),
        "while loop": replace_in_text("while ($) _ {}"),
        "switch": replace_in_text("switch ($) {}"),

        "constant [<value_name>]": Function(output_constant),
        "variable [<value_name>]": Function(output_variable),
        "test [<test_name>]": Function(output_test),
        "public": Text("pub "),
        "external": Text("extern "),
        "function": insert_function(),
        "public function": Text("pub ") + insert_function(),
        "external function": Text("extern ") + insert_function(),
        "a sink": Text("async "),
        "await": Text("await "),
        "try": Text("try "),
        "catch": Text("catch "),
        "defer": Text("defer "),
        "import": replace_in_text("const $ = @import(\"_\");"),
        "compile time": Text("comptime "),

        "define struct": replace_in_text("const $ = struct {};"),
        "define union": replace_in_text("const $ = union(_) {};"),
        "define enumeration": replace_in_text("const $ = enum {};"),
        "struct": Text("struct {}"),
        "union": Text("union(_) {}"),
        "enumeration": Text("enum {}"),

        "check equal": Text(" == "),
        "check not equal": Text(" != "),
        "equals": Text(" = "),
        "arrow": Text(" => "),
        "pointer": Text("ptr"),
    }

    extras = [
        Dictation("test_name", default=""),
        Dictation("value_name", default="")
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
