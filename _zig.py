from dragonfly import (Grammar, CompoundRule, Text, MappingRule)
from macro_utilities import (replace_percentage)


def insert_function():
    return Text("fn %%(_) _ {}") + replace_percentage(25)


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
        "if": Text("if (%%) {} _") + replace_percentage(15),
        "for loop": Text("for (%%) |_| {}") + replace_percentage(15),
        "while loop": Text("while (%%) _ {}") + replace_percentage(15),
        "switch": Text("switch (%%) {}") + replace_percentage(15),

        "const": Text("const %% = ;") + replace_percentage(15),
        "variable": Text("var %% = ;") + replace_percentage(15),
        "test": Text("test \"%%\" {}") + replace_percentage(15),
        "public": Text("pub "),
        "function": insert_function(),
        "a sink": Text("async "),
        "await": Text("await "),
        "try": Text("try "),
        "catch": Text("catch "),
        "defer": Text("defer "),
        "import": Text("const %% = @import(\"_\");") + replace_percentage(15),
        "compile time": Text("comptime "),

        "define struct": Text("const %% = struct {};") + replace_percentage(15),
        "define union": Text("const %% = union(_) {};") + replace_percentage(15),
        "define enumeration": Text("const %% = enum {};") + replace_percentage(15),
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
