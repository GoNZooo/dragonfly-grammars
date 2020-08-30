from dragonfly import (Grammar, CompoundRule, Text, Key, MappingRule)
from macro_utilities import (replace_percentage)


class PythonEnabler(CompoundRule):
    spec = "enable Python"

    def _process_recognition(self, node, extras):
        pythonBootstrap.disable()
        pythonGrammar.enable()
        print "Python grammar enabled!"


class PythonDisabler(CompoundRule):
    spec = "disable Python"

    def _process_recognition(self, node, extras):
        pythonGrammar.disable()
        pythonBootstrap.enable()
        print "Python grammar disabled"


class PythonUtilities(MappingRule):
    mapping = {
        "statement else if": Text("elif %%:") + replace_percentage(25),
        "statement else": Text("else:") + Key("enter"),
        "statement if": Text("if %%:") + replace_percentage(25),
        "for loop": Text("for %% in _:") + replace_percentage(25),
        "anonymous function": Text("lambda %%: ") + replace_percentage(25),
        "function": Text("def %%(_):") + replace_percentage(25),
        "from import": Text("from %% import (_)") + replace_percentage(25),
        "generic qualified import": Text("import %% as _") + replace_percentage(25),
        "import dragonfly": Text("import dragonfly as dragonfly"),
        "check equal": Text(" == "),
        "check not equal": Text(" != "),
        "equals": Text(" = "),
    }

    extras = []


# The main Python grammar rules are activated here
pythonBootstrap = Grammar("python bootstrap")
pythonBootstrap.add_rule(PythonEnabler())
pythonBootstrap.load()

pythonGrammar = Grammar("python grammar")
pythonGrammar.add_rule(PythonUtilities())
pythonGrammar.add_rule(PythonDisabler())
pythonGrammar.load()
pythonGrammar.disable()

# Unload function which will be called by natlink at unload time.


def unload():
    global pythonGrammar
    if pythonGrammar:
        pythonGrammar.unload()
    pythonGrammar = None
