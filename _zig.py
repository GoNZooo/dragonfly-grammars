from dragonfly import (Grammar, CompoundRule, Text, MappingRule)
from macro_utilities import (replace_in_text)


def insert_function():
    return replace_in_text("fn $(_) _ {}")


class ZigEnabler(CompoundRule):
    spec = "all your base are belong to us"

    def _process_recognition(self, node, extras):
        zigBootstrap.disable()
        zigGrammar.enable()
        print "Zig grammar enabled!"


class ZigDisabler(CompoundRule):
    spec = "take off every zig"

    def _process_recognition(self, node, extras):
        zigGrammar.disable()
        zigBootstrap.enable()
        print "Zig grammar disabled"


class ZigUtilities(MappingRule):
    mapping = {
        "if": replace_in_text("if ($) {} _"),
        "for loop": replace_in_text("for ($) |_| {}"),
        "while loop": replace_in_text("while ($) _ {}"),
        "switch": replace_in_text("switch ($) {}"),

        "const": replace_in_text("const $ = ;"),
        "variable": replace_in_text("var $ = ;"),
        "test": replace_in_text("test \"$\" {}"),
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

    extras = []


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
